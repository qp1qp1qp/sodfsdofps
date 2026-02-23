<script setup>
import { reactive, watch, ref, onMounted, onUnmounted, inject } from 'vue'
import { getProducts, getFavorites, addFavorite, removeFavorite } from '../api'
import debounce from 'lodash.debounce'
import BestItemsSlider from '../components/BestItemsSlider.vue'
import Footer from '../components/Footer.vue'
import Contact from '../components/Contact.vue'
import MixedProductGallery from '../components/MixedProducts.vue'
import { useHead } from '@vueuse/head'

const { cart, addToCart, removeFromCart, updateFavorites, favorites } = inject('cart')

// Разделяем массивы для разных секций
const galleryItems = ref([]) // Для обычной галереи (Наши товары)
const sliderItems = ref([])  // Для слайдера (Товары по акции)
const currentHeroIndex = ref(0)
const isMobile = ref(window.innerWidth < 768)
const isLoading = ref(true)

let autoSwitchInterval

useHead({
  title: 'WoodDon - Магазин пиломатериалов и стройматериалов',
  meta: [
    {
      name: 'description',
      content:
        'Широкий выбор пиломатериалов и стройматериалов в Ростове-на-Дону. Качественные товары, выгодные цены, быстрая доставка.'
    },
    {
      name: 'keywords',
      content: 'пиломатериалы, стройматериалы, доска обрезная, брус, Ростов-на-Дону'
    }
  ]
})

const heroItems = [
  {
    title: 'Скидки до 50%',
    subtitle: 'Успейте приобрести товары по выгодным ценам',
    image: '/pictures/hero1.jpg',
    link: '/lumber',
    buttonText: 'Смотреть предложения'
  },
  {
    title: 'Новые поступления',
    subtitle: 'Откройте для себя наши последние новинки',
    image: '/pictures/hero2.jpg',
    link: '/new-products',
    buttonText: 'Узнать больше'
  }
]

const filters = reactive({
  sortBy: 'title',
  searchQuery: ''
})

const onClickAddPlus = (item) => {
  console.log('Home.vue: Adding to cart, item details:', item);
  
  // Keep track of the item's existing added state
  const wasAlreadyAdded = item.isAdded;
  
  if (!wasAlreadyAdded) {
    // First time adding the item - use the quantity provided
    addToCart(item);
    
    // Update UI for both the regular items list and the bestItems list
    // Update in galleryItems array
    const itemInRegularList = galleryItems.value.find(i => i.id === item.id);
    if (itemInRegularList) {
      itemInRegularList.isAdded = true;
    }
    
    // Update in visible items in BestItemsSlider if present
    const itemInBestList = sliderItems.value.find(i => i.id === item.id);
    if (itemInBestList) {
      itemInBestList.isAdded = true;
    }
  } else {
    // If already in cart and the green + is clicked, remove it from cart
    // This is the behavior the user expects on the main page
    removeFromCart(item);
    
    // Update UI for both the regular items list and the bestItems list
    // Update in galleryItems array
    const itemInRegularList = galleryItems.value.find(i => i.id === item.id);
    if (itemInRegularList) {
      itemInRegularList.isAdded = false;
    }
    
    // Update in visible items in BestItemsSlider if present
    const itemInBestList = sliderItems.value.find(i => i.id === item.id);
    if (itemInBestList) {
      itemInBestList.isAdded = false;
    }
  }
}

const onChangeSelect = (event) => {
  filters.sortBy = event.target.value
  fetchGalleryItems() // Теперь обновляем только галерею
}

const onChangeSearchInput = debounce((event) => {
  filters.searchQuery = event.target.value
  fetchGalleryItems() // Теперь обновляем только галерею
}, 400)

const addToFavorite = async (item) => {
  try {
    console.log(`Home.vue: Обработка избранного для товара ${item.id}, исходный статус: ${item.isFavorite}`);
    
    const newFavoriteState = !item.isFavorite;
    
    if (newFavoriteState) {
      await addFavorite(item.id);
      console.log(`Товар ${item.id} добавлен в избранное`);
    } else {
      await removeFavorite(item.id);
      console.log(`Товар ${item.id} удален из избранного`);
    }
    
    await updateFavorites();
    
  } catch (err) {
    console.error('Ошибка при обновлении избранного:', err);
    
    // В случае ошибки нужно откатить состояние компонентов
    // Для этого используем временную переменную и повторно вызываем updateFavoriteStatus
    await updateFavoriteStatus();
  }
}

