from django.contrib import admin
from .models import Characteristic, NewsletterSubscriber, CharacteristicValue, Product, ProductCharacteristic, HeroImage, GalleryImage, Order, Page, Favorite, ProductType, ProductImage, UserActivityLog, ErrorLog
from django import forms
from django.utils.html import format_html
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
import json
import logging


logger = logging.getLogger(__name__)

class CharacteristicValueInline(admin.TabularInline):
    model = CharacteristicValue
    extra = 1

@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    inlines = [CharacteristicValueInline]

class ProductCharacteristicInline(admin.TabularInline):
    model = ProductCharacteristic
    extra = 1
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Настройка полей для выбора значений характеристики"""
        if db_field.name == "characteristic_value":
            # Если форма редактируется и характеристика выбрана
            if hasattr(self, 'instance') and self.instance and self.instance.characteristic:
                kwargs["queryset"] = CharacteristicValue.objects.filter(characteristic=self.instance.characteristic)
            else:
                # Для новых форм показываем все значения характеристик
                kwargs["queryset"] = CharacteristicValue.objects.all()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductAdminForm(forms.ModelForm):
    """Форма для продукта с улучшенной логикой работы с единицами измерения и ценами"""
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Добавляем подсказки для полей
        self.fields['primary_unit'].help_text = 'Выберите основную единицу измерения для товара'
        self.fields['price'].help_text = 'Введите цену за выбранную единицу измерения'
        
        # Подсказки для размеров
        if 'length' in self.fields:
            self.fields['length'].help_text = 'Длина в метрах (обязательно для всех типов)'
        if 'width' in self.fields:
            self.fields['width'].help_text = 'Ширина в метрах (обязательно для м² и м³)'
        if 'thickness' in self.fields:
            self.fields['thickness'].help_text = 'Толщина в метрах (обязательно только для м³)'
        
        # Добавляем JavaScript для динамического изменения видимости полей размеров
        self.fields['primary_unit'].widget.attrs.update({
            'onchange': 'updateDimensionFields(this.value)'
        })
        
        # Добавляем подсказку для поля "штук в пачке"
        if 'pieces_per_package' in self.fields:
            self.fields['pieces_per_package'].help_text = 'Количество штук в одной пачке (используется при расчете цены для м²)'

    def clean(self):
        """Проверка данных формы"""
        cleaned_data = super().clean()
        
        # Переводим запятые в точки для числовых полей
        for field_name in ['price', 'length', 'width', 'thickness']:
            if field_name in cleaned_data and cleaned_data[field_name]:
                if isinstance(cleaned_data[field_name], str):
                    try:
                        cleaned_data[field_name] = Decimal(cleaned_data[field_name].replace(',', '.'))
                    except (InvalidOperation, ValueError):
                        # Устанавливаем None для некорректных значений
                        cleaned_data[field_name] = None
        
        return cleaned_data

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = ('title', 'custom_url', 'get_product_type', 'get_price_display', 'primary_unit', 'quantity', 'is_available')
    list_filter = ('product_type', 'primary_unit', 'is_available', 'is_featured')
    search_fields = ('title', 'description')
    prepopulated_fields = {'custom_url': ('title',)}
    readonly_fields = ('price_per_unit', 'price_per_cubic_meter', 'price_per_square_meter', 'price_per_linear_meter', 
                       'volume_per_unit', 'area_per_unit', 'linear_meters_per_unit', 'get_measurement_summary')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'custom_url', 'product_type', 'imageUrl', 'is_available', 'is_featured')
        }),
        ('Единица измерения и цена', {
            'fields': ('primary_unit', 'price', 'quantity', 'pieces_per_package'),
            'description': 'Укажите основную единицу измерения, цену за эту единицу и количество штук в пачке (для м²)',
        }),
        ('Размеры', {
            'fields': ('length', 'width', 'thickness'),
            'description': 'Укажите размеры товара в метрах',
        }),
        ('Расчетные данные', {
            'fields': ('get_measurement_summary', 'price_per_unit', 'volume_per_unit', 'area_per_unit', 'linear_meters_per_unit', 
                     'price_per_cubic_meter', 'price_per_square_meter', 'price_per_linear_meter'),
            'classes': ('collapse',),
            'description': 'Автоматически рассчитанные значения',
        }),
    )
    inlines = [ProductCharacteristicInline, ProductImageInline]

    def get_product_type(self, obj):
        return obj.product_type.name if obj.product_type else 'No Type'
    get_product_type.short_description = 'Тип товара'
    
    def get_price_display(self, obj):
        """Отображение цены с учетом единицы измерения"""
        unit_value = obj.get_unit_value()
        unit_label = obj.get_unit_label()
        
        if unit_value:
            return format_html(
                '{} ₽/шт.<br><span style="color:#888; font-size:0.9em;">{} {} в 1 шт.</span><br>'
                '<span style="font-size:0.9em;">{} ₽/{}</span>',
                obj.price_per_unit, unit_value, unit_label, obj.price, unit_label
            )
        else:
            return format_html('{} ₽/шт.', obj.price_per_unit)
    get_price_display.short_description = 'Цена'
    
    def get_measurement_summary(self, obj):
        """Показать сводку по размерам и единицам измерения"""
        if not obj.pk:
            return "Сохраните товар для расчета"
        
        unit_value = obj.get_unit_value()
        unit_label = obj.get_unit_label()
        
        if unit_value:
            summary = format_html(
                '<div style="font-size:1.1em; margin-bottom:10px;">Цена за штуку: <strong>{} ₽</strong></div>'
                '<div style="color:#444;">В 1 штуке: {} {}</div>'
                '<div style="color:#444;">Цена за {}: {} ₽</div>',
                obj.price_per_unit, unit_value, unit_label, unit_label, obj.price
            )
            
            # Добавляем информацию о пачке для товаров с единицей измерения м²
            if obj.primary_unit == 'square' and obj.pieces_per_package > 1:
                summary += format_html(
                    '<div style="color:#444; margin-top:5px;">В пачке: {} шт.</div>'
                    '<div style="color:#444;">Цена одной пачки: {} ₽</div>',
                    obj.pieces_per_package, obj.price_per_unit
                )
            
            return summary
        else:
            return "Недостаточно данных для расчета"
    get_measurement_summary.short_description = 'Сводка по ценам и размерам'
    
    def save_model(self, request, obj, form, change):
        """Сохраняем основную модель с обработкой ошибок"""
        try:
            obj.calculate_measurements_and_prices()
            super().save_model(request, obj, form, change)
        except Exception as e:
            messages.error(request, f"Ошибка при сохранении: {str(e)}")
    
    def save_formset(self, request, form, formset, change):
        """Безопасное сохранение формсетов"""
        try:
            if formset.model == ProductCharacteristic:
                # Правильно вызываем formset.save() с commit=False, чтобы создать необходимые атрибуты
                instances = formset.save(commit=False)
                
                # Проходимся по каждому экземпляру и проверяем его перед сохранением
                for instance in instances:
                    if instance.characteristic and instance.characteristic_value:
                        try:
                            instance.save()
                        except Exception as e:
                            messages.error(request, f"Ошибка при сохранении характеристики: {str(e)}")
                    else:
                        if instance.characteristic:
                            messages.warning(
                                request, 
                                f"Характеристика '{instance.characteristic}' не имеет значения и не будет сохранена."
                            )
                
                # Удаляем отмеченные для удаления
                for obj in formset.deleted_objects:
                    try:
                        obj.delete()
                    except Exception as e:
                        messages.error(request, f"Ошибка при удалении характеристики: {str(e)}")
                
                # Сохраняем m2m связи
                formset.save_m2m()
            else:
                # Для других формсетов используем стандартное сохранение
                formset.save()
        except Exception as e:
            messages.error(request, f"Общая ошибка при сохранении связанных данных: {str(e)}")
    
    class Media:
        js = ('admin/js/product_admin.js', 'admin/js/characteristic_filter.js')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_number', 'customer_type', 'first_name', 'last_name', 'phone', 'delivery_method', 'total_price', 'created_at', 'status')
    list_filter = ('customer_type', 'delivery_method', 'status', 'created_at')
    search_fields = ('first_name', 'last_name', 'phone', 'email', 'order_number')
    readonly_fields = ('total_price', 'created_at', 'order_number')

    def get_readonly_fields(self, request, obj=None):
        """Динамически определяем readonly_fields"""
        if obj:  # Это существующий объект
            return self.readonly_fields + ('formatted_items',)
        return self.readonly_fields  # Это новый объект
    
    def formatted_items(self, obj):
        """Показать товары заказа"""
        try:
            items = obj.order_items.all()
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

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('product', 'session_key', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('product__title', 'session_key')

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('email',)

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)


@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'action_type', 'session_key', 
        'ip_address', 'location_display', 'duration_display'
    ]
    list_filter = [
        'action_type', 'timestamp', 'country', 'city',
        ('timestamp', admin.DateFieldListFilter),
    ]
    search_fields = ['session_key', 'ip_address', 'path']
    readonly_fields = [
        'timestamp', 'session_key', 'ip_address', 'user_agent',
        'action_type', 'path', 'method', 'country', 'city', 
        'region', 'extra_data_display', 'duration', 'status_code'
    ]
    date_hierarchy = 'timestamp'
    
    def location_display(self, obj):
        """Отображение геолокации"""
        parts = [obj.city, obj.region, obj.country]
        location = ', '.join(filter(None, parts))
        return location or '-'
    location_display.short_description = 'Местоположение'
    
    def duration_display(self, obj):
        """Отображение времени выполнения с цветом"""
        if obj.duration is None:
            return '-'
        
        if obj.duration < 0.5:
            color = 'green'
        elif obj.duration < 2.0:
            color = 'orange'
        else:
            color = 'red'
        
        # Форматируем число до передачи в format_html
        duration_str = f'{obj.duration:.3f}s'
        return format_html('<span style="color: {};">{}</span>', color, duration_str)
    duration_display.short_description = 'Время выполнения'
    
    def extra_data_display(self, obj):
        """Красивое отображение JSON данных"""
        if not obj.extra_data:
            return '-'
        return format_html(
            '<pre style="max-height: 300px; overflow: auto;">{}</pre>',
            json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
        )
    extra_data_display.short_description = 'Дополнительные данные'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    # Добавляем статистику
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        
        # Статистика за последние 24 часа
        last_24h = timezone.now() - timedelta(hours=24)
        stats_24h = UserActivityLog.objects.filter(timestamp__gte=last_24h).aggregate(
            total=Count('id'),
            cart_actions=Count('id', filter=Q(action_type='add_to_cart')),
            favorites=Count('id', filter=Q(action_type='toggle_favorite')),
            orders=Count('id', filter=Q(action_type='create_order')),
            views=Count('id', filter=Q(action_type__in=['view_products', 'view_product', 'page_view'])),
            clicks=Count('id', filter=Q(action_type='click')),
            searches=Count('id', filter=Q(action_type='search')),
        )
        
        # Статистика за последние 7 дней
        last_7d = timezone.now() - timedelta(days=7)
        stats_7d = UserActivityLog.objects.filter(timestamp__gte=last_7d).aggregate(
            total=Count('id'),
            unique_sessions=Count('session_key', distinct=True),
            unique_ips=Count('ip_address', distinct=True),
        )
        
        # Топ стран
        top_countries = UserActivityLog.objects.filter(
            timestamp__gte=last_24h,
            country__isnull=False
        ).exclude(country='').values('country').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Топ страниц
        top_pages = UserActivityLog.objects.filter(
            timestamp__gte=last_24h
        ).values('path').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        extra_context['stats_24h'] = stats_24h
        extra_context['stats_7d'] = stats_7d
        extra_context['top_countries'] = list(top_countries)
        extra_context['top_pages'] = list(top_pages)
        
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp', 'level', 'message_short', 
        'path', 'ip_address', 'is_resolved'
    ]
    list_filter = [
        'level', 'is_resolved', 
        ('timestamp', admin.DateFieldListFilter),
    ]
    search_fields = ['message', 'path', 'ip_address']
    readonly_fields = [
        'timestamp', 'level', 'message', 'path', 'method',
        'ip_address', 'user_agent', 'traceback_display', 'extra_data_display'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('timestamp', 'level', 'message', 'is_resolved')
        }),
        ('Запрос', {
            'fields': ('path', 'method', 'ip_address', 'user_agent')
        }),
        ('Детали ошибки', {
            'fields': ('traceback_display', 'extra_data_display'),
            'classes': ('collapse',)
        }),
        ('Разрешение', {
            'fields': ('resolved_at', 'resolved_by'),
            'classes': ('collapse',)
        }),
    )
    
    def message_short(self, obj):
        """Короткое сообщение"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_short.short_description = 'Сообщение'
    
    def traceback_display(self, obj):
        """Красивое отображение traceback"""
        if not obj.traceback:
            return '-'
        return format_html(
            '<pre style="max-height: 400px; overflow: auto; background: #f5f5f5; padding: 10px;">{}</pre>',
            obj.traceback
        )
    traceback_display.short_description = 'Traceback'
    
    def extra_data_display(self, obj):
        if not obj.extra_data:
            return '-'
        return format_html(
            '<pre style="max-height: 300px; overflow: auto;">{}</pre>',
            json.dumps(obj.extra_data, indent=2, ensure_ascii=False)
        )
    extra_data_display.short_description = 'Дополнительные данные'
    
    def has_add_permission(self, request):
        return False
    
    actions = ['mark_as_resolved']
    
    def mark_as_resolved(self, request, queryset):
        """Отметить ошибки как решенные"""
        queryset.update(
            is_resolved=True,
            resolved_at=timezone.now(),
            resolved_by=request.user.username
        )
        self.message_user(request, f'{queryset.count()} ошибок отмечено как решенные')
    mark_as_resolved.short_description = 'Отметить как решенные'