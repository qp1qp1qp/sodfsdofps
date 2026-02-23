<script setup>
import { ref, onMounted, computed, inject } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getProductByCustomUrl, getProductTypeBySlug } from '../api'
import Footer from '../components/Footer.vue'
import { ShoppingCart, Truck, CreditCard, Plus, Minus } from 'lucide-vue-next'

const route = useRoute()
const router = useRouter()
const product = ref(null)
const productType = ref(null)
const activeTab = ref('payment')
const mainImage = ref('')
const quantity = ref(1)
const buttonPressed = ref(false)
const showTabContent = ref(true)

const text = ref('Качественные материалы для вашего строительства - Быстрая доставка - Выгодные цены - Гарантия качества')

// Данные о видах доставки
const deliveryTypes = [
  {
    name: 'Самовывоз',
    description: 'Самый экономичный вариант. Вы можете забрать товар самостоятельно из нашего склада в удобное для вас время.',
    icon: 'box'
  },
  {
    name: 'Газель до 1.5 т.',
    description: 'Идеально подходит для небольших заказов: доски от 0.01 м³ до 2 м³ или других товаров до 1.5 т.',
    icon: 'truck-small'
  },
  {
    name: 'Манипулятор до 6 т.',
    description: 'Оптимально для средних заказов: доски от 2 м³ до 6 м³ или других товаров от 1.5 т. до 6 т.',
    icon: 'truck-medium'
  },
  {
    name: 'КАМАЗ до 10 т.',
    description: 'Для крупных заказов: доски от 6 м³ до 10 м³ или других товаров более 6 т.',
    icon: 'truck-large'
  }
]

// Данные о способах оплаты
const paymentMethods = [
  {
    name: 'Оплата картой в офисе',
    description: 'Принимаем банковские карты Visa, MasterCard, МИР. Возможна оплата с корпоративных счетов.'
  },
  {
    name: 'Наличные',
    description: 'Оплата наличными доступна при самовывозе или при получении заказа.'
  },
  {
    name: 'Безналичный расчет',
    description: 'Для юридических лиц доступна оплата по счету. Предоставляем все необходимые закрывающие документы.'
  }
]

const { cart, addToCart } = inject('cart')

const addProductToCart = () => {
  if (product.value) {
    // Создаем объект товара с правильной ценой (всегда за штуку)
    const productToAdd = {
      ...product.value,
      quantity: quantity.value,
      // Используем цену за штуку (price_per_unit) вместо базовой цены (price)
      price: product.value.price_per_unit
    };
    
    addToCart(productToAdd);
  }
}

const fetchProduct = async () => {
  try {
    const { typeSlug, productSlug } = route.params
    const typeResponse = await getProductTypeBySlug(typeSlug)
    productType.value = typeResponse.data
    const response = await getProductByCustomUrl(productSlug)
    product.value = response.data
    if (product.value.product_type.slug !== productType.value.slug) {
      router.push('/404')
    }
    // Set the main image to the first image in the array or the default imageUrl
    mainImage.value =
      product.value.images.length > 0
        ? getFullImageUrl(product.value.images[0].image)
        : getFullImageUrl(product.value.imageUrl)
  } catch (error) {
    console.error('Error fetching product:', error)
    router.push('/404')
  }
}

const incrementQuantity = () => {
  quantity.value++
}

const decrementQuantity = () => {
  if (quantity.value > 1) {
    quantity.value--
  }
}

const formatPrice = (price) => {
  return new Intl.NumberFormat('ru-RU').format(price)
}

const setMainImage = (imageUrl) => {
  mainImage.value = getFullImageUrl(imageUrl)
}

const sortedImages = computed(() => {
  return product.value ? [...product.value.images].sort((a, b) => a.order - b.order) : []
})

const getFullImageUrl = (imageUrl) => {
  if (imageUrl && !imageUrl.startsWith('http')) {
    const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/api\/?$/, '');
    return `${baseUrl}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`
  }
  return imageUrl
}

const secondaryPrice = computed(() => {
  if (!product.value) return null;
  
  // Если основная единица измерения - не штука, то вторичная цена не нужна
  // так как она будет показана в отдельном условии для price_per_unit
  if (product.value.primary_unit !== 'piece') {
    return null;
  }
  
  // Для штучных товаров показываем цену за единицу (кубы, квадраты или погонные метры)
  // в зависимости от того, какие данные доступны
  if (product.value.volume_per_unit && product.value.price_per_cubic_meter) {
    return { 
      value: product.value.price_per_cubic_meter, 
      unit: 'м³', 
      label: 'за кубический метр' 
    };
  } else if (product.value.area_per_unit && product.value.price_per_square_meter) {
    return { 
      value: product.value.price_per_square_meter, 
      unit: 'м²', 
      label: 'за квадратный метр' 
    };
  } else if (product.value.linear_meters_per_unit && product.value.price_per_linear_meter) {
    return { 
      value: product.value.price_per_linear_meter, 
      unit: 'п.м', 
      label: 'за погонный метр' 
    };
  }
  return null;
})