// Функция для получения товаров для слайдера (товары по акции)
const fetchSliderItems = async (favoritesData) => {
  try {
    console.log('Fetching slider items (featured products)');
    const params = { is_featured: true }
    const itemsResponse = await getProducts(params)

    const itemsData = Array.isArray(itemsResponse.data) ? itemsResponse.data : itemsResponse.data.results || []

    sliderItems.value = itemsData.map((obj) => {
      // Check if item is in cart
      const isInCart = cart.value.some((cartItem) => cartItem.id === obj.id);
      
      return {
        ...obj,
        isFavorite: favoritesData.some((fav) => fav.product.id === obj.id),
        isAdded: isInCart,
        // If the item is in cart, use the cart quantity
        quantity: isInCart 
          ? cart.value.find(cartItem => cartItem.id === obj.id).quantity
          : obj.quantity
      };
    });
    
    console.log('Processed slider items:', sliderItems.value.length);
  } catch (err) {
    console.error('Ошибка при загрузке товаров для слайдера:', err)
  }
}

// Функция для получения товаров для галереи (с применением фильтров)
const fetchGalleryItems = async (favoritesData) => {
  try {
    isLoading.value = true;
    const params = {
      sortBy: filters.sortBy,
      title: filters.searchQuery
    }
    console.log('Fetching gallery items with params:', params)
    const itemsResponse = await getProducts(params)

    const itemsData = Array.isArray(itemsResponse.data) ? itemsResponse.data : itemsResponse.data.results || []

    galleryItems.value = itemsData.map((obj) => {
      // Check if item is in cart
      const isInCart = cart.value.some((cartItem) => cartItem.id === obj.id);
      
      return {
        ...obj,
        isFavorite: favoritesData.some((fav) => fav.product.id === obj.id),
        isAdded: isInCart,
        // If the item is in cart, use the cart quantity
        quantity: isInCart 
          ? cart.value.find(cartItem => cartItem.id === obj.id).quantity
          : obj.quantity
      };
    });
    
    console.log('Processed gallery items:', galleryItems.value.length);
    isLoading.value = false;
  } catch (err) {
    console.error('Ошибка при загрузке данных для галереи:', err)
    isLoading.value = false;
  }
}

const updateFavoriteStatus = async () => {
  try {
    const favoritesResponse = await getFavorites()
    const favoritesData = favoritesResponse.data
    
    // Обновляем статус избранного для галереи
    galleryItems.value = galleryItems.value.map((item) => ({
      ...item,
      isFavorite: favoritesData.some((fav) => fav.product.id === item.id)
    }))
    
    // Обновляем статус избранного для слайдера
    sliderItems.value = sliderItems.value.map((item) => ({
      ...item,
      isFavorite: favoritesData.some((fav) => fav.product.id === item.id)
    }))
    
    console.log('Updated favorite status for all items')
  } catch (err) {
    console.error('Ошибка при обновлении статуса избранного:', err)
  }
}

onMounted(async () => {
  const localCart = localStorage.getItem('cart')
  cart.value = localCart ? JSON.parse(localCart) : []

  // Делаем единственный запрос за избранными товарами
  await updateFavorites();
  const currentFavorites = favorites.value || [];

  // Имитируем API-ответ для совместимости с функциями маппинга
  const favoritesData = currentFavorites.map(id => ({ product: { id } }));

  // Загружаем товары, передавая им общий список избранного
  await Promise.all([
    fetchSliderItems(favoritesData),
    fetchGalleryItems(favoritesData)
  ]);

  window.addEventListener('resize', () => {
    isMobile.value = window.innerWidth < 768
  })

  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) {
      updateFavoriteStatus()
    }
  })
})

const nextHero = () => {
  currentHeroIndex.value = (currentHeroIndex.value + 1) % heroItems.length
}

const prevHero = () => {
  currentHeroIndex.value = (currentHeroIndex.value - 1 + heroItems.length) % heroItems.length
}

const startAutoSwitch = () => {
  autoSwitchInterval = setInterval(nextHero, 8000)
}

const stopAutoSwitch = () => {
  clearInterval(autoSwitchInterval)
}

onMounted(() => {
  startAutoSwitch()
})

onUnmounted(() => {
  stopAutoSwitch()
})

// Слежение за изменениями фильтров только для обновления галереи
watch(filters, fetchGalleryItems)

// Обновляем статус "isAdded" при изменении корзины
watch(
  cart,
  () => {
    // Обновляем для галереи
    galleryItems.value = galleryItems.value.map((item) => ({
      ...item,
      isAdded: cart.value.some((cartItem) => cartItem.id === item.id)
    }))
    
    // Обновляем для слайдера
    sliderItems.value = sliderItems.value.map((item) => ({
      ...item,
      isAdded: cart.value.some((cartItem) => cartItem.id === item.id)
    }))
  },
  { deep: true }
)

