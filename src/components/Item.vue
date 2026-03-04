<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  id: Number,
  title: String,
  imageUrl: String,
  price_per_unit: Number,
  volume_per_unit: { type: Number, default: 0 },
  price_per_cubic_meter: Number,
  price_per_square_meter: Number,
  price_per_linear_meter: Number,
  primary_unit: {
    type: String,
    default: 'piece'
  },
  unit_value: Number,
  unit_label: String,
  isFavorite: Boolean,
  isAdded: Boolean,
  onClickFavorite: Function,
  onClickAdd: Function,
  custom_url: String,
  product_type: Object,
  is_available: Boolean,
  quantity: Number,
  is_featured: {
    type: Boolean,
    default: false
  }
})

const localQuantity = ref(1)

const fullImageUrl = computed(() => {
  if (props.imageUrl) {
    if (props.imageUrl.startsWith('http')) return props.imageUrl;
    const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/api\/?$/, '');
    return `${baseUrl}${props.imageUrl.startsWith('/') ? '' : '/'}${props.imageUrl}`;
  }
  return ''
})

const hasData = computed(() => {
  const result =
    props.id &&
    props.title &&
    props.imageUrl &&
    props.price_per_unit !== undefined &&
    props.price_per_cubic_meter !== undefined
  console.log(`Item ${props.id}: Has all required data: ${result}`)
  return result
})

const goToProductPage = () => {
  if (props.product_type && props.product_type.slug && props.custom_url) {
    router.push({
      name: 'ProductPage',
      params: {
        typeSlug: props.product_type.slug,
        productSlug: props.custom_url
      }
    })
  } else {
    console.error(`Custom URL or product type is not defined for product with id ${props.id}`)
  }
}

const incrementQuantity = () => {
  if (localQuantity.value < props.quantity) {
    localQuantity.value++
    console.log(`Item ${props.id}: Количество увеличено до ${localQuantity.value}`)
  }
}

const decrementQuantity = () => {
  if (localQuantity.value > 1) {
    localQuantity.value--
    console.log(`Item ${props.id}: Количество уменьшено до ${localQuantity.value}`)
  }
}

const addToCart = (e) => {
  // Make sure to stop propagation to prevent the event from bubbling up
  e.stopPropagation()
  
  console.log(`Item ${props.id}: Добавление в корзину. Количество: ${localQuantity.value}`)
  
  // Create a new object with the exact properties needed for the cart
  const itemToAdd = {
    id: props.id,
    title: props.title,
    imageUrl: props.imageUrl,
    volume_per_unit: props.volume_per_unit,
    price_per_unit: props.price_per_unit, // Original price per unit
    price_per_cubic_meter: props.price_per_cubic_meter,
    price_per_linear_meter: props.price_per_linear_meter,
    isFavorite: props.isFavorite,
    isAdded: true,
    custom_url: props.custom_url,
    product_type: props.product_type,
    is_available: props.is_available,
    is_featured: props.is_featured,
    quantity: localQuantity.value, // Selected quantity
    price: props.price_per_unit // Original price for calculation
  }
  
  // Pass the complete item data with correct quantity
  props.onClickAdd(itemToAdd)
  
  // Reset quantity after adding
  localQuantity.value = 1
}

const maxQuantityReached = computed(() => localQuantity.value >= props.quantity)

const getPriceDisplay = () => {
  const formatNumber = (num) => {
    if (num === null || num === undefined) return '';
    return new Intl.NumberFormat('ru-RU').format(num);
  };

  // Определяем первичную цену (за основную единицу)
  let primaryPrice = 0;
  let primaryUnit = 'шт.';
  
  switch (props.primary_unit) {
    case 'cubic':
      primaryPrice = props.price_per_cubic_meter;
      primaryUnit = 'м³';
      break;
    case 'square':
      primaryPrice = props.price_per_square_meter;
      primaryUnit = 'м²';
      break;
    case 'linear':
      primaryPrice = props.price_per_linear_meter;
      primaryUnit = 'п.м';
      break;
    case 'piece':
    default:
      primaryPrice = props.price_per_unit;
      primaryUnit = 'шт.';
  }
  
  // Возвращаем текстовое представление цены
  return `${formatNumber(primaryPrice || 0)} ₽/${primaryUnit}`;
};

