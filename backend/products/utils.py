"""
Утилиты для логирования и аналитики
"""
import logging
import traceback
from .models import UserActivityLog, ErrorLog
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Получает реальный IP клиента"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location_from_ip(ip):
    """
    Получает геолокацию по IP адресу
    
    Примечание: База данных GeoIP2 не установлена. Функция всегда возвращает None.
    Это не критично для работы системы логирования - поля country, city, region будут пустыми.
    """
    if not ip:
        return None
    
    # Пропускаем локальные адреса
    if ip in ['127.0.0.1', 'localhost', '::1']:
        return None
    
    # База GeoIP2 не установлена, возвращаем None
    # Это нормально - система логирования работает без геолокации
    return None


def categorize_analytics_event(event):
    """
    Умная категоризация событий аналитики
    Преобразует события с фронтенда в action_type для UserActivityLog
    """
    event_name = event.get('event_name', '').lower()
    properties = event.get('properties', {})
    
    # Маппинг событий
    event_mapping = {
        'click': 'click',
        'page_view': 'view_products',
        'add_to_cart': 'add_to_cart',
        'toggle_favorite': 'toggle_favorite',
        'create_order': 'create_order',
        'search': 'search',
        'time_on_page': 'view_products',
    }
    
    action_type = event_mapping.get(event_name, 'view_products')
    
    # Формируем extra_data с умной категоризацией
    extra_data = {
        'original_event': event_name,
        'timestamp': event.get('timestamp'),
    }
    
    # Добавляем специфичные данные в зависимости от типа события
    if event_name == 'click':
        extra_data['element'] = properties.get('element')
        extra_data['click_data'] = properties
    elif event_name == 'add_to_cart':
        extra_data['product_id'] = properties.get('product_id')
        extra_data['product_title'] = properties.get('product_title')
        extra_data['quantity'] = properties.get('quantity')
        extra_data['price'] = properties.get('price')
    elif event_name == 'toggle_favorite':
        extra_data['product_id'] = properties.get('product_id')
        extra_data['product_title'] = properties.get('product_title')
        extra_data['action'] = properties.get('action')  # 'add' or 'remove'
    elif event_name == 'search':
        extra_data['query'] = properties.get('query')
        extra_data['results_count'] = properties.get('results_count')
    elif event_name == 'time_on_page':
        extra_data['page'] = properties.get('page')
        extra_data['duration_seconds'] = properties.get('duration_seconds')
    elif event_name == 'create_order':
        extra_data['order_number'] = properties.get('order_number')
        extra_data['total_price'] = properties.get('total_price')
        extra_data['items_count'] = properties.get('items_count')
    
    # Добавляем техническую информацию
    extra_data['screen_resolution'] = properties.get('screen_resolution')
    extra_data['viewport_size'] = properties.get('viewport_size')
    extra_data['referrer'] = properties.get('referrer')
    
    return action_type, extra_data


def log_user_activity(request, action_type, extra_data=None, duration=None, status_code=None):
    """
    Универсальная функция для логирования активности пользователя
    """
    try:
        if not request.session.session_key:
            request.session.save()
        
        ip_address = get_client_ip(request)
        location = get_location_from_ip(ip_address)
        
        UserActivityLog.objects.create(
            session_key=request.session.session_key,
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            action_type=action_type,
            path=request.path,
            method=request.method,
            country=location.get('country', '') if location else '',
            city=location.get('city', '') if location else '',
            region=location.get('region', '') if location else '',
            extra_data=extra_data or {},
            duration=duration,
            status_code=status_code or 200,
        )
    except Exception as e:
        logger.error(f"Error logging user activity: {e}", exc_info=True)


def log_error(request, level, message, traceback_text=None, extra_data=None):
    """
    Универсальная функция для логирования ошибок
    """
    try:
        ip_address = get_client_ip(request) if request else None
        
        ErrorLog.objects.create(
            level=level,
            message=message,
            path=request.path if request else '',
            method=request.method if request else '',
            ip_address=ip_address,
            user_agent=request.META.get('HTTP_USER_AGENT', '') if request else '',
            traceback=traceback_text or '',
            extra_data=extra_data or {},
        )
    except Exception as e:
        logger.error(f"Error logging error: {e}", exc_info=True)
