<script setup>
import { ref, inject, watch, onMounted, computed, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import ThemeToggle from './ThemeToggle.vue'
import { getProductTypes } from '../api'

const emit = defineEmits(['openDrawer'])

const { cart, favorites, updateFavorites } = inject('cart')
const { isDarkMode, toggleDarkMode } = inject('theme')

const handleToggleDarkMode = () => {
  toggleDarkMode()
}

const isMenuOpen = ref(false)
const isMobile = ref(window.innerWidth < 768)
const isProductTypesMenuOpen = ref(false)
const productTypes = ref([])
const burgerMenu = ref(null)

const router = useRouter()

const handleLogoClick = () => {
  updateFavorites()
  // Если уже на главной — просто скроллим наверх
  if (router.currentRoute.value.path === '/') {
    const mainContent = document.getElementById('main-content')
    if (mainContent) {
      mainContent.scrollTo({ top: 0, behavior: 'smooth' })
    }
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

const toggleMenu = () => {
  isMenuOpen.value = !isMenuOpen.value
  if (isMenuOpen.value) {
    nextTick(() => {
      document.addEventListener('click', handleOutsideClick)
    })
  } else {
    removeOutsideClickHandler()
  }
}

const removeOutsideClickHandler = () => {
  document.removeEventListener('click', handleOutsideClick)
}

const handleOutsideClick = (event) => {
  // Проверяем, был ли клик вне меню и не на кнопке открытия меню
  if (
    burgerMenu.value &&
    !burgerMenu.value.contains(event.target) &&
    !event.target.closest('.menu-toggle-button')
  ) {
    isMenuOpen.value = false
    removeOutsideClickHandler()
  }
}

const toggleProductTypesMenu = () => {
  isProductTypesMenuOpen.value = !isProductTypesMenuOpen.value
}

const closeMenu = () => {
  isMenuOpen.value = false
  isProductTypesMenuOpen.value = false
  removeOutsideClickHandler()
}

const hasItemsInCart = computed(() => cart.value.length > 0)

// Updated computed property to handle both mobile view and dark mode
const logoSrc = computed(() => {
  if (isMobile.value) {
    return isDarkMode.value ? '/logo_short_dark.svg' : '/logo_short.svg'
  } else {
    return isDarkMode.value ? '/logo_dark.svg' : '/logo.svg'
  }
})

const hasFavorites = computed(() => {
  console.log('Computing hasFavorites:', favorites.value)
  return Array.isArray(favorites.value) && favorites.value.length > 0
})

watch(
  favorites,
  (newFavorites) => {
    console.log('Favorites changed in Header:', newFavorites)
    console.log('Has favorites:', hasFavorites.value)
  },
  { deep: true }
)

const fetchProductTypes = async () => {
  try {
    const response = await getProductTypes()
    console.log('респонсе ', response.data)
    productTypes.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (error) {
    console.error('Ошибка при загрузке типов товаров:', error)
  }
}
// Следим за изменением ширины экрана
watch(
  () => window.innerWidth,
  (newWidth) => {
    if (newWidth >= 1280) {
      // 1280px соответствует xl в Tailwind
      isMenuOpen.value = false
    }
    isMobile.value = newWidth < 768
  }
)

let closeTimer = null

const startCloseTimer = () => {
  closeTimer = setTimeout(() => {
    isProductTypesMenuOpen.value = false
  }, 300)
}

const clearCloseTimer = () => {
  if (closeTimer) {
    clearTimeout(closeTimer)
  }
}

const closeProductTypesMenu = () => {
  isProductTypesMenuOpen.value = false
}

watch(
  () => router.currentRoute.value.fullPath,
  () => {
    if (isMenuOpen.value) {
      closeMenu()
    }
  }
)

onUnmounted(() => {
  if (closeTimer) {
    clearTimeout(closeTimer)
  }
  removeOutsideClickHandler()
})

// Добавляем слушатель при монтировании компонента
onMounted(() => {
  window.addEventListener('resize', () => {
    if (window.innerWidth >= 1280) {
      isMenuOpen.value = false
    }
    isMobile.value = window.innerWidth < 768
  })
  fetchProductTypes()
  updateFavorites()
})
</script>


<template>
  <header class="py-4 px-4 absolute top-0 left-0 right-0 z-50 pointer-events-none">
    <div class="flex items-center justify-between gap-4">
      <div class="p-2 rounded-lg h-16 flex items-center flex-shrink-0 pointer-events-auto">
        <router-link to="/" @click="handleLogoClick" class="logo-link">
          <img :src="logoSrc" alt="Wooddon Logo" class="logo h-12 w-auto object-contain" />
        </router-link>
      </div>

      <div
        class="bg-[#d4d1f0] dark:bg-gray-700 p-2 rounded-full h-16 flex items-center justify-between hidden xl:flex pointer-events-auto"
      >
        <nav class="header__menu">
          <div class="header__menu__inner font-semibold">
            <div class="relative group">
              <router-link
                to="/all-products"
                class="header__button"
                @mouseover="isProductTypesMenuOpen = true"
                @mouseleave="startCloseTimer"
              >
                Все товары
              </router-link>
              <div
                v-if="isProductTypesMenuOpen"
                class="absolute absolute_bubble top-full left-0 bg-white dark:bg-gray-800 rounded-2xl shadow-lg py-2 mt-8"
                @mouseover="clearCloseTimer"
                @mouseleave="closeProductTypesMenu"
              >
                <div class="grid grid-cols-2 gap-x-4 gap-y-2 px-4">
                  <router-link
                    v-for="type in productTypes"
                    :key="type.id"
                    :to="`/all-products/${type.slug}`"
                    class="block p-2 font-medium hover:text-sky-400 dark:hover:gray-700 whitespace-nowrap"
                  >
                    {{ type.name }}
                  </router-link>
                </div>
              </div>
            </div>
            <router-link to="/new-products" class="header__button">Новинки</router-link>
            <router-link to="/contacts" class="header__button">Контакты</router-link>
            <router-link to="/delivery" class="header__button">Доставка</router-link>
            <router-link to="/about" class="header__button">О компании</router-link>
            <!-- Закомментировано временно
            <a href="/wooddon_pricelist.xlsx" download class="header__button flex items-center gap-1">
              <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
              </svg>
              Прайс-лист
            </a>
            -->
          </div>
        </nav>
      </div>

      <div class="header__desktop__bar__r h-16 flex items-center flex-shrink-0 xl:flex hidden pointer-events-auto">
        <ul
          class="flex items-center gap-3 md:gap-4 lg:gap-5 header__desktop__buttons header__desktop__buttons--icons"
        >
          <li>
            <div class="scale-125 ml-4">
              <ThemeToggle :is-dark-mode="isDarkMode" @toggle="handleToggleDarkMode" />
            </div>
          </li>
          <li
            @click="() => emit('openDrawer')"
            class="flex items-center cursor-pointer gap-2 text-slate-500 hover:text-black dark:hover:text-white"
          >
            <img
              :src="hasItemsInCart ? '/cart_check.svg' : '/cart.svg'"
              alt="Cart"
              class="w-6 h-6"
            />
          </li>
          <li
            class="flex items-center cursor-pointer gap-2 text-slate-500 hover:text-black dark:hover:text-white"
          >
            <router-link
              to="/favorites"
              class="flex items-center gap-2 mr-3"
              @click="updateFavorites"
            >
              <img
                :src="hasFavorites ? '/heart_red.svg' : '/heart1.svg'"
                :alt="hasFavorites ? 'Favorites (not empty)' : 'Favorites (empty)'"
                class="w-6 h-6 object-contain"
              />
            </router-link>
          </li>
        </ul>
      </div>

      <button
        @click.stop="toggleMenu"
        class="xl:hidden p-2 bg-[#eeecfe] dark:bg-gray-700 rounded-full menu-toggle-button header__menu pointer-events-auto"
      >
        <img src="/menu.svg" alt="Menu" class="w-8 h-8" />
      </button>
    </div>

    <div
      v-if="isMenuOpen"
      ref="burgerMenu"
      class="burger-menu xl:hidden bg-white dark:bg-gray-800 mt-4 rounded-lg shadow-lg pointer-events-auto"
    >
      <nav class="burger-menu__nav">
        <div class="relative">
          <button @click="toggleProductTypesMenu" class="burger-menu__button text-left">
            <span>Все товары</span>
            <span class="burger-menu__arrow">▼</span>
          </button>
          <div v-if="isProductTypesMenuOpen" class="pl-4">
            <router-link
              v-for="type in productTypes"
              :key="type.id"
              :to="`/all-products/${type.slug}`"
              class="block p-2 font-medium hover:text-sky-400 dark:hover:text-gray-300"
              @click="closeMenu"
            >
              {{ type.name }}
            </router-link>
          </div>
        </div>

        <router-link to="/new-products" class="burger-menu__button" @click="closeMenu"
          >Новинки</router-link
        >
        <router-link to="/contacts" class="burger-menu__button" @click="closeMenu"
          >Контакты</router-link
        >
        <router-link to="/delivery" class="burger-menu__button" @click="closeMenu"
          >Доставка</router-link
        >
        <router-link to="/about" class="burger-menu__button" @click="closeMenu"
          >О компании</router-link
        >
        <!-- Закомментировано временно
        <a href="/wooddon_pricelist.xlsx" download class="burger-menu__button flex items-center gap-2">
          <svg class="w-4 h-4 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
            <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
          </svg>
          Прайс-лист
        </a>
        -->
      </nav>
      <hr class="burger-menu__divider" />
      <div class="burger-menu__icons">
        <ThemeToggle :is-dark-mode="isDarkMode" @toggle="handleToggleDarkMode" />
        <button @click="() => emit('openDrawer')" class="burger-menu__icon-button">
          <img :src="hasItemsInCart ? '/cart_check.svg' : '/cart.svg'" alt="Cart" class="w-6 h-6" />
        </button>
        <router-link to="/favorites" class="burger-menu__icon-button" @click="updateFavorites">
          <img
            :src="hasFavorites ? '/heart_red.svg' : '/heart1.svg'"
            alt="Favorites"
            class="w-6 h-6"
          />
        </router-link>
      </div>
    </div>
  </header>
</template>

<style scoped>
.dark {
  color-scheme: dark;
}

.dark body {
  background: linear-gradient(45deg, #1a1c20, #2c3e50, #34495e);
}
.header__menu {
  z-index: 20;
}

.header__menu__inner {
  display: flex;
  height: 100%;
}

.header__button {
  margin: 0 10px;
  color: #000;
  text-decoration: none;
  cursor: pointer;
  transition: color 0.3s ease;
}

.header__button:hover {
  color: #4a5568;
}

.dark .header__button:hover {
  color: #d8dbc7;
}

.group:hover .absolute {
  display: block;
}

.whitespace-nowrap {
  white-space: nowrap;
}

.overflow-hidden {
  overflow: hidden;
}

.text-ellipsis {
  text-overflow: ellipsis;
}

.header__desktop__bar__r {
  border-radius: 50px;
  padding: 0 10px;
  background-color: #e5e7eb;
}

.header__desktop__buttons {
  display: flex;
  height: 100%;
  align-items: center;
}

.header__desktop__buttons--icons {
  overflow: hidden;
}

.dark .header__desktop__bar__r {
  background-color: #3a3f44;
}

.dark .header__desktop__buttons--icons li {
  color: #a0aec0;
}

.dark .header__desktop__buttons--icons li:hover {
  color: #ffffff;
}

.dark .header__button {
  color: #ffffff;
}

.burger-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: calc(100vh - 180px); /* Уменьшаем максимальную высоту */
  overflow-y: auto;
  margin: 0 20px 20px; /* Добавляем отступы по бокам и снизу */
  
}

/* .burger-menu__content {
  display: flex;
  flex-direction: column;
  height: 100%;
} */

.burger-menu__nav {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  padding: 1rem;
}

.burger-menu__button {
  padding: 0.5rem 0;
  color: #000;
  text-decoration: none;
  position: relative;
  display: flex;
  /* justify-content: space-between;
  align-items: center; */
}

.burger-menu__arrow {
  margin-left: 0.5rem;
}

.burger-menu__divider {
  border-top: 1px solid #e2e8f0;
  margin: 0.5rem 0;
}

.burger-menu__icons {
  display: flex;
  align-items: center;
  padding: 1rem;
  justify-content: flex-start;
}

.burger-menu__icon-button {
  padding: 0.5rem;
  margin-right: 0.5rem;
}

/* Стили для скроллбара */
.burger-menu::-webkit-scrollbar {
  width: 6px;
}

.burger-menu::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.burger-menu::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 3px;
}

.burger-menu::-webkit-scrollbar-thumb:hover {
  background: #555;
}

.dark .burger-menu__button {
  color: #ffffff;
}

.dark .burger-menu__divider {
  border-top-color: #4a5568;
}

.dark .burger-menu__icon-button {
  background: transparent;
}

.absolute_bubble {
  width: max-content;
}

/* @media (max-width: 1224px) {
  .xl\:flex {
    display: none;
  }
  .xl\:hidden {
    display: flex;
  }
} */
</style>
