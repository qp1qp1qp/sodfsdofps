import logging
import json
import time
import traceback
from django.utils.deprecation import MiddlewareMixin
from .utils import log_user_activity, log_error, get_client_ip, get_location_from_ip
from .models import UserActivityLog

user_activity_logger = logging.getLogger('user_activity')
request_logger = logging.getLogger('django.request')


class UserActivityMiddleware(MiddlewareMixin):
    """
    Логирует действия пользователей:
    - Клики по продуктам
    - Добавления в корзину
    - Добавления в избранное
    - Просмотры страниц
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        # Логируем только определенные действия
        if request.method in ['POST', 'PUT', 'DELETE']:
            self._log_user_action(request, response)
        
        return response
    
    def _log_user_action(self, request, response):
        """Логирует действие пользователя в файл и БД"""
        try:
            duration = time.time() - request.start_time
            
            # Получаем IP адрес
            ip = get_client_ip(request)
            
            # Пытаемся получить геолокацию
            location = get_location_from_ip(ip)
            
            # Определяем тип действия
            action_type = self._determine_action_type(request)
            
            # Подготавливаем данные для логирования в файл
            log_data = {
                'timestamp': time.time(),
                'session_key': request.session.session_key,
                'ip_address': ip,
                'location': location,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'action_type': action_type,
                'path': request.path,
                'method': request.method,
                'status_code': response.status_code,
                'duration': f'{duration:.3f}s',
            }
            
            # Добавляем данные запроса для определенных действий
            extra_data = {}
            if action_type in ['add_to_cart', 'toggle_favorite', 'create_order']:
                extra_data['request_data'] = self._safe_get_request_data(request)
            
            # Логируем в файл
            user_activity_logger.info(
                f"User action: {action_type}",
                extra=log_data
            )
            
            # Сохраняем в БД
            log_user_activity(
                request=request,
                action_type=action_type,
                extra_data=extra_data,
                duration=duration,
                status_code=response.status_code
            )
            
        except Exception as e:
            # Не должны ломать приложение из-за логирования
            request_logger.error(f"Error in UserActivityMiddleware: {e}")
            # Логируем ошибку в БД
            try:
                log_error(
                    request=request,
                    level='ERROR',
                    message=f"Error in UserActivityMiddleware: {str(e)}",
                    traceback_text=traceback.format_exc()
                )
            except Exception:
                pass
    
    
    def _determine_action_type(self, request):
        """Определяет тип действия на основе пути"""
        path = request.path
        method = request.method
        
        if '/favorites/toggle/' in path:
            return 'toggle_favorite'
        elif '/orders/' in path and method == 'POST':
            return 'create_order'
        elif '/products/' in path:
            if method == 'GET':
                return 'view_products'
            elif method == 'POST':
                return 'add_to_cart'
        elif '/newsletter/subscribe/' in path:
            return 'newsletter_subscribe'
        
        return 'unknown'
    
    def _safe_get_request_data(self, request):
        """Безопасно извлекает данные запроса"""
        try:
            if request.content_type == 'application/json':
                return json.loads(request.body.decode('utf-8'))
            else:
                return dict(request.POST)
        except Exception:
            return {}


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Логирует все HTTP запросы для анализа трафика
    """
    
    def process_request(self, request):
        request.start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Логируем только медленные запросы или ошибки
            if duration > 1.0 or response.status_code >= 400:
                request_logger.warning(
                    f"{request.method} {request.path} - {response.status_code} - {duration:.3f}s",
                    extra={
                        'method': request.method,
                        'path': request.path,
                        'status_code': response.status_code,
                        'duration': duration,
                        'ip': get_client_ip(request),
                    }
                )
                
                # Логируем ошибки в БД
                if response.status_code >= 400:
                    try:
                        log_error(
                            request=request,
                            level='ERROR' if response.status_code >= 500 else 'WARNING',
                            message=f"{request.method} {request.path} - {response.status_code}",
                            extra_data={
                                'duration': duration,
                                'status_code': response.status_code,
                            }
                        )
                    except Exception:
                        pass
        
        return response