from django.db import models
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from .models import Product, Characteristic, CharacteristicValue, HeroImage, GalleryImage, Order, Page, Favorite, ProductType, ProductCharacteristic
from .serializers import ProductSerializer, CharacteristicSerializer, HeroImageSerializer, GalleryImageSerializer, OrderSerializer, PageSerializer, FavoriteSerializer, ProductTypeSerializer
from .cache import get_product, get_favorites, add_favorite, remove_favorite, get_favorites_cache_key
import logging
from django.db import connection
from django.db.models import F, Case, When, Value, IntegerField, Count
from django.db.models import Subquery, OuterRef, Prefetch, Q
from .models import NewsletterSubscriber
from .serializers import NewsletterSubscriberSerializer
import json
from decimal import Decimal
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from .utils import send_order_notification 



logger = logging.getLogger('products')
activity_logger = logging.getLogger('user_activity')


class ProductPagination(PageNumberPagination):
    """Кастомная пагинация"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class ProductTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ProductType.objects.all().order_by('name')
    serializer_class = ProductTypeSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    @action(detail=True, methods=['GET'])
    def by_slug(self, request, slug=None):
        try:
            product_type = self.get_object()
            serializer = self.get_serializer(product_type)
            return Response(serializer.data)
        except ProductType.DoesNotExist:
            return Response({"error": "Product type not found"}, status=status.HTTP_404_NOT_FOUND)
    
class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    pagination_class = ProductPagination
    
    def get_queryset(self):
        """
        Оптимизированный queryset с prefetch_related
        для избежания N+1 проблемы
        """
        queryset = Product.objects.select_related('product_type').prefetch_related(
            Prefetch(
                'product_characteristics',
                queryset=ProductCharacteristic.objects.filter(
                    characteristic__isnull=False
                ).select_related('characteristic', 'characteristic_value')
            ),
            'images'
        )
        
        return queryset
    
    def list(self, request):
        """Список продуктов с кэшированием"""
        try:
            # Создаем ключ кэша на основе параметров запроса
            cache_key = self._generate_cache_key(request)
            
            # Проверяем кэш
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.info(f"Cache hit for key: {cache_key}")
                return Response(cached_response)
            
            # Если нет в кэше, выполняем запрос
            queryset = self.filter_queryset(self.get_queryset())
            
            # Применяем фильтры
            queryset = self._apply_filters(queryset, request)
            
            # Пагинация
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                paginated_response = self.get_paginated_response(serializer.data)
                
                # Кэшируем результат на 5 минут
                cache.set(cache_key, paginated_response.data, timeout=300)
                
                # Логируем просмотр
                self._log_product_view(request, queryset.count())
                
                return paginated_response
            
            serializer = self.get_serializer(queryset, many=True)
            response_data = serializer.data
            
            # Кэшируем
            cache.set(cache_key, response_data, timeout=300)
            
            return Response(response_data)
            
        except Exception as e:
            logger.error(f"Error in ProductViewSet.list: {e}", exc_info=True)
            return Response(
                {"error": "Ошибка при получении списка продуктов"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_cache_key(self, request):
        """Генерирует ключ кэша на основе параметров запроса"""
        params = sorted(request.query_params.items())
        params_str = '&'.join([f'{k}={v}' for k, v in params])
        return f"products_list:{params_str}"
    
    def _apply_filters(self, queryset, request):
        """Применяет фильтры к queryset"""
        # Фильтр по типу продукта
        product_type = request.query_params.get('product_type')
        if product_type:
            try:
                product_type_obj = ProductType.objects.get(slug=product_type)
                queryset = queryset.filter(product_type=product_type_obj)
            except ProductType.DoesNotExist:
                return Product.objects.none()
        
        # Фильтр по избранному
        is_favorite = request.query_params.get('is_favorite')
        if is_favorite:
            session_key = request.session.session_key
            favorite_products = Favorite.objects.filter(
                session_key=session_key
            ).values_list('product', flat=True)
            queryset = queryset.filter(id__in=favorite_products)
        
        # Фильтр по featured
        is_featured = request.query_params.get('is_featured')
        if is_featured is not None:
            is_featured_bool = is_featured.lower() == 'true'
            queryset = queryset.filter(is_featured=is_featured_bool)
        
        # Поиск
        search_query = request.query_params.get('title', '').strip()
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Сортировка
        sort_by = request.query_params.get('sortBy', 'title')
        if sort_by in ['price', '-price', 'title', '-title']:
            queryset = queryset.order_by(sort_by)
        
        # Фильтры по характеристикам
        for param, value in request.query_params.items():
            if param.startswith('characteristic_'):
                try:
                    characteristic_id = param.split('_')[1]
                    queryset = queryset.filter(
                        product_characteristics__characteristic_value__characteristic_id=characteristic_id,
                        product_characteristics__characteristic_value__value=value
                    )
                except Exception as e:
                    logger.error(f"Error filtering by characteristic {param}: {e}")
        
        return queryset.distinct()
    
    def _log_product_view(self, request, count):
        """Логирует просмотр списка продуктов"""
        try:
            activity_logger.info(
                'Product list viewed',
                extra={
                    'action_type': 'view_products',
                    'session_key': request.session.session_key,
                    'product_count': count,
                    'filters': dict(request.query_params),
                }
            )
        except Exception as e:
            logger.error(f"Error logging product view: {e}")
    

    
    @action(detail=False, methods=['GET'], url_path='by-custom-url/(?P<custom_url>[-\w]+)')
    def get_by_custom_url(self, request, custom_url=None):
        """Получение продукта по custom_url с логированием"""
        try:
            # Проверяем кэш
            cache_key = f"product_by_url:{custom_url}"
            cached_product = cache.get(cache_key)
            
            if cached_product:
                # Логируем просмотр
                self._log_product_detail_view(request, cached_product['id'])
                return Response(cached_product)
            
            product = Product.objects.select_related('product_type').prefetch_related(
                'product_characteristics__characteristic',
                'product_characteristics__characteristic_value',
                'images'
            ).get(custom_url=custom_url)
            
            serializer = self.get_serializer(product)
            product_data = serializer.data
            
            # Кэшируем на 10 минут
            cache.set(cache_key, product_data, timeout=600)
            
            # Логируем просмотр
            self._log_product_detail_view(request, product.id)
            
            return Response(product_data)
            
        except Product.DoesNotExist:
            logger.warning(f"Product not found: {custom_url}")
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in get_by_custom_url: {e}", exc_info=True)
            return Response(
                {"error": "Внутренняя ошибка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _log_product_detail_view(self, request, product_id):
        """Логирует просмотр конкретного продукта"""
        try:
            activity_logger.info(
                f'Product {product_id} viewed',
                extra={
                    'action_type': 'view_product',
                    'session_key': request.session.session_key,
                    'product_id': product_id,
                }
            )
        except Exception as e:
            logger.error(f"Error logging product detail view: {e}")

class CharacteristicViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Characteristic.objects.all()
    serializer_class = CharacteristicSerializer
    permission_classes = [AllowAny]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        product_type_slug = self.request.query_params.get('product_type')

        qs = CharacteristicValue.objects.select_related('characteristic')

        if product_type_slug:
            qs = qs.filter(
                productcharacteristic__product__product_type__slug=product_type_slug
            )
            qs = qs.annotate(
                product_count=Count(
                    'productcharacteristic__product',
                    filter=Q(productcharacteristic__product__product_type__slug=product_type_slug),
                    distinct=True
                )
            )
        else:
            qs = qs.annotate(
                product_count=Count('productcharacteristic__product', distinct=True)
            )

        qs = qs.distinct()
        context['characteristic_values'] = qs
        return context
    
    def get_queryset(self):
        product_type_slug = self.request.query_params.get('product_type')
        qs = Characteristic.objects.all()
        if product_type_slug:
            qs = qs.filter(
                values__productcharacteristic__product__product_type__slug=product_type_slug
            ).distinct()
        return qs

class HeroImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HeroImage.objects.all()
    serializer_class = HeroImageSerializer
    permission_classes = [AllowAny]

class GalleryImageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = GalleryImage.objects.all()
    serializer_class = GalleryImageSerializer
    permission_classes = [AllowAny]

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        return [IsAdminUser()]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.none()

    def perform_create(self, serializer):
        order = serializer.save()
        send_order_notification(order)


class PageViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Page.objects.all()
    serializer_class = PageSerializer
    permission_classes = [AllowAny]

class FavoriteViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    
    def list(self, request):
        """Список избранного с кэшированием"""
        try:
            if not request.session.session_key:
                request.session.save()
            
            session_key = request.session.session_key
            
            favorites = Favorite.objects.filter(
                session_key=session_key
            ).select_related('product__product_type').prefetch_related(
                'product__product_characteristics'
            )
            
            from .serializers import FavoriteSerializer
            serializer = FavoriteSerializer(favorites, many=True)
            
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error in FavoriteViewSet.list: {e}", exc_info=True)
            return Response([], status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST', 'DELETE'], url_path='toggle/(?P<pk>[^/.]+)')
    def toggle(self, request, pk=None):
        """Переключение избранного с логированием"""
        try:
            if not request.session.session_key:
                request.session.save()
            
            session_key = request.session.session_key
            
            product = Product.objects.get(pk=pk)
            
            if request.method == 'POST':
                favorite, created = Favorite.objects.get_or_create(
                    product=product,
                    session_key=session_key
                )
                action = 'added' if created else 'already_exists'
            else:  # DELETE
                deleted_count, _ = Favorite.objects.filter(
                    product=product,
                    session_key=session_key
                ).delete()
                action = 'removed' if deleted_count > 0 else 'not_found'
            
            # Логируем действие
            activity_logger.info(
                f'Favorite toggled: {action}',
                extra={
                    'action_type': 'toggle_favorite',
                    'session_key': session_key,
                    'product_id': pk,
                    'action': action,
                }
            )
            
            # Возвращаем обновленный список
            favorites = Favorite.objects.filter(session_key=session_key)
            from .serializers import FavoriteSerializer
            serializer = FavoriteSerializer(favorites, many=True)
            
            
            return Response(serializer.data)
            
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Error in toggle favorite: {e}", exc_info=True)
            return Response(
                {"error": "Внутренняя ошибка сервера"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe_newsletter(request):
    try:
        serializer = NewsletterSubscriberSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            if NewsletterSubscriber.objects.filter(email=email).exists():
                return Response({"message": "Вы уже подписаны!"}, status=status.HTTP_200_OK)
            serializer.save()
            return Response({"message": "Вы успешно подписались!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Ошибка подписки на рассылку: {e}", exc_info=True)
        return Response({"error": "Внутренняя ошибка сервера"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def receive_analytics_events(request):
    """
    Принимает события аналитики с фронтенда и сохраняет их в БД
    Не требует API ключ - использует сессии Django для идентификации
    """
    from .models import UserActivityLog
    from .utils import get_client_ip, get_location_from_ip, categorize_analytics_event
    
    try:
        if not request.session.session_key:
            request.session.save()
        
        events = request.data.get('events', [])
        if not events:
            return Response({"error": "No events provided"}, status=status.HTTP_400_BAD_REQUEST)
        if len(events) > 50:
            return Response({"error": "Too many events"}, status=status.HTTP_400_BAD_REQUEST)
        
        ip_address = get_client_ip(request)
        location = get_location_from_ip(ip_address)
        session_key = request.session.session_key
        
        saved_count = 0
        errors = []
        
        for event in events:
            try:
                # Категоризируем событие
                action_type, extra_data = categorize_analytics_event(event)
                
                # Создаем лог
                log_entry = UserActivityLog.objects.create(
                    session_key=session_key,
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    action_type=action_type,
                    path=event.get('url', request.path),
                    method='POST',
                    country=location.get('country', '') if location else '',
                    city=location.get('city', '') if location else '',
                    region=location.get('region', '') if location else '',
                    extra_data={
                        **extra_data,
                        'event_name': event.get('event_name'),
                        'properties': event.get('properties', {}),
                        'session_id': event.get('session_id'),
                    }
                )
                saved_count += 1
            except Exception as e:
                logger.error(f"Error saving analytics event: {e}")
                errors.append(str(e))
        
        return Response({
            "message": f"Saved {saved_count} events",
            "saved": saved_count,
            "errors": errors if errors else None
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in receive_analytics_events: {e}", exc_info=True)
        return Response(
            {"error": "Internal server error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@staff_member_required
def get_characteristic_values(request):
    """API для получения значений характеристик"""
    characteristic_id = request.GET.get('characteristic_id')
    if not characteristic_id:
        return JsonResponse([], safe=False)
    
    values = CharacteristicValue.objects.filter(characteristic_id=characteristic_id).values('id', 'value')
    return JsonResponse(list(values), safe=False)



@api_view(['POST'])
@permission_classes([AllowAny])
def submit_quiz(request):
    from .models import QuizLead
    from .serializers import QuizLeadSerializer
    from .utils import send_quiz_notification  # или from .email_utils import ...

    serializer = QuizLeadSerializer(data=request.data)
    if serializer.is_valid():
        lead = serializer.save()
        send_quiz_notification(lead)
        return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)

    logger.error(f"Quiz submit validation error: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)