<script setup>
import { ref, onMounted, watch, inject } from 'vue'
import Item from './Item.vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  products: Array,
  images: Array
})

const emit = defineEmits(['addToFavorite', 'addToCart'])

// Получаем доступ к корзине и избранному чтобы отслеживать их изменения
const { cart, favorites } = inject('cart')

const router = useRouter()
const items = ref([])
const localProducts = ref([])
const localImages = ref([])
const hasInitialized = ref(false)

const imageLayouts = [
  { size: '2x2', span: { col: 2, row: 2 }, position: 4 },
  { size: '3x3', span: { col: 3, row: 3 }, position: 12 },
  { size: '2x2', span: { col: 2, row: 2 }, position: 26 },
  { size: '1x2', span: { col: 1, row: 2 }, position: 33 }
]

const shuffleArray = (array) => {
  const newArray = [...array];
  for (let i = newArray.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[newArray[i], newArray[j]] = [newArray[j], newArray[i]]
  }
  return newArray
}

const createItems = async () => {
  console.log('Входные данные для createItems:', { products: props.products, images: props.images })

  if (!hasInitialized.value) {
    if (props.products && props.products.length > 0) {
      // Получаем копию продуктов и сразу проверяем их наличие в корзине и избранном
      localProducts.value = [...props.products].map(product => {
        // Проверяем, находится ли товар в корзине и избранном
        const isInCart = cart.value.some(cartItem => cartItem.id === product.id);
        const isInFavorites = favorites.value.includes(product.id);
        
        return {
          ...product,
          isAdded: isInCart,
          isFavorite: isInFavorites
        };
      });
    }

    if (props.images && props.images.length > 0) {
      localImages.value = [...props.images]
    }
    
    hasInitialized.value = true;
  } else {
    if (props.products && props.products.length > 0) {
      props.products.forEach(newProduct => {
        const existingProduct = localProducts.value.find(p => p.id === newProduct.id);
        if (existingProduct) {
          // Здесь обновляем не только из пропсов, но и проверяем корзину и избранное
          const isInCart = cart.value.some(cartItem => cartItem.id === newProduct.id);
          const isInFavorites = favorites.value.includes(newProduct.id);
          
          existingProduct.isAdded = newProduct.isAdded || isInCart;
          existingProduct.isFavorite = newProduct.isFavorite || isInFavorites;
          existingProduct.quantity = newProduct.quantity;
        }
      });
    }
    
    // Также проверяем все текущие товары на наличие в корзине и избранном
    localProducts.value.forEach(product => {
      const isInCart = cart.value.some(cartItem => cartItem.id === product.id);
      const isInFavorites = favorites.value.includes(product.id);
      
      if (isInCart) {
        product.isAdded = true;
      }
      
      if (isInFavorites) {
        product.isFavorite = true;
      }
    });
  }

  if (items.value.length === 0) {
    const newItems = Array(40).fill(null)
    const shuffledImages = shuffleArray([...localImages.value])
    let productIndex = 0

    imageLayouts.forEach((layout) => {
      if (shuffledImages.length > 0) {
        const imageIndex = Math.floor(Math.random() * shuffledImages.length)
        newItems[layout.position] = {
          type: 'image',
          src: shuffledImages[imageIndex],
          size: layout.size,
          span: layout.span
        }
        shuffledImages.splice(imageIndex, 1)
        for (let r = 0; r < layout.span.row; r++) {
          for (let c = 0; c < layout.span.col; c++) {
            if (r !== 0 || c !== 0) {
              newItems[layout.position + r * 4 + c] = 'occupied'
            }
          }
        }
      }
    })

    for (let i = 0; i < 40; i++) {
      if (newItems[i] === null && productIndex < localProducts.value.length) {
        // Проверяем, есть ли товар в корзине и избранном при создании элементов
        const productData = localProducts.value[productIndex];
        const isInCart = cart.value.some(cartItem => cartItem.id === productData.id);
        const isInFavorites = favorites.value.includes(productData.id);
        
        newItems[i] = {
          type: 'product',
          data: {
            ...productData,
            isAdded: productData.isAdded || isInCart, // Убедимся, что isAdded установлен правильно
            isFavorite: productData.isFavorite || isInFavorites // Убедимся, что isFavorite установлен правильно
          }
        }
        productIndex++
      }
    }

    items.value = newItems.filter((item) => item !== null && item !== 'occupied')
  } else {
    items.value.forEach(item => {
      if (item.type === 'product') {
        // Проверяем обновления из props
        const updatedProduct = props.products?.find(p => p.id === item.data.id);
        if (updatedProduct) {
          item.data.isAdded = updatedProduct.isAdded;
          item.data.isFavorite = updatedProduct.isFavorite;
          item.data.quantity = updatedProduct.quantity;
        }
        
        // Также проверяем наличие в корзине и избранном
        const isInCart = cart.value.some(cartItem => cartItem.id === item.data.id);
        const isInFavorites = favorites.value.includes(item.data.id);
        
        if (isInCart) {
          item.data.isAdded = true;
        }
        
        if (isInFavorites) {
          item.data.isFavorite = true;
        }
      }
    });
  }
  
  console.log('Итоговый массив элементов для отображения (с проверкой корзины и избранного):', items.value)
}

