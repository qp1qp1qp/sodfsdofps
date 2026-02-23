<script setup>
import { ref, onMounted, inject, watch } from 'vue'
import { getFavorites, removeFavorite } from '../api'
import ItemList from '../components/ItemList.vue'
import Footer from '../components/Footer.vue'

const { cart, addToCart, updateFavorites, toggleFavoriteItem, favorites: globalFavorites } = inject('cart')

const favoriteItems = ref([])

const fetchFavorites = async () => {
  try {
    const response = await getFavorites();
    
    // Синхронизируем локальный стор со свежими данными
    const favData = Array.isArray(response.data) ? response.data : response.data.results || [];
    globalFavorites.value = favData.map((fav) => fav.product.id);
    favoriteItems.value = favData.map((favorite) => ({
      ...favorite.product,
      isFavorite: true,
      isAdded: cart.value.some((cartItem) => cartItem.id === favorite.product.id)
    }));
    
    console.log('Fetched favorites:', favoriteItems.value)
  } catch (err) {
    console.error('Ошибка при загрузке избранных товаров:', err)
  }
}

const toggleFavorite = async (item) => {
  try {
    console.log('Favorites.vue: Изменение статуса избранного для товара', item.id);
    
    const success = await toggleFavoriteItem(item);
    
    if (success) {
      await fetchFavorites();
    }
  } catch (err) {
    console.error('Ошибка при обновлении избранного:', err);
    
    await fetchFavorites();
  }
}

const onClickAdd = (itemData) => {
  console.log(
    `Favorites.vue: Добавление в корзину. ID: ${itemData.id}, Название: ${itemData.title}, Количество: ${itemData.quantity}, Цена за единицу: ${itemData.price_per_unit}`
  )
  addToCart(itemData)
}

onMounted(() => {
  fetchFavorites()
})

watch(
  cart,
  () => {
    favoriteItems.value = favoriteItems.value.map((item) => ({
      ...item,
      isAdded: cart.value.some((cartItem) => cartItem.id === item.id)
    }))
  },
  { deep: true }
)

watch(
  globalFavorites,
  () => {
    favoriteItems.value = favoriteItems.value.filter(item => 
      globalFavorites.value.includes(item.id)
    );
  },
  { deep: true }
)
</script>

<template>
  <div class="main-container">
    <div class="content mt-20">
      <div class="container mx-auto px-4 py-8">
        <h1 class="text-3xl font-bold mb-8 dark:text-white">Избранное</h1>
        <ItemList :items="favoriteItems" @add-to-favorite="toggleFavorite" @addToCart="onClickAdd" />
        <div v-if="favoriteItems.length === 0" class="text-center text-gray-500 dark:text-gray-400">
          У вас пока нет избранных товаров.
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
  min-height: 100%;
}

.content {
  flex: 1;
}
</style>
