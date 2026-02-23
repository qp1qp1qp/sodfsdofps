<script setup>
import { ref, computed, onMounted, inject, watch } from 'vue'
import { getProducts, addFavorite, removeFavorite, getFavorites } from '../api'
import Footer from '../components/Footer.vue'
import ItemList from '../components/ItemList.vue'
import { useHead } from '@vueuse/head'

const featuredItems = ref([])
const { cart, addToCart, updateFavorites, toggleFavoriteItem, favorites } = inject('cart')


const baseImageUrl = import.meta.env.VITE_API_URL || ''

// Добавляем мета-теги для SEO
useHead({
  title: 'Новинки | WoodDon',
  meta: [
    {
      name: 'description',
      content: 'Новые поступления пиломатериалов и строительных материалов. Свежие товары от WoodDon.'
    },
    {
      name: 'keywords',
      content: 'пиломатериалы, стройматериалы, новинки, новые поступления, WoodDon'
    }
  ]
})

onMounted(async () => {
  try {
    // First get the favorites to properly sync the UI
    const favoritesResponse = await getFavorites();
    const favoritesData = favoritesResponse.data;
    
    const { data } = await getProducts({ is_featured: true })
    const productsData = Array.isArray(data) ? data : data.results || []
    featuredItems.value = productsData.map((item) => {
      // Check if item is in cart
      const isInCart = cart.value.some((cartItem) => cartItem.id === item.id);
      
      return {
        ...item,
        price_per_unit: Number(item.price_per_unit),
        price_per_cubic_meter: Number(item.price_per_cubic_meter),
        quantity: Number(item.quantity) || 0,
        // Use server data for favorite status - not local state
        isFavorite: favoritesData.some((fav) => fav.product.id === item.id),
        isAdded: isInCart
      };
    });
    
    console.log('Loaded featured items with favorites sync:', featuredItems.value)
  } catch (error) {
    console.error('Ошибка при загрузке новых товаров:', error)
  }
})

// Добавляем наблюдение за корзиной, чтобы обновлять состояние кнопок
watch(cart, () => {
  // Обновляем isAdded для каждого товара на основе состояния корзины
  featuredItems.value.forEach(item => {
    const isInCart = cart.value.some(cartItem => cartItem.id === item.id);
    item.isAdded = isInCart;
  });
}, { deep: true });

// Добавляем наблюдение за глобальным состоянием избранного
watch(favorites, (newFavorites) => {
  console.log('NewProducts: Обновление UI в соответствии с избранным');
  
  // Создаем временную копию элементов для работы
  const updatedItems = [...featuredItems.value];
  let hasChanges = false;
  
  // Проходим по всем товарам и обновляем их статус
  updatedItems.forEach(item => {
    const shouldBeFavorite = newFavorites.includes(item.id);
    if (item.isFavorite !== shouldBeFavorite) {
      item.isFavorite = shouldBeFavorite;
      hasChanges = true;
      console.log(`NewProducts: Обновлен статус избранного для ${item.id} на ${shouldBeFavorite}`);
    }
  });
  
  // Если были изменения, обновляем весь массив для реактивности
  if (hasChanges) {
    featuredItems.value = updatedItems;
  }
}, { deep: true });

const getFullImageUrl = (imageUrl) => {
  if (imageUrl && !imageUrl.startsWith('http')) {
    const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/api\/?$/, '');
    return `${baseUrl}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`
  }
  return imageUrl
}

const addToFavorite = async (item) => {
  try {
    console.log('NewProducts.vue: Изменение статуса избранного для товара', item.id);
    
    // Вызываем централизованную функцию
    const success = await toggleFavoriteItem(item);
    
    if (success) {
      // Явно обновляем UI для этого конкретного товара
      const updatedItem = featuredItems.value.find(i => i.id === item.id);
      if (updatedItem) {
        // Устанавливаем точное значение из глобального состояния
        updatedItem.isFavorite = favorites.value.includes(item.id);
        console.log(`NewProducts.vue: Обновлен статус избранного для товара ${item.id} на ${updatedItem.isFavorite}`);
      }
    }
  } catch (err) {
    console.error('Ошибка при обновлении избранного:', err);
  }
}

const onClickAdd = (itemData) => {
  console.log(
    `NewProducts.vue: Добавление в корзину. ID: ${itemData.id}, Название: ${itemData.title}, Количество: ${itemData.quantity}, Цена за единицу: ${itemData.price_per_unit}`
  );
  
  // Обновляем локальное состояние товара
  const item = featuredItems.value.find(item => item.id === itemData.id);
  if (item) {
    item.isAdded = true;
  }
  
  // Добавляем в корзину
  addToCart(itemData);
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}
</script>

<template>
  <div class="main-container">
    <div class="content pt-20 sm:pt-24">
      <div class="container mx-auto px-2 xs:px-3 sm:px-4 py-4 sm:py-8 max-w-full xl:max-w-[1920px]">
        <h1 class="text-2xl md:text-3xl lg:text-4xl font-bold mb-8 text-center dark:text-white">Новинки</h1>

        <!-- Товары -->
        <div v-if="featuredItems.length > 0">
          <ItemList :items="featuredItems" @add-to-favorite="addToFavorite" @addToCart="onClickAdd" />
        </div>
        <div v-else class="py-12 text-center text-gray-500 dark:text-gray-400">
          Загрузка новинок...
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
}

.container {
  width: 100%;
}
</style>