const goToAllProducts = () => {
  router.push('/all-products')
}

const onClickFavorite = async (item) => {
      console.log(`BestItemsSlider: Изменение статуса избранного для товара ${item.id}`);
      
      try {
        // Просто вызываем централизованную функцию
        emit('addToFavorite', item); // Это вызовет toggleFavoriteItem в родительском компоненте
        
        // UI обновится через watcher favorites
      } catch (error) {
        console.error('Ошибка при обновлении избранного:', error);
      }
    }

const onClickAdd = (itemData) => {
  console.log('MixedProducts: Adding item to cart:', itemData);
  
  // Update the UI state to show the item as added
  items.value.forEach(item => {
    if (item.type === 'product' && item.data.id === itemData.id) {
      item.data.isAdded = true;
    }
  });
  
  const product = localProducts.value.find(p => p.id === itemData.id);
  if (product) {
    product.isAdded = true;
  }
  
  // Использую emit с правильным именем события, как в AllProducts
  emit('addToCart', itemData);
}

onMounted(() => {
  createItems()
})

watch(() => props.products?.length, (newLength, oldLength) => {
  if (newLength !== oldLength && hasInitialized.value) {
    hasInitialized.value = false;
    items.value = [];
    createItems();
  }
})

watch(() => props.images?.length, (newLength, oldLength) => {
  if (newLength !== oldLength && hasInitialized.value) {
    hasInitialized.value = false;
    items.value = [];
    createItems();
  }
})

// Добавляем слежение за изменениями корзины
watch(cart, () => {
  console.log('Корзина изменилась, обновляем состояние товаров в MixedProducts');
  
  // Обновляем состояние isAdded для всех товаров в компоненте
  items.value.forEach(item => {
    if (item.type === 'product') {
      // Проверяем, есть ли товар в корзине
      const isInCart = cart.value.some(cartItem => cartItem.id === item.data.id);
      item.data.isAdded = isInCart;
    }
  });
  
  // Также обновляем localProducts для синхронизации
  localProducts.value.forEach(product => {
    const isInCart = cart.value.some(cartItem => cartItem.id === product.id);
    product.isAdded = isInCart;
  });
  
  // Очень важное изменение - если кардинально изменилась корзина,
  // возможно нужно полностью обновить товары
  if (hasInitialized.value && items.value.length > 0) {
    // Не перезагружаем полностью, а только проверяем и обновляем
    items.value.forEach(item => {
      if (item.type === 'product') {
        const isInCart = cart.value.some(cartItem => cartItem.id === item.data.id);
        if (isInCart !== item.data.isAdded) {
          item.data.isAdded = isInCart;
          console.log(`Обновлен статус isAdded для товара ${item.data.id} на ${isInCart}`);
        }
      }
    });
  }
}, { deep: true });

// Добавляем слежение за изменениями избранного
watch(favorites, () => {
  console.log('Избранное изменилось, обновляем состояние товаров в MixedProducts');
  
  // Обновляем состояние isFavorite для всех товаров в компоненте
  items.value.forEach(item => {
    if (item.type === 'product') {
      // Проверяем, есть ли товар в избранном
      const isInFavorites = favorites.value.includes(item.data.id);
      if (isInFavorites !== item.data.isFavorite) {
        item.data.isFavorite = isInFavorites;
        console.log(`Обновлен статус избранного для товара ${item.data.id} на ${isInFavorites}`);
      }
    }
  });
  
  // Также обновляем localProducts для синхронизации
  localProducts.value.forEach(product => {
    const isInFavorites = favorites.value.includes(product.id);
    if (isInFavorites !== product.isFavorite) {
      product.isFavorite = isInFavorites;
    }
  });
}, { deep: true });
</script>

