<script setup>
import { ref, onMounted, inject, watch } from 'vue'
import {
  getProducts,
  getFavorites,
  getProductTypes,
  getCharacteristics
} from '../api'
import { useFavoriteSync } from '../composables/useFavoriteSync'
import ItemList from '../components/ItemList.vue'
import Footer from '../components/Footer.vue'
import debounce from 'lodash.debounce'
import { useRoute, useRouter } from 'vue-router'
import { useHead } from '@vueuse/head'

const route = useRoute()
const router = useRouter()
const { cart, addToCart, updateFavorites, toggleFavoriteItem, favorites } = inject('cart')

const items = ref([])
const productTypes = ref([])
const selectedType = ref(null)
const filters = ref({
  sortBy: 'title',
  searchQuery: ''
})

let lastParams = null

const characteristics = ref([])
const selectedCharacteristics = ref({})
const openCharacteristic = ref(null)

useHead({
  title: 'Каталог продукции | WoodDon',
  meta: [
    {
      name: 'description',
      content:
        'Широкий выбор пиломатериалов и стройматериалов в нашем каталоге. Качественные товары по доступным ценам.'
    },
    {
      name: 'keywords',
      content: 'пиломатериалы, стройматериалы, каталог, доска обрезная, брус, Ростов-на-Дону'
    }
  ]
})

