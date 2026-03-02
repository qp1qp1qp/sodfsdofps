"""
Утилиты для логирования и аналитики
"""
import logging
import traceback
from .models import UserActivityLog, ErrorLog
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def get_client_ip(request):
    trusted_proxies = getattr(settings, 'TRUSTED_PROXY_IPS', [])
    remote_addr = request.META.get('REMOTE_ADDR')
    
    if trusted_proxies and remote_addr in trusted_proxies:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
    
    return remote_addr


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


def send_order_notification(order):
    """Отправить уведомление о новом заказе на почту менеджера"""
    try:
        items_text = ''
        
        # Запрашиваем связанные товары из базы данных
        order_items = order.order_items.all()
        
        if order_items.exists():
            for item in order_items:
                # Обращаемся к полям через точку, так как это объекты модели
                title = getattr(item, 'title', '—')
                quantity = getattr(item, 'quantity', 1)
                price = getattr(item, 'price', 0)
                items_text += f"  • {title} × {quantity} шт. — {price} ₽\n"

        message = f"""
Новый заказ на сайте WoodDon!
═══════════════════════════════

📦 Номер заказа: {order.order_number or '—'}
👤 Клиент:     {order.first_name} {order.last_name or ''}
📞 Телефон:    {order.phone}
📧 Email:      {order.email or '—'}
🏢 Тип:        {'Юр. лицо' if order.customer_type == 'legal' else 'Физ. лицо'}

📋 Состав заказа:
{items_text or '  (данные о товарах загружаются...)'}

🚚 Доставка:   {order.delivery_method or '—'}
💬 Комментарий: {order.comment or '—'}

💰 Итого:      {order.total_price} ₽

───────────────────────────────
Посмотреть в админке: https://test.wooddon.ru/admin_new_wooddon_site_ru_test/products/order/{order.id}/
        """.strip()

        from django.core.mail import send_mail
        from django.conf import settings
        
        send_mail(
            subject=f'🛒 Новый заказ {order.order_number or f"#{order.id}"} — WoodDon',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFICATION_EMAIL],
            fail_silently=False,  # Оставим False для тестирования, чтобы сразу видеть ошибки
        )
        print(">>> ПИСЬМО О ЗАКАЗЕ УСПЕШНО ОТПРАВЛЕНО!")
        
    except Exception as e:
        import logging
        logging.getLogger('products').error(f'Order email notification error: {e}')
        print(f">>> ОШИБКА ОТПРАВКИ ПИСЬМА: {e}")


def send_quiz_notification(lead):
    """Отправить уведомление о новой заявке с квиза"""
    try:
        message = f"""
Новая заявка с квиза на WoodDon!
═══════════════════════════════

👤 Имя:        {lead.name}
📞 Телефон:    {lead.phone}
📧 Email:      {lead.email or '—'}

🔍 Ответы квиза:
  • Строение:   {lead.structure or '—'}
  • Материал:   {lead.material or '—'}
  • Объём:      {lead.volume or '—'}
  • Сроки:      {lead.timing or '—'}

💡 Рекомендовано: {lead.recommended or '—'}

───────────────────────────────
Посмотреть в админке: https://test.wooddon.ru/admin_new_wooddon_site_ru_test/products/quizlead/{lead.id}/
        """.strip()

        send_mail(
            subject=f'📋 Новая заявка с квиза — {lead.name}',
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFICATION_EMAIL],
            fail_silently=True,
        )
    except Exception as e:
        import logging
        logging.getLogger('products').error(f'Quiz email notification error: {e}')