<template>
  <div class="mixed-gallery" aria-label="Галерея товаров">
    <div class="gallery-grid">
      <template v-for="(item, index) in items" :key="index">
        <div v-if="item.type === 'image'" :class="['gallery-item', `size-${item.size}`]">
          <div class="image-container">
            <img :src="item.src" :alt="`Gallery image ${index}`" class="gallery-image" />
          </div>
        </div>
        <div v-else-if="item.type === 'product'" class="gallery-item size-product">
          <Item
            :id="item.data.id"
            :title="item.data.title"
            :image-url="item.data.imageUrl"
            :price_per_unit="Number(item.data.price_per_unit)"
            :price_per_cubic_meter="Number(item.data.price_per_cubic_meter)"
            :price_per_square_meter="Number(item.data.price_per_square_meter)"
            :price_per_linear_meter="Number(item.data.price_per_linear_meter)"
            :primary_unit="item.data.primary_unit"
            :unit_value="item.data.unit_value"
            :unit_label="item.data.unit_label"
            :isFavorite="item.data.isFavorite"
            :onClickFavorite="() => onClickFavorite(item.data)"
            :onClickAdd="onClickAdd"
            :isAdded="item.data.isAdded"
            :custom_url="item.data.custom_url"
            :product_type="item.data.product_type"
            :is_available="item.data.is_available"
            :quantity="item.data.quantity"
            :is_featured="item.data.is_featured"
            class="mixed-product"
          />
        </div>
      </template>
    </div>
    <div class="view-more-container">
      <button @click="goToAllProducts" class="view-more-button">Посмотреть все товары</button>
    </div>
  </div>
</template>

<style scoped>
.mixed-gallery {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  box-sizing: border-box;
}

.gallery-grid {
  display: grid;
  gap: 20px;
  grid-template-columns: repeat(4, 1fr);
  grid-auto-rows: 300px; /* Увеличенная высота строки */
}

.gallery-item {
  overflow: hidden;
  border-radius: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
}

.image-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.gallery-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-container:hover .gallery-image {
  transform: scale(1.05);
}

.size-2x2 {
  grid-column: span 2;
  grid-row: span 2;
}

.size-3x3 {
  grid-column: span 3;
  grid-row: span 3;
}

.size-1x2 {
  grid-column: span 1;
  grid-row: span 2;
}

.size-product {
  grid-column: span 1;
  grid-row: span 1;
  display: flex;
  min-width: 0;
}

.size-product > :deep(.item-container) {
  width: 100%;
  height: 100%;
}

.size-product > :deep(.product-info) {
  overflow: hidden;
}

.view-more-container {
  display: flex;
  justify-content: center;
  margin-top: 40px;
}

.view-more-button {
  background-color: #4caf50;
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.view-more-button:hover {
  background-color: #45a049;
}

/* Адаптивные стили */
@media (max-width: 1200px) {
  .gallery-grid {
    grid-template-columns: repeat(3, 1fr);
    grid-auto-rows: 350px; /* Увеличенная высота строки для средних экранов */
  }

  .size-3x3 {
    grid-column: span 2;
    grid-row: span 2;
  }
}

@media (max-width: 900px) {
  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
    grid-auto-rows: 400px; /* Увеличенная высота строки для маленьких экранов */
  }

  .size-2x2,
  .size-3x3 {
    grid-column: span 2;
    grid-row: span 2;
  }

  .size-1x2 {
    grid-column: span 1;
    grid-row: span 1;
  }
}

@media (max-width: 600px) {
  .gallery-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
    grid-auto-rows: 300px; /* Уменьшенная высота строки для мобильных устройств */
  }

  .size-2x2,
  .size-3x3,
  .size-1x2 {
    grid-column: span 2;
    grid-row: span 1;
  }
}

@media (max-width: 440px) {
  .gallery-grid {
    grid-template-columns: 1fr;
  }

  .size-2x2,
  .size-3x3,
  .size-1x2,
  .size-product {
    grid-column: span 1;
  }

  .view-more-button {
    width: 100%;
  }
}
.featured-label {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: #f59e0b;
  color: white;
  padding: 4px 8px;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  z-index: 9;
}

:root.dark .featured-label {
  background-color: #d97706;
}
</style>