// Получить основную цену и её метку
const primaryPrice = computed(() => {
  if (!product.value) return { value: 0, unit: 'шт.', label: 'за штуку' };
  
  switch (product.value.primary_unit) {
    case 'cubic':
      return { 
        value: product.value.price, 
        unit: 'м³', 
        label: 'за кубический метр' 
      };
    case 'square':
      return { 
        value: product.value.price, 
        unit: 'м²', 
        label: 'за квадратный метр' 
      };
    case 'linear':
      return { 
        value: product.value.price, 
        unit: 'п.м', 
        label: 'за погонный метр' 
      };
    case 'piece':
    default:
      return { 
        value: product.value.price_per_unit, 
        unit: 'шт.', 
        label: 'за штуку' 
      };
  }
})

// Получить отображаемую единицу измерения
const unitValueDisplay = computed(() => {
  if (!product.value || !product.value.unit_value) return null;
  
  return {
    value: product.value.unit_value,
    unit: product.value.unit_label || ''
  };
})

// Функция для переключения вкладок с возможностью сворачивания
const toggleTab = (tab) => {
  if (activeTab.value === tab) {
    showTabContent.value = !showTabContent.value
  } else {
    activeTab.value = tab
    showTabContent.value = true
  }
}

// Добавим вычисляемые свойства для правильного отображения цен
const getPrimaryUnitLabel = computed(() => {
  if (!product.value) return '';
  
  switch (product.value.primary_unit) {
    case 'cubic':
      return 'м³';
    case 'square':
      return 'м²';
    case 'linear':
      return 'пог. м';
    case 'piece':
    default:
      return 'шт';
  }
});

const getSecondaryUnitLabel = computed(() => {
  if (!product.value) return '';
  return 'шт';
});

const getPrimaryPrice = computed(() => {
  if (!product.value) return 0;
  
  switch (product.value.primary_unit) {
    case 'cubic':
      return product.value.price_per_cubic_meter;
    case 'square':
      return product.value.price_per_square_meter;
    case 'linear':
      return product.value.price_per_linear_meter;
    case 'piece':
    default:
      return product.value.price_per_unit;
  }
});

onMounted(fetchProduct)
</script>