// Обновляем статус "isFavorite" при изменении избранного
watch(
  favorites,
  (newFavorites) => {
    // Обновляем для галереи
    galleryItems.value = galleryItems.value.map((item) => ({
      ...item,
      isFavorite: newFavorites.includes(item.id)
    }))
    
    // Обновляем для слайдера
    sliderItems.value = sliderItems.value.map((item) => ({
      ...item,
      isFavorite: newFavorites.includes(item.id)
    }))
  },
  { deep: true }
)

const galleryImages = ref([
  '/pictures/mnogo_dosok.jpg',
  '/pictures/nov_doski.jpg',
  '/pictures/sklad.jpg',
  '/pictures/eshe_doski.jpg',
  '/pictures/doski.jpg'
])
</script>

<template>
  <div class="home-container">
    <h1 class="sr-only">WoodDon - Магазин пиломатериалов и стройматериалов</h1>
    <!-- Хиро баннеры -->
    <div
      class="hero-banners"
      aria-label="Специальные предложения"
      @mouseenter="stopAutoSwitch"
      @mouseleave="startAutoSwitch"
    >
      <div
        v-for="(hero, index) in heroItems"
        :key="index"
        class="hero-banner"
        :class="{ active: index === currentHeroIndex }"
      >
        <img
          :src="hero.image"
          :alt="hero.title"
          class="hero-image-img"
          :fetchpriority="index === 0 ? 'high' : 'auto'"
          :loading="index === 0 ? 'eager' : 'lazy'"
          width="1920"
          height="1080"
        />
        <div class="hero-overlay"></div>
        <div class="hero-content">
          <h2 class="hero-title">{{ hero.title }}</h2>
          <p class="hero-subtitle">{{ hero.subtitle }}</p>
          <router-link :to="hero.link" class="hero-button">
            {{ hero.buttonText }}
          </router-link>
        </div>
      </div>
      <div class="hero-nav">
        <button @click="prevHero" class="hero-nav-button prev">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="w-6 h-6"
          >
            <path
              fill-rule="evenodd"
              d="M7.72 12.53a.75.75 0 010-1.06l7.5-7.5a.75.75 0 111.06 1.06L9.31 12l6.97 6.97a.75.75 0 11-1.06 1.06l-7.5-7.5z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
        <button @click="nextHero" class="hero-nav-button next">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 24 24"
            fill="currentColor"
            class="w-6 h-6"
          >
            <path
              fill-rule="evenodd"
              d="M16.28 11.47a.75.75 0 010 1.06l-7.5 7.5a.75.75 0 01-1.06-1.06L14.69 12 7.72 5.03a.75.75 0 011.06-1.06l7.5 7.5z"
              clip-rule="evenodd"
            />
          </svg>
        </button>
      </div>
    </div>

    <div class="content">
      <!-- Бегущая строка -->

      <router-link
        to="/new-products"
        class="marquee-container rounded-2xl"
        role="marquee"
        aria-label="Горячие новинки"
      >
        <div class="marquee-content">
          <span class="marquee-text">Успей купить горячие новинки!</span>
        </div>
      </router-link>

      <!-- Блок с лучшими товарами -->
      <section aria-labelledby="best-items-title">
        <h2 id="best-items-title" class="text-2xl md:text-3xl font-bold mb-6 mt-8">
          Новинки
        </h2>
        <BestItemsSlider
          v-if="sliderItems.length > 0"
          :bestItems="sliderItems"
          @addToFavorite="addToFavorite"
          @addToCart="addToCart"
        />
      </section>

      <section aria-labelledby="our-products-title">
        <div
          class="flex flex-col md:flex-row justify-between items-start md:items-center pt-12 pb-4 md:pt-20"
        >
          <h2 id="our-products-title" class="text-4xl md:text-5xl font-bold mb-4 md:mb-0">
            Наши товары
          </h2>

          <div class="flex flex-col md:flex-row gap-4 w-full md:w-auto">
            <select
              @change="onChangeSelect"
              class="py-2 px-3 border rounded-md outline-none w-full md:w-auto"
            >
              <option value="title">Название</option>
              <option value="price">Цена (low to Up)</option>
              <option value="-price">Цена (Up to low)</option>
            </select>

            <div class="relative w-full md:w-auto">
              <img class="absolute left-4 top-3" src="/search.svg" />

              <input
                @input="onChangeSearchInput"
                class="border rounded-md py-2 pl-11 pr-4 outline-none focus:border-gray-400 w-full"
                placeholder="Search..."
              />
            </div>
          </div>
        </div>
      </section>

      <div v-if="isLoading" class="text-center py-8">
        <p>Загрузка товаров...</p>
      </div>
      <MixedProductGallery
        v-else
        :products="galleryItems"
        :images="galleryImages"
        @addToFavorite="addToFavorite"
        @addToCart="addToCart"
      />

      <!-- Блок с контактами -->
      <Contact />
    </div>
    <!-- Футер -->
    <Footer />
  </div>
