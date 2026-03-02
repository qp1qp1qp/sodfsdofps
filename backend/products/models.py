from django.db import models
from django.conf import settings
import os
from django.utils.html import format_html
import json
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError

from django.utils import timezone
import re
import logging

logger = logging.getLogger(__name__)

def product_image_path(instance, filename):
    return os.path.join('public', 'products', filename)

def get_default_product_image():
    # Возвращаем путь к изображению по умолчанию
    return 'product_images/1569685356.jpg'

def hero_image_path(instance, filename):
    return os.path.join('public', 'hero', filename)

def gallery_image_path(instance, filename):
    return os.path.join('public', 'gallery', filename)

class Characteristic(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

class CharacteristicValue(models.Model):
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE, related_name='values')
    value = models.CharField(max_length=100)
    
    def clean(self):
        """Очистка значения характеристики"""
        if self.value:
            self.value = self.value.strip()
        else:
            self.value = "Не указано"
    
    def save(self, *args, **kwargs):
        try:
            self.clean()
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при сохранении CharacteristicValue: {e}")
            if not self.value:
                self.value = "Не указано"
            super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.characteristic.name}: {self.value}"

class ProductType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    # Варианты единиц измерения
    UNIT_CHOICES = [
        ('piece', 'Штука'),
        ('cubic', 'Кубический метр'),
        ('square', 'Квадратный метр'),
        ('linear', 'Погонный метр'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Основная единица измерения товара
    primary_unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='piece', verbose_name="Единица измерения")
    
    # Базовая цена (цена за выбранную единицу измерения)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за единицу измерения")
    
    # Рассчитанные цены для разных единиц измерения
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена за штуку")
    price_per_cubic_meter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена за м³")
    price_per_square_meter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена за м²")
    price_per_linear_meter = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Цена за погонный метр")
    
    # Размеры
    length = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text='Длина в метрах', verbose_name="Длина (м)")
    width = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text='Ширина в метрах', verbose_name="Ширина (м)")
    thickness = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True, help_text='Толщина в метрах', verbose_name="Толщина (м)")
    
    # Количество единиц измерения в одной штуке (рассчитывается)
    volume_per_unit = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Объем в 1 шт. (м³)")
    area_per_unit = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, verbose_name="Площадь в 1 шт. (м²)")
    linear_meters_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Длина в 1 шт. (п.м)")
    
    pieces_per_package = models.IntegerField(default=1, verbose_name="Штук в пачке", help_text="Количество штук в одной пачке")
    

    quantity = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    imageUrl = models.ImageField(upload_to=product_image_path, default=get_default_product_image)
    product_type = models.ForeignKey(ProductType, on_delete=models.SET_NULL, null=True, related_name='products')
    characteristics = models.ManyToManyField(Characteristic, through='ProductCharacteristic')
    is_featured = models.BooleanField(default=False)
    custom_url = models.SlugField(unique=True, max_length=200, null=True, blank=True)
    
    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Переопределенный метод сохранения с валидацией"""
        try:
            self.clean()
            self.calculate_measurements_and_prices()
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при сохранении Product: {e}")
            # Установим безопасные значения и попробуем сохранить
            if not self.price_per_unit:
                self.price_per_unit = self.price or Decimal('0')
            super().save(*args, **kwargs)
    
    def clean(self):
        """Очистка и проверка данных перед сохранением"""
        # Очистка текстовых полей
        if self.title:
            self.title = self.title.strip()
        if self.description:
            self.description = self.description.strip()
        
        # Безопасное преобразование числовых значений для размеров
        self.length = self._safe_convert_decimal(self.length)
        self.width = self._safe_convert_decimal(self.width)
        self.thickness = self._safe_convert_decimal(self.thickness)
        
        # Безопасное преобразование ценовых значений
        self.price = self._safe_convert_decimal(self.price, default=Decimal('0'))
        self.price_per_unit = self._safe_convert_decimal(self.price_per_unit, default=Decimal('0'))
        self.price_per_cubic_meter = self._safe_convert_decimal(self.price_per_cubic_meter)
        self.price_per_square_meter = self._safe_convert_decimal(self.price_per_square_meter)
        self.price_per_linear_meter = self._safe_convert_decimal(self.price_per_linear_meter)
        
    def _safe_convert_decimal(self, value, default=None):
        """Безопасно преобразует значение в Decimal"""
        if value is None:
            return default
        
        try:
            # Если строка, очищаем и преобразуем
            if isinstance(value, str):
                # Удаляем все символы, кроме цифр, точек и запятых
                value = re.sub(r'[^\d.,]', '', value)
                # Заменяем запятые на точки
                value = value.replace(',', '.')
                # Если после очистки строка пустая, возвращаем default
                if not value:
                    return default
            
            return Decimal(str(value))
        except (ValueError, InvalidOperation, TypeError) as e:
            logger.warning(f"Ошибка преобразования в Decimal: {e}, value={value}")
            return default

    def calculate_measurements_and_prices(self):
        """Рассчитать объемы в разных единицах измерения и соответствующие цены"""
        try:
            # Сбрасываем значения
            self.volume_per_unit = None
            self.area_per_unit = None
            self.linear_meters_per_unit = None
            
            # Максимально допустимое значение для decimal(10,2)
            MAX_DECIMAL_VALUE = Decimal('99999999.99')
            
            # Минимальное безопасное значение для деления
            min_safe_value = Decimal('0.0001')
            
            # Если не указаны необходимые размеры, прерываем расчет
            if not self.length:
                return
            
            # Расчет объема
            if self.length and self.width and self.thickness:
                self.volume_per_unit = self.length * self.width * self.thickness
            
            # Расчет площади
            if self.length and self.width:
                self.area_per_unit = self.length * self.width
            
            # Погонные метры
            if self.length:
                self.linear_meters_per_unit = self.length

            pieces_per_package = max(1, self.pieces_per_package or 1)

            # Расчет цен в зависимости от единицы измерения
            if self.primary_unit == 'piece':
                self.price_per_unit = self.price
                
                # Расчет цен для других единиц
                if self.volume_per_unit and self.volume_per_unit > min_safe_value:
                    try:
                        price_per_cubic = self.price / self.volume_per_unit
                        self.price_per_cubic_meter = min(price_per_cubic, MAX_DECIMAL_VALUE)
                    except (ZeroDivisionError, InvalidOperation):
                        self.price_per_cubic_meter = None
                
                if self.area_per_unit and self.area_per_unit > min_safe_value:
                    try:
                        price_per_square = self.price / self.area_per_unit
                        self.price_per_square_meter = min(price_per_square, MAX_DECIMAL_VALUE)
                    except (ZeroDivisionError, InvalidOperation):
                        self.price_per_square_meter = None
                
                if self.linear_meters_per_unit and self.linear_meters_per_unit > min_safe_value:
                    try:
                        price_per_linear = self.price / self.linear_meters_per_unit
                        self.price_per_linear_meter = min(price_per_linear, MAX_DECIMAL_VALUE)
                    except (ZeroDivisionError, InvalidOperation):
                        self.price_per_linear_meter = None
            
            # Аналогично для других единиц измерения с защитой от ошибок
            elif self.primary_unit == 'cubic':
                self.price_per_cubic_meter = self.price
                
                if self.volume_per_unit:
                    try:
                        price_per_unit = self.price * self.volume_per_unit
                        self.price_per_unit = min(price_per_unit, MAX_DECIMAL_VALUE)
                    except (InvalidOperation, TypeError):
                        self.price_per_unit = self.price
                
                if self.area_per_unit and self.area_per_unit > min_safe_value:
                    try:
                        price_per_square = self.price_per_unit / self.area_per_unit
                        self.price_per_square_meter = min(price_per_square, MAX_DECIMAL_VALUE)
                    except (ZeroDivisionError, InvalidOperation):
                        self.price_per_square_meter = None

                if self.linear_meters_per_unit and self.linear_meters_per_unit > min_safe_value:
                    try:
                        price_per_linear = self.price_per_unit / self.linear_meters_per_unit
                        self.price_per_linear_meter = min(price_per_linear, MAX_DECIMAL_VALUE)
                    except (ZeroDivisionError, InvalidOperation):
                        self.price_per_linear_meter = None

            elif self.primary_unit == 'linear':
                self.price_per_linear_meter = self.price

                if self.linear_meters_per_unit and self.linear_meters_per_unit > min_safe_value:
                    try:
                        price_per_unit = self.price * self.linear_meters_per_unit
                        self.price_per_unit = min(price_per_unit, MAX_DECIMAL_VALUE)
                    except (InvalidOperation, TypeError):
                        self.price_per_unit = self.price

                if self.volume_per_unit and self.volume_per_unit > min_safe_value:
                    try:
                        price_per_cubic = self.price_per_unit / self.volume_per_unit
                        self.price_per_cubic_meter = min(price_per_cubic, MAX_DECIMAL_VALUE)
                    except (ZeroDivisionError, InvalidOperation):
                        self.price_per_cubic_meter = None

            elif self.primary_unit == 'square':
                self.price_per_square_meter = self.price
                
                if self.area_per_unit and self.area_per_unit > min_safe_value:
                    try:
                        # Рассчитываем базовую цену за штуку
                        base_price_per_unit = self.price * self.area_per_unit
                        
                        # Если указано количество штук в пачке больше 1, умножаем цену на это количество
                        if pieces_per_package > 1:
                            self.price_per_unit = base_price_per_unit * pieces_per_package
                        else:
                            self.price_per_unit = base_price_per_unit
                    except (InvalidOperation, TypeError):
                        self.price_per_unit = self.price
                
        except Exception as e:
            logger.error(f"Ошибка в calculate_measurements_and_prices: {e}")
            # Устанавливаем безопасные значения по умолчанию
            self.price_per_unit = self.price or Decimal('0')
    
    def get_unit_value(self):
        """Получить количество единиц измерения в одной штуке товара"""
        if self.primary_unit == 'cubic' and self.volume_per_unit:
            return self.volume_per_unit
        elif self.primary_unit == 'square' and self.area_per_unit:
            return self.area_per_unit
        elif self.primary_unit == 'linear' and self.linear_meters_per_unit:
            return self.linear_meters_per_unit
        return None
    
    def get_unit_label(self):
        """Получить метку для единицы измерения"""
        if self.primary_unit == 'cubic':
            return 'м³'
        elif self.primary_unit == 'square':
            return 'м²'
        elif self.primary_unit == 'linear':
            return 'п.м'
        return 'шт.'

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=product_image_path)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

class ProductCharacteristic(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_characteristics')
    characteristic = models.ForeignKey(Characteristic, on_delete=models.CASCADE)
    characteristic_value = models.ForeignKey(CharacteristicValue, on_delete=models.CASCADE, null=True, blank=True)

    def clean(self):
        """Валидация данных перед сохранением"""
        super().clean()
        
        if self.characteristic and not self.characteristic_value:
            raise ValidationError({
                'characteristic_value': 'Необходимо указать значение для характеристики'
            })
        
    def save(self, *args, **kwargs):
        """Сохранение с дополнительной проверкой"""
        try:
            # Проверяем обязательные поля
            if not self.characteristic or not self.characteristic_value:
                logger.warning(f"Попытка сохранения неполной характеристики: {self}")
                return  # Не сохраняем неполные характеристики
            
            super().save(*args, **kwargs)
        except Exception as e:
            logger.error(f"Ошибка при сохранении характеристики: {e}")
            # Не пробрасываем исключение дальше, чтобы не нарушить работу админки
    
    def __str__(self):
        try:
            char_name = self.characteristic.name if self.characteristic else 'Нет характеристики'
            char_value = self.characteristic_value.value if self.characteristic_value else 'Не указано'
            product_title = self.product.title if self.product else 'Нет продукта'
            return f"{product_title} - {char_name}: {char_value}"
        except Exception as e:
            logger.error(f"Ошибка в __str__ ProductCharacteristic: {e}")
            return "Ошибка отображения характеристики"

class HeroImage(models.Model):
    image = models.ImageField(upload_to=hero_image_path)
    title = models.CharField(max_length=200)
    link = models.CharField(max_length=200)

class GalleryImage(models.Model):
    image = models.ImageField(upload_to=gallery_image_path)

class Order(models.Model):
    CUSTOMER_TYPE_CHOICES = [
        ('individual', 'Физическое лицо'),
        ('legal', 'Юридическое лицо'),
    ]
    
    customer_type = models.CharField(
        max_length=20, 
        choices=CUSTOMER_TYPE_CHOICES, 
        null=True,  # Разрешаем null значения
        blank=True  # Разрешаем пустые значения в формах
    )
    first_name = models.CharField(max_length=100, null=True, blank=True )
    last_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20,  null=True, blank=True)
    email = models.EmailField(blank=True)
    comment = models.TextField(blank=True)
    delivery_method = models.CharField(max_length=100, null=True, blank=True )
    #items = models.TextField(default='[]')  # Изменим на TextField
    order_number = models.CharField(max_length=8, unique=True, null=True, blank=True, verbose_name="Номер заказа")
    total_price = models.DecimalField(max_digits=10, decimal_places=2,  null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, default='Новый')

    def formatted_items(self):
        """Отображение товаров заказа в админке"""
        try:
            items = self.order_items.all()
            if not items:
                return "Нет товаров"
            
            return format_html('<br>'.join([
                f"Товар: {item.title}, Количество: {item.quantity}, Цена: {item.price}"
                for item in items
            ]))
        except Exception as e:
            logger.error(f"Ошибка в formatted_items: {e}")
            return "Ошибка отображения товаров"
    formatted_items.short_description = "Товары"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Заказ {self.id} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product_id = models.IntegerField()
    title = models.CharField(max_length=255)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.title} - {self.quantity} шт."

class Page(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.JSONField()

class Favorite(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('product', 'session_key')

    def __str__(self):
        return f"{self.product.title} - {self.session_key}"
    
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class UserActivityLog(models.Model):
    """Логи активности пользователей"""
    
    ACTION_TYPES = [
        ('view_product', 'Просмотр товара'),
        ('add_to_cart', 'Добавление в корзину'),
        ('remove_from_cart', 'Удаление из корзины'),
        ('toggle_favorite', 'Изменение избранного'),
        ('create_order', 'Создание заказа'),
        ('view_products', 'Просмотр списка товаров'),
        ('newsletter_subscribe', 'Подписка на рассылку'),
        ('search', 'Поиск'),
        ('click', 'Клик по элементу'),
        ('page_view', 'Просмотр страницы'),
        ('time_on_page', 'Время на странице'),
    ]
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    session_key = models.CharField(max_length=40, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES, db_index=True)
    path = models.CharField(max_length=500)
    method = models.CharField(max_length=10)
    
    # Геолокация
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    
    # Дополнительные данные в JSON
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Производительность
    duration = models.FloatField(null=True, blank=True, help_text="Время выполнения в секундах")
    status_code = models.IntegerField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'action_type']),
            models.Index(fields=['session_key', '-timestamp']),
            models.Index(fields=['ip_address', '-timestamp']),
        ]
        verbose_name = 'Лог активности'
        verbose_name_plural = 'Логи активности'
    
    def __str__(self):
        return f"{self.action_type} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"


class ErrorLog(models.Model):
    """Логи ошибок"""
    
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    level = models.CharField(max_length=20, db_index=True)
    message = models.TextField()
    
    path = models.CharField(max_length=500, blank=True)
    method = models.CharField(max_length=10, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Traceback и дополнительные данные
    traceback = models.TextField(blank=True)
    extra_data = models.JSONField(default=dict, blank=True)
    
    # Флаг для отслеживания обработанных ошибок
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=100, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp', 'level']),
            models.Index(fields=['is_resolved', '-timestamp']),
        ]
        verbose_name = 'Лог ошибок'
        verbose_name_plural = 'Логи ошибок'
    
    def __str__(self):
        return f"{self.level} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

@receiver([post_save, post_delete], sender=Product)
def invalidate_product_cache(sender, **kwargs):
    cache.delete_many(cache.keys('products_list:*') if hasattr(cache, 'keys') else [])
    # Для LocMemCache используем паттерн
    try:
        cache.delete_pattern('products_list:*')
    except AttributeError:
        # LocMemCache не поддерживает паттерны — очищаем весь кэш
        cache.clear()


class QuizLead(models.Model):
    created_at    = models.DateTimeField(auto_now_add=True, db_index=True)
    name          = models.CharField(max_length=150, verbose_name='Имя')
    phone         = models.CharField(max_length=30,  verbose_name='Телефон')
    email        = models.EmailField(blank=True,     verbose_name='Email')
    structure     = models.CharField(max_length=100, blank=True, verbose_name='Тип строения')
    material      = models.CharField(max_length=100, blank=True, verbose_name='Материал')
    volume        = models.CharField(max_length=100, blank=True, verbose_name='Объём')
    timing        = models.CharField(max_length=100, blank=True, verbose_name='Сроки')
    recommended   = models.CharField(max_length=255, blank=True, verbose_name='Рекомендации')
    is_processed  = models.BooleanField(default=False, verbose_name='Обработан')
    manager_note  = models.TextField(blank=True, verbose_name='Заметка менеджера')

    class Meta:
        verbose_name        = 'Заявка с квиза'
        verbose_name_plural = 'Заявки с квиза'
        ordering            = ['-created_at']

    def __str__(self):
        return f"{self.name} | {self.phone} | {self.created_at:%d.%m.%Y %H:%M}"
