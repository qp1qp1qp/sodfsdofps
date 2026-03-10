<script setup>
import { ref, watch, provide, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Header from './components/Header.vue'
import Drawer from './components/Drawer.vue'
import { getFavorites, addFavorite, removeFavorite } from './api'
import StructuredData from './components/StructuredData.vue'
import SkipToContent from './components/SkipToContent.vue'
import FloatingBubbles from './components/FloatingBubbles.vue'
import PhoneBubble from './components/PhoneBubble.vue'

const router = useRouter()

watch(
  () => router.currentRoute.value.path,
  () => {
    // Прокрутка основного контента
    setTimeout(() => {
      const mainContent = document.getElementById('main-content');
      if (mainContent) {
        mainContent.scrollTop = 0;
      }
      window.scrollTo(0, 0);
    }, 300);
  }
)

const isSmallScreen = ref(window.innerWidth < 479)

const checkScreenSize = () => {
  isSmallScreen.value = window.innerWidth < 479
}

/* Корзина (start) */
const cart = ref([])
const favorites = ref([])
const drawerOpen = ref(false)
const totalPrice = computed(() =>
  cart.value.reduce((acc, item) => acc + Number(item.price) * item.quantity, 0)
)

// Добавьте эти строки для управления темной темой
const isDarkMode = ref(false)

const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
  localStorage.setItem('darkMode', isDarkMode.value)
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}

const closeDrawer = () => {
  drawerOpen.value = false
}

const openDrawer = () => {
  drawerOpen.value = true
}

const addToCart = (item) => {
  if (!item) {
    if (import.meta.env.DEV) console.error('App.vue: Attempted to add undefined item to cart');
    return;
  }
  if (!item.id || !item.title || !item.quantity) {
    if (import.meta.env.DEV) console.error('App.vue: Item missing required fields:', item);
    return;
  }

  const existingItemIndex = cart.value.findIndex(cartItem => cartItem.id === item.id);

  if (existingItemIndex >= 0) {
    const existingQuantity = cart.value[existingItemIndex].quantity;
    const newQuantity = existingQuantity + item.quantity;
    const updatedCart = [...cart.value];
    updatedCart[existingItemIndex] = {
      ...updatedCart[existingItemIndex],
      quantity: newQuantity,
      isAdded: true
    };
    cart.value = updatedCart;
  } else {
    cart.value.push({ ...item, isAdded: true });
  }

  localStorage.setItem('cart', JSON.stringify(cart.value));
}

const removeFromCart = (item) => {
  cart.value = cart.value.filter((cartItem) => cartItem.id !== item.id)
}

const updateCartItemQuantity = (itemId, newQuantity) => {
  // Создаём новый массив — гарантирует реактивное обновление computed во всех дочерних компонентах
  cart.value = cart.value.map(item =>
    item.id === itemId
      ? { ...item, quantity: newQuantity, price: item.price_per_unit }
      : item
  )
}

watch(
  cart,
  () => {
    localStorage.setItem('cart', JSON.stringify(cart.value))
  },
  { deep: true }
)

const isFavoriteOperationInProgress = ref(false);

const updateFavorites = async () => {
  try {
    const { data } = await getFavorites()
    favorites.value = data.map((fav) => fav.product.id)
    return favorites.value
  } catch (err) {
    if (import.meta.env.DEV) console.error('Ошибка при обновлении избранных товаров:', err)
    return favorites.value
  }
}

const toggleFavoriteItem = async (item) => {
  if (isFavoriteOperationInProgress.value) {
    return false;
  }

  isFavoriteOperationInProgress.value = true;

  try {
    const isFavorite = favorites.value.includes(item.id);

    if (isFavorite) {
      await removeFavorite(item.id);
    } else {
      await addFavorite(item.id);
    }

    if (isFavorite) {
      favorites.value = favorites.value.filter(id => id !== item.id);
    } else {
      favorites.value = [...favorites.value, item.id];
    }

    await updateFavorites();
    isFavoriteOperationInProgress.value = false;
    return true;
  } catch (error) {
    if (import.meta.env.DEV) console.error('Ошибка при обновлении избранного:', error);
    isFavoriteOperationInProgress.value = false;
    await updateFavorites();
    return false;
  }
}