<template>
  <div class="main-container bg-gray-100 dark:bg-gray-900">
    <div class="content pt-20 sm:pt-24">
      <div class="marquee">
        <div class="marquee-container">
          <!-- Первая копия текста -->
          <div class="marquee-content">
            <span class="marquee-text">{{ text }}</span>
            <span class="marquee-text">{{ text }}</span>
            <span class="marquee-text">{{ text }}</span>
          </div>
          
          <!-- Вторая копия текста для плавного перехода -->
          <div class="marquee-content marquee-content-second">
            <span class="marquee-text">{{ text }}</span>
            <span class="marquee-text">{{ text }}</span>
            <span class="marquee-text">{{ text }}</span>
          </div>
        </div>
      </div>
      <div class="container mx-auto px-4 py-8 max-w-full">
        <div
          v-if="product"
          class="product-page bg-white dark:bg-gray-800 shadow-lg rounded-lg overflow-hidden"
        >
          <div class="product-content flex flex-col lg:flex-row">
            <div class="product-images lg:w-1/2 p-6 flex flex-row">
              <div class="thumbnails flex flex-col space-y-2 w-1/5">
                <img
                  v-for="image in sortedImages"
                  :key="image.id"
                  :src="getFullImageUrl(image.image)"
                  :alt="`${product.title} - изображение ${image.order}`"
                  class="w-full h-20 object-cover rounded cursor-pointer border dark:border-gray-700 hover:border-indigo-500 transition-transform transform hover:scale-105 hover:opacity-90"
                  @click="setMainImage(image.image)"
                />
              </div>

              <div
                class="main-image flex-grow ml-4 border dark:border-gray-700 rounded-lg overflow-hidden"
              >
                <img :src="mainImage" :alt="product.title" class="w-full h-auto object-cover" />
              </div>
            </div>

            <div class="product-info lg:w-1/2 p-6">
              <div class="flex justify-between items-center mb-4">
                <h1 class="text-3xl font-bold text-gray-800 dark:text-white">
                  {{ product.title }}
                </h1>
                <div v-if="product.is_featured" class="featured-label">Новинка</div>
              </div>
              <p class="text-gray-600 dark:text-gray-300 mb-6">{{ product.description }}</p>

              <div class="product-details mb-6 bg-gray-50 dark:bg-gray-700 p-4 rounded-lg">
                <div class="grid grid-cols-2 gap-4">
                  <div class="flex flex-col">
                    <span class="text-sm text-gray-500 dark:text-gray-400">{{ primaryPrice.label }}</span>
                    <span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                      {{ formatPrice(primaryPrice.value) }} ₽/{{ primaryPrice.unit }}
                    </span>
                  </div>
                  <div v-if="product.price_per_unit && product.primary_unit !== 'piece'" class="flex flex-col">
                    <span class="text-sm text-gray-500 dark:text-gray-400">Цена за штуку</span>
                    <span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                      {{ formatPrice(product.price_per_unit) }} ₽/шт.
                    </span>
                  </div>
                  <div v-else-if="secondaryPrice" class="flex flex-col">
                    <span class="text-sm text-gray-500 dark:text-gray-400">Цена {{ secondaryPrice.label }}</span>
                    <span class="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                      {{ formatPrice(secondaryPrice.value) }} ₽/{{ secondaryPrice.unit }}
                    </span>
                  </div>
                  <div class="flex items-center">
                    <span class="text-sm text-gray-500 dark:text-gray-400 mr-2">Статус:</span>
                    <span class="text-green-500 dark:text-green-400 font-semibold">В наличии</span>
                  </div>
                  <div v-if="unitValueDisplay" class="flex items-center">
                    <span class="text-sm text-gray-500 dark:text-gray-400 mr-2">В упаковке:</span>
                    <span class="dark:text-gray-300">{{ unitValueDisplay.value }} {{ unitValueDisplay.unit }}</span>
                  </div>
                </div>
              </div>

              <div class="characteristics mb-6">
                <h3 class="text-xl font-semibold mb-2 text-gray-800 dark:text-white">
                  Характеристики
                </h3>
                <div class="grid grid-cols-2 gap-2">
                  <div
                    v-for="char in product.characteristics"
                    :key="char.name"
                    class="flex items-center py-1 border-b border-gray-200 dark:border-gray-700"
                  >
                    <span class="text-sm font-medium text-gray-600 dark:text-gray-400 mr-2"
                      >{{ char.name }}:</span
                    >
                    <span class="text-sm text-gray-800 dark:text-gray-300">{{ char.value }}</span>
                  </div>
                </div>
              </div>

              <div class="tabs mb-6">
                <div class="flex border-b dark:border-gray-700 overflow-x-auto">
                  <button
                    @click="toggleTab('delivery')"
                    :class="[
                      'px-4 py-2 text-sm font-semibold flex items-center whitespace-nowrap',
                      activeTab === 'delivery'
                        ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400'
                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                    ]"
                  >
                    <span class="w-4 h-4 mr-2">🚚</span>
                    Доставка
                  </button>
                  <button
                    @click="toggleTab('payment')"
                    :class="[
                      'px-4 py-2 text-sm font-semibold flex items-center whitespace-nowrap',
                      activeTab === 'payment'
                        ? 'text-indigo-600 dark:text-indigo-400 border-b-2 border-indigo-600 dark:border-indigo-400'
                        : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                    ]"
                  >
                    <span class="w-4 h-4 mr-2">💳</span>
                    Оплата
                  </button>
                </div>
                <div v-if="showTabContent" class="p-4 bg-gray-50 dark:bg-gray-700 rounded-b-lg">
                  <div v-if="activeTab === 'delivery'">
                    <h4 class="font-semibold text-lg mb-3 dark:text-white">Варианты доставки</h4>
                    <div class="space-y-4">
                      <div v-for="(type, index) in deliveryTypes" :key="index" class="flex">
                        <div class="w-10 h-10 flex-shrink-0 flex items-center justify-center mr-3">
                          <span class="text-xl">{{ type.icon === 'box' ? '📦' : '🚚' }}</span>
                        </div>
                        <div>
                          <h5 class="text-md font-medium text-gray-900 dark:text-white">{{ type.name }}</h5>
                          <p class="text-sm text-gray-600 dark:text-gray-300">{{ type.description }}</p>
                        </div>
                      </div>
                    </div>
                    <div class="mt-4 text-sm text-gray-500 dark:text-gray-400">
                      <p>Стоимость и сроки доставки зависят от объема заказа и удаленности от склада. Уточните детали у наших менеджеров.</p>
                    </div>
                  </div>
                  
                  <div v-if="activeTab === 'payment'">
                    <h4 class="font-semibold text-lg mb-3 dark:text-white">Способы оплаты</h4>
                    <div class="space-y-4">
                      <div v-for="(method, index) in paymentMethods" :key="index">
                        <h5 class="text-md font-medium text-gray-900 dark:text-white">{{ method.name }}</h5>
                        <p class="text-sm text-gray-600 dark:text-gray-300">{{ method.description }}</p>
                      </div>
                    </div>
                    <div class="mt-4 p-3 bg-indigo-50 dark:bg-indigo-900/30 rounded-md">
                      <p class="text-sm text-indigo-700 dark:text-indigo-300 font-medium">⚠️ Обратите внимание: оплата через сайт не принимается.</p>
                    </div>
                  </div>
                </div>
              </div>

              <div
                class="flex flex-col sm:flex-row items-center justify-between mb-6 space-y-4 sm:space-y-0"
              >
                <div
                  class="quantity-selector flex items-center border dark:border-gray-700 rounded-md"
                >
                  <button
                    @click="decrementQuantity"
                    class="p-2 text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400"
                  >
                    <Minus class="w-5 h-5" />
                  </button>
                  <span class="px-4 py-2 text-lg font-semibold dark:text-white">{{
                    quantity
                  }}</span>
                  <button
                    @click="incrementQuantity"
                    class="p-2 text-gray-600 dark:text-gray-400 hover:text-indigo-600 dark:hover:text-indigo-400"
                  >
                    <Plus class="w-5 h-5" />
                  </button>
                </div>
                <button
                  @click="addProductToCart"
                  @mousedown="buttonPressed = true"
                  @mouseup="buttonPressed = false"
                  @mouseleave="buttonPressed = false"
                  :class="[
                    'w-full sm:w-auto sm:flex-grow sm:ml-4 text-white py-3 px-6 rounded-lg font-semibold transition-all duration-150 flex items-center justify-center',
                    buttonPressed
                      ? 'bg-indigo-700 transform scale-95'
                      : 'bg-indigo-600 hover:bg-indigo-700'
                  ]"
                >
                  <ShoppingCart class="w-5 h-5 mr-2" />
                  <span>Добавить в корзину</span>
                </button>
              </div>

              <!-- Далее заменим раздел отображения цен 
              <div class="product-pricing">
                <div v-if="product.primary_unit !== 'piece'" class="flex flex-col">
                  <h3 class="text-xl font-bold">{{ getPrimaryPrice }} ₽ за {{ getPrimaryUnitLabel }}</h3>
                  <h4 class="text-lg mt-2">{{ product.price_per_unit }} ₽ за {{ getSecondaryUnitLabel }}</h4>
                </div>
                <div v-else class="flex flex-col">
                  <h3 class="text-xl font-bold">{{ product.price_per_unit }} ₽ за шт</h3>
                </div>
              </div> -->
            </div>
          </div>
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


