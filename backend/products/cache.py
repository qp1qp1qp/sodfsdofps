from django.core.cache import cache
from .models import Product, Favorite
from .serializers import ProductSerializer, FavoriteSerializer
import json
import logging

logger = logging.getLogger(__name__)
CACHE_TTL = 60 * 15  # 15 минут

def get_product_cache_key(product_id):
    return f"product:{product_id}"

def get_favorites_cache_key(session_key):
    return f"favorites:{session_key}"

def get_product(product_id):
    cache_key = get_product_cache_key(product_id)
    product_data = cache.get(cache_key)

    if product_data is None:
        try:
            product = Product.objects.get(id=product_id)
            serializer = ProductSerializer(product)
            product_data = serializer.data
            cache.set(cache_key, json.dumps(product_data), CACHE_TTL)
            logger.info(f"Product {product_id} cached")

        except Product.DoesNotExist:
            return None
    else:
        logger.info(f"Cache hit for product {product_id}")

    return json.loads(product_data) if isinstance(product_data, str) else product_data

def get_favorites(session_key):
    # Попытка получить из кэша
    cache_key = get_favorites_cache_key(session_key)
    favorites_data = cache.get(cache_key)
    
    # Всегда получаем свежие данные из базы
    favorites = Favorite.objects.filter(session_key=session_key)
    serializer = FavoriteSerializer(favorites, many=True, context={'request': None})
    favorites_data = serializer.data
    
    # Обновляем кэш, но всегда используем данные из БД
    cache.set(cache_key, json.dumps(favorites_data), CACHE_TTL)
    
    return favorites_data

def add_favorite(product_id, session_key):
    try:
        product = Product.objects.get(id=product_id)
        favorite, created = Favorite.objects.get_or_create(
            product=product,
            session_key=session_key
        )
        cache_key = get_favorites_cache_key(session_key)
        cache.delete(cache_key)  # Инвалидируем кэш избранного
        return favorite
    except Product.DoesNotExist:
        return None

def remove_favorite(product_id, session_key):
    Favorite.objects.filter(product_id=product_id, session_key=session_key).delete()
    cache_key = get_favorites_cache_key(session_key)
    cache.delete(cache_key)  # Инвалидируем кэш избранного