const getSecondaryPriceDisplay = () => {
  const formatNumber = (num) => {
    if (num === null || num === undefined) return '';
    return new Intl.NumberFormat('ru-RU').format(num);
  };

  // Если товар измеряется в штуках, но мы знаем цену за м³, м² или п.м
  if (props.primary_unit === 'piece') {
    if (props.price_per_cubic_meter) {
      return `${formatNumber(props.price_per_cubic_meter)} ₽/м³`;
    } else if (props.price_per_square_meter) {
      return `${formatNumber(props.price_per_square_meter)} ₽/м²`;
    } else if (props.price_per_linear_meter) {
      return `${formatNumber(props.price_per_linear_meter)} ₽/п.м`;
    }
  } 
  // Для других типов единиц, показываем цену за штуку
  else {
    // Для квадратных и линейных метров всегда показываем цену за штуку первой
    if (props.primary_unit === 'square' || props.primary_unit === 'linear') {
      return `${formatNumber(props.price_per_unit)} ₽/шт.`;
    }
    
    // Для кубических метров оставляем логику без изменений
    if (props.price_per_unit) {
      return `${formatNumber(props.price_per_unit)} ₽/шт.`;
    }
  }
  
  return '';
};
</script>

<template>
  <div v-if="hasData" class="item-container cursor-pointer" @click="goToProductPage">
    <img
      :src="!isFavorite ? '/like-1.svg' : '/like-2.svg'"
      alt="Like"
      class="favorite-icon"
      @click.stop="onClickFavorite"
    />

    <!-- Изменяем условие на is_featured -->
    <div v-if="is_featured" class="featured-label">Новинка</div>

    <div class="product-image-container">
      <img :src="fullImageUrl" loading="lazy" alt="Product" class="product-image" />
    </div>
    <div class="product-info">
      <h3 class="product-title">{{ title }}</h3>
      <div class="price-container">
        <div class="price-value">{{ getPriceDisplay() }}</div>
        <div v-if="getSecondaryPriceDisplay()" class="secondary-price">{{ getSecondaryPriceDisplay() }}</div>
      </div>

      <div class="product-footer">
        <div
          class="stock-status"
          :class="{ 'in-stock': is_available, 'out-of-stock': !is_available }"
        >
          <!-- Используем разные классы для разных размеров экрана -->
          <span class="full-text">{{ is_available ? 'В наличии' : 'Под заказ' }}</span>
          <span class="short-text">{{ is_available ? 'В нал.' : 'Под зак.' }}</span>
          <span class="tiny-text">{{ is_available ? 'Нал.' : 'Зак.' }}</span>
        </div>
        <div class="qty-controls">
          <button
            @click.stop="decrementQuantity"
            class="qty-btn-minus"
            :disabled="localQuantity === 1"
          >
            -
          </button>
          <span class="qty-value">{{ localQuantity }}</span>
          <button
            @click.stop="incrementQuantity"
            class="qty-btn-plus"
            :disabled="maxQuantityReached"
          >
            +
          </button>
        </div>
        <button
          @click.stop="addToCart"
          class="add-to-cart-btn"
          :class="{ added: isAdded }"
          :disabled="!is_available || props.quantity === 0"
        >
          <span class="full-cart-text">{{ isAdded ? '+' : 'Купить' }}</span>
          <span class="short-cart-text">{{ isAdded ? '+' : 'Купить' }}</span>
          <span class="tiny-cart-text">{{ isAdded ? '+' : '🛒' }}</span>
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.item-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: white;
  border-radius: 20px;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  overflow: hidden;
  position: relative;
}

:root.dark .item-container {
  background-color: #2a2a2a;
  color: #e0e0e0;
}

:root.dark .item-container:hover {
  box-shadow: 0 10px 20px rgba(255, 255, 255, 0.1);
}

.item-container:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.15);
}

.favorite-icon {
  position: absolute;
  top: 10px;
  left: 10px;
  width: 32px;
  height: 32px;
  cursor: pointer;
  z-index: 1;
  /* Добавляем эффект тени для лучшей видимости на белом фоне */
  filter: drop-shadow(0px 0px 2px rgba(0, 0, 0, 0.5));
  transition: transform 0.2s ease;
}

.favorite-icon:hover {
  transform: scale(1.1);
}

.product-image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  aspect-ratio: 1 / 1;
}

.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  padding: 15px;
  display: flex;
  flex-direction: column;
}

.product-title {
  font-size: 1.1rem; /* Увеличенный размер шрифта */
  line-height: 1.4;
  font-weight: bold;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 0.75rem;
  flex-grow: 1;
}

:root.dark .product-title {
  color: #ffffff;
}

.price-container {
  margin-bottom: 0.75rem;
}

.price-value {
  font-size: 1.1rem;
  font-weight: 600;
  color: #4f46e5;
}