.marquee {
  position: relative;
  width: 100%;
  overflow: hidden;
  background: linear-gradient(to right, #4f46e5, #3b82f6);
}

.marquee-container {
  display: flex;
  white-space: nowrap;
  padding: 0.75rem 0;
}

.marquee-content {
  display: inline-block;
  animation: marquee 55s linear infinite;
}

.marquee-content-second {
  position: absolute;
  top: 0.75rem;
  animation: marquee2 55s linear infinite;
}

.marquee-text {
  display: inline-block;
  color: white;
  font-weight: bold;
  margin: 0 70px;
}

@keyframes marquee {
  0% {
    transform: translateX(0%);
  }
  100% {
    transform: translateX(-100%);
  }
}

@keyframes marquee2 {
  0% {
    transform: translateX(100%);
  }
  100% {
    transform: translateX(0%);
  }
}


@media (max-width: 1023px) {
  .product-content {
    flex-direction: column;
  }

  .product-images,
  .product-info {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .product-details .grid,
  .characteristics .grid {
    grid-template-columns: 1fr;
  }

  .tabs button {
    padding: 0.5rem;
  }
}

.featured-label {
  background-color: #f59e0b;
  color: white;
  padding: 7px 12px;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  white-space: nowrap;
}

:root.dark .featured-label {
  background-color: #d97706;
}

@media (max-width: 640px) {
  .product-info h1 {
    font-size: 1.5rem;
  }

  .featured-label {
    font-size: 0.75rem;
    padding: 4px 8px;
  }
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>