onMounted(async () => {
  const savedCart = localStorage.getItem('cart')
  if (savedCart) {
    try {
      cart.value = JSON.parse(savedCart)
    } catch (e) {
      localStorage.removeItem('cart')
    }
  }
  await updateFavorites()

  const savedDarkMode = localStorage.getItem('darkMode') === 'true'
  isDarkMode.value = savedDarkMode
  if (savedDarkMode) {
    document.documentElement.classList.add('dark')
  }

  window.addEventListener('resize', checkScreenSize)
  checkScreenSize()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', checkScreenSize)
})

const clearCart = () => {
  cart.value.forEach((item) => {
    item.isAdded = false
  })
  cart.value = []
  localStorage.removeItem('cart')
}


provide('theme', { isDarkMode, toggleDarkMode })

provide('layout', { isSmallScreen  })

provide('cart', {
  cart,
  favorites,
  closeDrawer,
  openDrawer,
  addToCart,
  removeFromCart,
  clearCart,
  updateFavorites,
  toggleFavoriteItem,
  updateCartItemQuantity,
  totalPrice
})
</script>

<template>
  <template v-if="isSmallScreen">
    <StructuredData />
    <SkipToContent />
    <div
      :class="[
        'app-container-mobile bg-[#fbfcf4] dark:bg-[#292e33] flex flex-col relative overflow-hidden',
        { dark: isDarkMode }
      ]"
    >
      <!-- Добавляем класс fixed-header для хедера на маленьких экранах -->
      <div class="fixed-header w-full z-10">
        <Header
          :total-price="totalPrice"
          :has-favorites="favorites.length > 0"
          @open-drawer="openDrawer"
          :is-dark-mode="isDarkMode"
          @toggle-dark-mode="toggleDarkMode"
        />
      </div>
      
      <!-- Добавляем отступ для контента, равный высоте хедера -->
      <div class="header-spacer"></div>

      <main id="main-content" class="flex-grow overflow-y-scroll">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>

      <Drawer v-if="drawerOpen" :total-price="totalPrice" />
    </div>
  </template>
  <template v-else>
    <StructuredData />
    <SkipToContent />
    <div class="app-wrapper">
      <FloatingBubbles class="floating-bubbles-background" />
      
      <div
        :class="[
          'app-container bg-[#fbfcf4] dark:bg-[#292e33] mx-6 rounded-xl shadow-2xl flex flex-col my-6 relative overflow-hidden',
          { dark: isDarkMode }
        ]"
        :style="{ height: 'calc(100vh - 3rem)' }"
      >
        <Header
          :total-price="totalPrice"
          :has-favorites="favorites.length > 0"
          @open-drawer="openDrawer"
          :is-dark-mode="isDarkMode"
          @toggle-dark-mode="toggleDarkMode"
        />

        <main id="main-content" class="flex-grow overflow-y-scroll">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </main>

        <Drawer v-if="drawerOpen" :total-price="totalPrice" />
      </div>
    </div>
  </template>
  <PhoneBubble />
</template>

<style scoped>
.app-wrapper {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.floating-bubbles-background {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
}

.app-container {
  backdrop-filter: blur(5px);
  z-index: 1;
  width: calc(100% - 3rem);
  max-height: calc(100vh - 3rem);
  margin: 1.5rem;
}

.app-container-mobile {
  min-height: 100vh; /* Используем min-height вместо height для iOS */
  width: 100%;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Фиксированный хедер для мобильных устройств */
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background-color: inherit; /* Наследуем цвет фона от родителя */
}

</style>