.secondary-price {
  font-size: 0.8rem;
  color: #6b7280;
  margin-top: 0.25rem;
}

.stock-status {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 12px;
  display: inline-block;
  flex-shrink: 1; /* Allow shrinking if needed */
  min-width: 0; /* Allow shrinking below content size */
  text-align: center;
  white-space: nowrap;
}

.in-stock {
  background-color: rgba(52, 211, 153, 0.1);
  color: #059669;
}

:root.dark .in-stock {
  background-color: rgba(52, 211, 153, 0.2);
  color: #34d399;
}

:root.dark .out-of-stock {
  background-color: rgba(248, 113, 113, 0.2);
  color: #f87171;
}

.out-of-stock {
  background-color: rgba(248, 113, 113, 0.1);
  color: #dc2626;
}

.product-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  flex-wrap: nowrap;
  gap: 4px; /* Add consistent gap */
}

/* Настройка текста для разных размеров экрана */
.short-text, .tiny-text, .short-cart-text, .tiny-cart-text {
  display: none;
}

/* Кнопки и элементы управления количеством */
.qty-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 2px;
  flex-shrink: 0; /* Prevent shrinking */
}

.qty-btn-minus, .qty-btn-plus {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 14px;
  border: none;
  cursor: pointer;
  flex-shrink: 0; /* Prevent shrinking */
  /* Явное указание цвета текста */
  color: #000;
}

.qty-btn-minus {
  background-color: #f3f4f6;
}

.qty-btn-plus {
  background-color: #4f46e5;
  color: white; /* Белый текст для плюса остается в любой теме */
}

/* Стили для темной темы */
:root.dark .qty-btn-minus {
  background-color: #374151;
  color: #fff;
}

:root.dark .qty-value {
  color: #fff;
}

.qty-value {
  margin: 0 2px;
  font-size: 14px;
  font-weight: 500;
}

.add-to-cart-btn {
  background-color: #4f46e5;
  color: white;
  padding: 6px 10px;
  border-radius: 9999px;
  font-weight: 600;
  font-size: 0.875rem;
  transition: background-color 0.3s;
  white-space: nowrap;
  flex-shrink: 0; /* Prevent shrinking */
  min-width: 70px; /* Ensure button has enough width */
  text-align: center;
}

.add-to-cart-btn:hover {
  background-color: #5a67d8;
}

.add-to-cart-btn.added {
  background-color: #10b981;
}

.add-to-cart-btn.added:hover {
  background-color: #059669;
}

.add-to-cart-btn:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
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

/* Медиазапросы для адаптивного отображения текста */
/* Default - show full text for everything */
.full-text, .full-cart-text {
  display: inline;
}
.short-text, .tiny-text, .short-cart-text, .tiny-cart-text {
  display: none;
}

/* ===== Block 1 - товары по акции (featured-products-slider) ===== */
/* 2 items (480-689px) - abbreviated text AND icon button */
@media (min-width: 480px) and (max-width:  518px) {
  .featured-products-slider .item-container .full-text {
    display: none;
  }
  .featured-products-slider .item-container .tiny-text {
    display: inline;
  }
  .featured-products-slider .item-container .full-cart-text,
  .featured-products-slider .item-container .short-cart-text {
    display: none;
  }
  .featured-products-slider .item-container .tiny-cart-text {
    display: inline;
  }
  .featured-products-slider .item-container .add-to-cart-btn {
    min-width: 32px;
    padding: 6px 8px;
  }
}
@media (min-width: 518px) and (max-width:  689px) {
  .featured-products-slider .item-container .full-text {
    display: none;
  }
  .featured-products-slider .item-container .short-text {
    display: inline;
  }
  .featured-products-slider .item-container .full-cart-text,
  .featured-products-slider .item-container .short-cart-text {
    display: none;
  }
  .featured-products-slider .item-container .tiny-cart-text {
    display: inline;
  }
  .featured-products-slider .item-container .add-to-cart-btn {
    min-width: 32px;
    padding: 6px 8px;
  }
}



/* 3 items (768-949px) - abbreviated text */
@media (min-width: 768px) and (max-width: 799px) {
  .featured-products-slider .item-container .full-text {
    display: none;
  }
  .featured-products-slider .item-container .tiny-text {
    display: inline;
  }
}
@media (min-width: 799px) and (max-width: 949px) {
  .featured-products-slider .item-container .full-text {
    display: none;
  }
  .featured-products-slider .item-container .short-text {
    display: inline;
  }
}