const fetchProductTypes = async () => {
  try {
    const response = await getProductTypes()
    productTypes.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (err) {
    console.error('Ошибка при загрузке типов товаров:', err)
  }
}

const updateSelectedType = () => {
  selectedType.value = route.params.typeSlug || null
}

const fetchCharacteristics = async () => {
  try {
    const params = {
      product_type: selectedType.value,
      title: filters.value.searchQuery,
      ...selectedCharacteristics.value
    }
    const response = await getCharacteristics(params)
    characteristics.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (err) {
    console.error('Ошибка при загрузке характеристик:', err)
  }
}

const fetchItems = async () => {
  try {
    const params = {
      sortBy: filters.value.sortBy,
      title: filters.value.searchQuery ? filters.value.searchQuery : undefined,
      product_type: route.params.typeSlug,
      ...Object.entries(selectedCharacteristics.value).reduce((acc, [key, value]) => {
        acc[`characteristic_${key}`] = value
        return acc
      }, {})
    }

    // Проверяем, изменились ли параметры с последнего запроса
    if (JSON.stringify(params) === JSON.stringify(lastParams)) {
      console.log('Skipping request with same params')
      return
    }

    lastParams = params
    console.log('Fetching items with params:', params)

    const [itemsResponse, favoritesResponse] = await Promise.all([
      getProducts(params),
      getFavorites()
    ])

    const itemsData = Array.isArray(itemsResponse.data) ? itemsResponse.data : itemsResponse.data.results || []
    const favoritesData = favoritesResponse.data

    items.value = itemsData.map((obj) => ({
      ...obj,
      price_per_unit: Number(obj.price_per_unit),
      price_per_cubic_meter: Number(obj.price_per_cubic_meter),
      estimated_volume: Number(obj.estimated_volume) || 0,
      quantity: Number(obj.quantity) || 0,
      isFavorite: favoritesData.some((fav) => fav.product.id === obj.id),
      isAdded: cart.value.some((cartItem) => cartItem.id === obj.id)
    }))

    await fetchCharacteristics()
  } catch (err) {
    console.error('Ошибка при загрузке данных:', err)
  }
}



const selectType = (typeSlug) => {
  if (selectedType.value !== typeSlug) {
    router.push({ path: `/all-products/${typeSlug}` })
  }
}

const showAllProducts = () => {
  router.push({ path: '/all-products' })
}

const resetCharacteristic = (characteristicId) => {
  delete selectedCharacteristics.value[characteristicId]
  fetchItems()
}

const toggleCharacteristic = (characteristicId) => {
  if (openCharacteristic.value === characteristicId) {
    openCharacteristic.value = null
  } else {
    openCharacteristic.value = characteristicId
  }
}

const selectCharacteristic = (characteristicId, value) => {
  if (selectedCharacteristics.value[characteristicId] === value) {
    delete selectedCharacteristics.value[characteristicId]
  } else {
    selectedCharacteristics.value[characteristicId] = value
  }
  openCharacteristic.value = null
  fetchItems()
}

const addToFavorite = async (item) => {
  try {
    console.log('AllProducts.vue: Изменение статуса избранного для товара', item.id);
    
    // Вызываем централизованную функцию
    const success = await toggleFavoriteItem(item);
    
    if (success) {
      // Явно обновляем UI для этого конкретного товара
      const updatedItem = items.value.find(i => i.id === item.id);
      if (updatedItem) {
        // Устанавливаем точное значение из глобального состояния
        updatedItem.isFavorite = favorites.value.includes(item.id);
        console.log(`AllProducts.vue: Обновлен статус избранного для товара ${item.id} на ${updatedItem.isFavorite}`);
      }
    }
  } catch (err) {
    console.error('Ошибка при обновлении избранного:', err);
  }
}

useFavoriteSync(items, favorites)

onMounted(async () => {
  selectedType.value = route.params.typeSlug || null

  await fetchProductTypes()
  await Promise.all([
    fetchItems(),
    fetchCharacteristics()
  ])
  await updateFavorites()

  items.value = items.value.map(item => ({
    ...item,
    isFavorite: favorites.value.includes(item.id)
  }))
})

const onClickAdd = (itemData) => {
  console.log(
    `AllProducts.vue: Добавление в корзину. ID: ${itemData.id}, Название: ${itemData.title}, Количество: ${itemData.quantity}, Цена за единицу: ${itemData.price_per_unit}`
  )
  addToCart(itemData)
}

const onChangeSelect = (event) => {
  filters.value.sortBy = event.target.value
  fetchItems()
}

const onChangeSearchInput = debounce((event) => {
  filters.value.searchQuery = event.target.value
  fetchItems()
}, 300)


watch(() => route.params.typeSlug, async (newSlug) => {
  selectedType.value = newSlug || null
  lastParams = null
  await Promise.all([fetchItems(), fetchCharacteristics()])
})

watch(
  cart,
  () => {
    items.value = items.value.map((item) => ({
      ...item,
      isAdded: cart.value.some((cartItem) => cartItem.id === item.id)
    }))
  },
  { deep: true }
)
</script>

<template>
  <div class="main-container">
    <div class="content pt-20 sm:pt-24">
      <div class="container mx-auto px-2 xs:px-3 sm:px-4 py-4 sm:py-8 max-w-full xl:max-w-[1920px]">
        <!-- Типы товаров -->
        <div class="flex flex-wrap justify-center gap-2 mb-6">
          <button
            @click="showAllProducts"
            :class="[
              'px-4 py-2 rounded-2xl',
              selectedType === null
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            ]"
          >
            Все товары
          </button>
          <button
            v-for="type in productTypes"
            :key="type.id"
            @click="selectType(type.slug)"
            :class="[
              'px-4 py-2 rounded-2xl',
              selectedType === type.slug
                ? 'bg-blue-500 text-white'
                : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
            ]"
          >
            {{ type.name }}
          </button>
        </div>

        <!-- Характеристики -->
        <div class="flex flex-wrap justify-center gap-2 mb-6">
          <div v-for="characteristic in characteristics" :key="characteristic.id" class="relative">
            <button
              @click="toggleCharacteristic(characteristic.id)"
              class="px-4 py-2 rounded-2xl bg-gray-200 text-gray-700 hover:bg-gray-300 focus:outline-none flex items-center"
            >
              {{ characteristic.name }}
              <span v-if="selectedCharacteristics[characteristic.id]" class="ml-2">
                : {{ selectedCharacteristics[characteristic.id] }}
              </span>
              <span
                v-if="selectedCharacteristics[characteristic.id]"
                @click.stop="resetCharacteristic(characteristic.id)"
                class="ml-2 text-red-500 hover:text-red-700 cursor-pointer"
              >
                ✕
              </span>
              <span class="ml-2">▼</span>
            </button>
            <div
              v-if="openCharacteristic === characteristic.id"
              class="absolute z-50 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg"
            >
              <button
                v-for="value in characteristic.values"
                :key="value.id"
                @click="selectCharacteristic(characteristic.id, value.value)"
                class="block w-full text-left px-4 py-2 hover:bg-gray-100 flex justify-between items-center"
                :class="{
                  'bg-blue-100': selectedCharacteristics[characteristic.id] === value.value
                }"
              >
                <span>{{ value.value }}</span>
                <span class="text-sm text-gray-500">({{ value.product_count }})</span>
              </button>
            </div>
          </div>
        </div>

        <div class="flex flex-col sm:flex-row justify-between items-center mb-6">
          <div class="flex flex-col sm:flex-row gap-4 w-full sm:w-auto mb-4 sm:mb-0">
            <select
              @change="onChangeSelect"
              class="py-2 px-3 border rounded-md outline-none dark:bg-gray-700 dark:text-white w-full sm:w-auto"
            >
              <option value="title">Название</option>
              <option value="price">Цена (по возрастанию)</option>
              <option value="-price">Цена (по убыванию)</option>
            </select>

            <div class="relative w-full sm:w-auto">
              <img class="absolute left-4 top-3" src="/search.svg" alt="Search" />
              <input
                @input="onChangeSearchInput"
                class="border rounded-md py-2 pl-11 pr-4 outline-none focus:border-gray-400 dark:bg-gray-700 dark:text-white w-full"
                placeholder="Поиск..."
              />
            </div>
          </div>
        </div>

        <ItemList :items="items" @add-to-favorite="addToFavorite" @addToCart="onClickAdd" />
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
