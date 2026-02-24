from rest_framework import serializers
from .models import Product, NewsletterSubscriber, Characteristic, HeroImage, GalleryImage, OrderItem, Order, Page, Favorite, ProductType, CharacteristicValue, ProductCharacteristic, ProductImage
from django.conf import settings
from decimal import Decimal
import json
import logging

logger = logging.getLogger(__name__)

class CharacteristicValueSerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(required=False, default=0)

    class Meta:
        model = CharacteristicValue
        fields = ['id', 'value', 'product_count']

class CharacteristicSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()

    class Meta:
        model = Characteristic
        fields = ['id', 'name', 'values']

    def get_values(self, obj):
        characteristic_values = self.context.get('characteristic_values')
        if characteristic_values is not None:
            values = characteristic_values.filter(characteristic=obj)
        else:
            values = CharacteristicValue.objects.filter(characteristic=obj)
        return CharacteristicValueSerializer(values, many=True).data

class ProductCharacteristicSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    value = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCharacteristic
        fields = ['name', 'value']
    
    def get_name(self, obj):
        """Безопасно получает имя характеристики"""
        try:
            if obj.characteristic:
                return obj.characteristic.name
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении имени характеристики: {e}")
            return None
    
    def get_value(self, obj):
        """Безопасно получает значение характеристики"""
        try:
            if obj.characteristic_value:
                return obj.characteristic_value.value
            return None
        except Exception as e:
            logger.error(f"Ошибка при получении значения характеристики: {e}")
            return None

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = ['id', 'name', 'slug']

class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'order']

    def get_image(self, obj):
        if obj.image:
            return f"{settings.MEDIA_URL}{obj.image}"
        return None

class ProductSerializer(serializers.ModelSerializer):
    imageUrl = serializers.SerializerMethodField()
    characteristics = serializers.SerializerMethodField()
    product_type = ProductTypeSerializer(read_only=True)
    is_favorite = serializers.SerializerMethodField()
    custom_url = serializers.CharField(read_only=True)
    price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_per_cubic_meter = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_per_square_meter = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    price_per_linear_meter = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    
    # Добавляем поля для единиц измерения
    primary_unit = serializers.CharField(read_only=True)
    unit_value = serializers.SerializerMethodField()
    unit_label = serializers.SerializerMethodField()
    dimension_values = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'quantity', 'is_available', 'imageUrl',
                 'characteristics', 'is_favorite', 'is_featured', 'product_type', 'custom_url',
                 'price_per_unit', 'price_per_cubic_meter', 'price_per_square_meter', 'price_per_linear_meter',
                 'primary_unit', 'unit_value', 'unit_label', 'dimension_values', 'price', 'images']
        
    def get_imageUrl(self, obj):
        if obj.imageUrl:
            return f"{settings.MEDIA_URL}{obj.imageUrl}"
        return None

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.session.session_key:
            return Favorite.objects.filter(product=obj, session_key=request.session.session_key).exists()
        return False
    
    def get_unit_value(self, obj):
        """Получить значение единицы измерения в штуке (объем, площадь или длина)"""
        if obj.primary_unit == 'cubic' and obj.volume_per_unit:
            return float(obj.volume_per_unit)
        elif obj.primary_unit == 'square' and obj.area_per_unit:
            return float(obj.area_per_unit)
        elif obj.primary_unit == 'linear' and obj.linear_meters_per_unit:
            return float(obj.linear_meters_per_unit)
        return None
    
    def get_unit_label(self, obj):
        """Получить метку единицы измерения (м³, м², погонный метр)"""
        return obj.get_unit_label()
    
    def get_dimension_values(self, obj):
        """Получить значения размеров в удобном формате для фронтенда"""
        dimensions = {}
        if obj.length:
            dimensions['length'] = float(obj.length)
        if obj.width:
            dimensions['width'] = float(obj.width)
        if obj.thickness:
            dimensions['thickness'] = float(obj.thickness)
        
        return dimensions

    def get_characteristics(self, obj):
        """Безопасно получает характеристики продукта"""
        try:
            # Фильтруем только валидные характеристики, у которых есть и характеристика и значение
            valid_characteristics = obj.product_characteristics.filter(
                characteristic__isnull=False,
                characteristic_value__isnull=False
            )
            
            return ProductCharacteristicSerializer(valid_characteristics, many=True).data
        except Exception as e:
            logger.error(f"Ошибка при получении характеристик продукта {obj.id}: {e}")
            return []

class HeroImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeroImage
        fields = '__all__'

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = '__all__'
    
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)
    
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product_id', 'title', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    # Определяем поле items как сериализатор для вложенных объектов
    order_items = OrderItemSerializer(many=True, read_only=True)
    items = serializers.JSONField(write_only=True, required=False)
    
    class Meta:
        model = Order
        fields = ['id', 'customer_type', 'first_name', 'last_name', 'phone', 
                 'email', 'comment', 'delivery_method', 'items', 'order_items',
                 'order_number', 'total_price', 'created_at', 'status']
        read_only_fields = ['created_at', 'order_items', 'order_number']

    def validate_phone(self, value):
        import re
        if value:
            cleaned = re.sub(r'[\s\-\(\)]', '', value)
            if not re.match(r'^\+?[1-9]\d{6,14}$', cleaned):
                raise serializers.ValidationError('Неверный формат телефона')
        return value

    def validate_first_name(self, value):
        if value and len(value.strip()) < 2:
            raise serializers.ValidationError('Имя слишком короткое')
        return value.strip() if value else value

    def validate_comment(self, value):
        # Ограничиваем длину комментария
        if value and len(value) > 1000:
            raise serializers.ValidationError('Комментарий не должен превышать 1000 символов')
        return value

    def create(self, validated_data):
        # Извлекаем items из validated_data
        items_data = validated_data.pop('items', [])
        
        # Рассчитываем общую сумму заказа
        total_price = Decimal('0')
        try:
            for item in items_data:
                quantity = int(item.get('quantity', 1))
                price = Decimal(str(item.get('price', '0')).replace(',', '.'))
                total_price += quantity * price
        except Exception as e:
            logger.error(f"Ошибка при расчете total_price: {e}")
        
        # Устанавливаем total_price
        validated_data['total_price'] = total_price
        
        # Создаем заказ
        order = Order.objects.create(**validated_data)
        
        # Создаем связанные OrderItem
        for item_data in items_data:
            try:
                # Очищаем и валидируем данные
                product_id = item_data.get('product_id')
                title = str(item_data.get('title', '')).strip() or "Неизвестный товар"
                
                try:
                    quantity = int(item_data.get('quantity', 1))
                    if quantity <= 0:
                        quantity = 1
                except (ValueError, TypeError):
                    quantity = 1
                
                try:
                    price_str = str(item_data.get('price', '0')).replace(',', '.')
                    price = Decimal(price_str)
                    if price < 0:
                        price = Decimal('0')
                except (InvalidOperation, TypeError):
                    price = Decimal('0')
                
                OrderItem.objects.create(
                    order=order,
                    product_id=product_id,
                    title=title,
                    quantity=quantity,
                    price=price
                )
            except Exception as e:
                logger.error(f"Ошибка при создании OrderItem: {e}")
                # Продолжаем с следующим элементом
                continue
        
        return order

class PageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ['id', 'product', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product'] = ProductSerializer(instance.product, context=self.context).data
        return representation

class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