/* 4 items (1024-1162px) - abbreviated text */
@media (min-width: 1024px) and (max-width: 1162px) {
  .featured-products-slider .item-container .full-text {
    display: none;
  }
  .featured-products-slider .item-container .short-text {
    display: inline;
  }
  /* For 4 items, we also need icon buttons */
  .featured-products-slider .item-container .full-cart-text,
  .featured-products-slider .item-container .short-cart-text {
    display: none;
  }
  .featured-products-slider .item-container .tiny-cart-text {
    display: inline;
  }
  .featured-products-slider .item-container .add-to-cart-btn {
    min-width: 32px;
    padding: 6px 8px;
  }
}

/* 5 items (1280-1479px) - abbreviated */
@media (min-width: 1280px) and (max-width: 1479px) {
  .featured-products-slider .item-container .full-text {
    display: none;
  }
  .featured-products-slider .item-container .short-text {
    display: inline;
  }
}

/* ===== Block 2 - наши товары (regular-products-grid) ===== */
/* 2 items (441-689px) - abbreviated text AND icon button */
@media (min-width: 491px) and (max-width: 689px) {
  .regular-products-grid .item-container .full-text,
  .mixed-product .full-text {
    display: none;
  }
  .regular-products-grid .item-container .short-text,
  .mixed-product .short-text {
    display: inline;
  }
  .regular-products-grid .item-container .full-cart-text,
  .regular-products-grid .item-container .short-cart-text,
  .mixed-product .full-cart-text,
  .mixed-product .short-cart-text {
    display: none;
  }
  .regular-products-grid .item-container .tiny-cart-text,
  .mixed-product .tiny-cart-text {
    display: inline;
  }
  .regular-products-grid .item-container .add-to-cart-btn,
  .mixed-product .add-to-cart-btn {
    min-width: 32px;
    padding: 6px 8px;
  }
}

@media (min-width: 440px) and (max-width: 491px) {
  .regular-products-grid .item-container .full-text,
  .mixed-product .full-text {
    display: none;
  }
  .regular-products-grid .item-container .short-text,
  .mixed-product .tiny-text {
    display: inline;
  }
  .regular-products-grid .item-container .full-cart-text,
  .regular-products-grid .item-container .short-cart-text,
  .mixed-product .full-cart-text,
  .mixed-product .short-cart-text {
    display: none;
  }
  .regular-products-grid .item-container .tiny-cart-text,
  .mixed-product .tiny-cart-text {
    display: inline;
  }
  .regular-products-grid .item-container .add-to-cart-btn,
  .mixed-product .add-to-cart-btn {
    min-width: 32px;
    padding: 6px 8px;
  }
}


/* ===== Both blocks - small screen adjustments ===== */
/* Very small screens - both blocks use tiny cart button */
@media (max-width: 374px) {
  .full-cart-text, .short-cart-text {
    display: none;
  }
  .tiny-cart-text {
    display: inline;
  }
  .add-to-cart-btn {
    padding: 6px 8px;
    min-width: 32px;
  }
}

/* Extremely small screens - use tiny text for everything */
@media (max-width: 374px) {
  .full-text, .short-text {
    display: none;
  }
  .tiny-text {
    display: inline;
  }
  .stock-status {
    padding: 4px;
    min-width: 36px;
    text-align: center;
  }
  .qty-controls {
    margin: 0 2px;
  }
  .qty-btn-minus, .qty-btn-plus {
    width: 20px;
    height: 20px;
    font-size: 12px;
  }
  .qty-value {
    margin: 0 2px;
    font-size: 12px;
  }
}

/* ===== Специальный запрос для страниц "Новые продукты" и "Все продукты" ===== */
@media (min-width: 379px) and (max-width: 439px) {
  .all-products-list .item-container .full-text,
  .product-items-list .item-container .full-text {
    display: none;
  }
  
  .all-products-list .item-container .tiny-text,
  .product-items-list .item-container .tiny-text {
    display: inline;
  }
  
  .all-products-list .item-container .full-cart-text,
  .all-products-list .item-container .short-cart-text,
  .product-items-list .item-container .full-cart-text,
  .product-items-list .item-container .short-cart-text {
    display: none;
  }
  
  .all-products-list .item-container .tiny-cart-text,
  .product-items-list .item-container .tiny-cart-text {
    display: inline;
  }
  
  .all-products-list .item-container .add-to-cart-btn,
  .product-items-list .item-container .add-to-cart-btn {
    min-width: 32px;
    padding: 6px 8px;
  }
}
</style>