</template>

<style scoped>
.home-container {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.hero-banners {
  height: calc(100vh - 3rem);
  position: relative;
  overflow: hidden;
}

.hero-banner {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  visibility: hidden;
  transition:
    opacity 0.5s ease-in-out,
    visibility 0.5s ease-in-out;
}

.hero-banner.active {
  opacity: 1;
  visibility: visible;
}

.hero-image-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transition: transform 0.3s ease-in-out;
  display: block;
}

.hero-banner:hover .hero-image-img {
  transform: scale(1.05);
}

.hero-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to right, rgba(0, 0, 0, 0.7) 0%, rgba(0, 0, 0, 0.3) 100%);
}

.hero-content {
  position: absolute;
  top: 50%;
  left: 10%;
  transform: translateY(-50%);
  color: white;
  max-width: 50%;
}

.hero-title {
  font-size: 3rem;
  font-weight: bold;
  margin-bottom: 1rem;
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity 0.5s ease-in-out,
    transform 0.5s ease-in-out;
}

.hero-subtitle {
  font-size: 1.5rem;
  margin-bottom: 2rem;
  opacity: 0;
  transform: translateY(20px);
  transition:
    opacity 0.5s ease-in-out,
    transform 0.5s ease-in-out;
}

.hero-button {
  display: inline-block;
  padding: 12px 24px;
  font-size: 1rem;
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid white;
  border-radius: 30px;
  text-decoration: none;
  transition:
    background-color 0.3s ease,
    color 0.3s ease;
  opacity: 0;
  transform: translateY(20px);
}

.hero-button:hover {
  background-color: white;
  color: black;
}

.hero-banner.active .hero-title,
.hero-banner.active .hero-subtitle,
.hero-banner.active .hero-button {
  opacity: 1;
  transform: translateY(0);
}

.hero-banner.active .hero-title {
  transition-delay: 0.3s;
}

.hero-banner.active .hero-subtitle {
  transition-delay: 0.5s;
}

.hero-nav {
  position: absolute;
  bottom: 30px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 30px;
}

.hero-nav-button {
  background-color: rgba(255, 255, 255, 0.3);
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background-color 0.1s ease;
}

.hero-nav-button:hover {
  background-color: rgba(255, 255, 255, 0.5);
}

.hero-nav-button svg {
  width: 24px;
  height: 24px;
}

@media (max-width: 768px) {
  .hero-content {
    left: 5%;
    max-width: 90%;
  }

  .hero-title {
    font-size: 2rem;
  }

  .hero-subtitle {
    font-size: 1rem;
  }

  .hero-button {
    padding: 10px 20px;
    font-size: 0.9rem;
  }
}

.content {
  padding: 2rem;
  flex: 1;
}

.marquee-container {
  display: block;
  overflow: hidden;
  background-color: #ffcf91;
  padding: 1rem 0;
  cursor: pointer;
  text-decoration: none;
}

.marquee-content {
  --text-width: 35ch;
  --gap: 2rem;
  --total-width: calc(var(--text-width) + var(--gap));

  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 100%;
  height: 40px;
  white-space: nowrap;
  font-size: 1.5rem;
  font-weight: 1000;
  color: transparent;

  text-shadow:
    calc(var(--total-width) * 0) 0 0 #2563eb,
    calc(var(--total-width) * 1) 0 0 #2563eb,
    calc(var(--total-width) * 2) 0 0 #2563eb,
    calc(var(--total-width) * 3) 0 0 #2563eb,
    calc(var(--total-width) * 4) 0 0 #2563eb;

  animation: marquee 10s linear infinite;
}

.marquee-link {
  text-decoration: none;
  white-space: nowrap;
}

@keyframes marquee {
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(calc(-1 * var(--total-width)));
  }
}

@media (max-width: 640px) {
  .marquee-content {
    --text-width: 35ch;
    --gap: 1rem;
  }
}
</style>
