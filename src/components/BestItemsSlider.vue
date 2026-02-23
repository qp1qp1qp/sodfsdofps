<script>
import { ref, onMounted, watch, nextTick, onBeforeUnmount, inject } from 'vue'
import KeenSlider from 'keen-slider'
import 'keen-slider/keen-slider.min.css'
import Item from './Item.vue'

export default {
  components: { Item },
  props: {
    bestItems: {
      type: Array,
      required: true
    }
  },
  emits: ['addToCart', 'addToFavorite'],
  setup(props, { emit }) {
    const isLoading = ref(true)
    const visibleItems = ref([])
    const sliderRef = ref(null)
    const sliderInstance = ref(null)
    
    // Получаем доступ к массиву избранного и корзине
    const { cart, favorites, updateFavorites } = inject('cart')
    
    // Функция для проверки, находится ли товар в избранном
    const isProductInFavorites = (productId) => {
      // Проверяем массив favorites, который может быть массивом идентификаторов
      if (Array.isArray(favorites.value)) {
        return favorites.value.includes(productId);
      }
      return false;
    }
    
    // Функция для обновления статуса избранного всех товаров
    const updateFavoritesStatus = () => {
      if (!visibleItems.value.length) return;
      
      console.log('Обновляем статусы избранного в BestItemsSlider');
      let changed = false;
      
      visibleItems.value.forEach(item => {
        const shouldBeFavorite = isProductInFavorites(item.id);
        if (item.isFavorite !== shouldBeFavorite) {
          item.isFavorite = shouldBeFavorite;
          changed = true;
          console.log(`BestItemsSlider: Обновлен статус избранного для товара ${item.id} на ${shouldBeFavorite}`);
        }
      });
      
      return changed;
    }

    const updateVisibleItems = async () => {
      isLoading.value = true
      
      const newItems = props.bestItems.filter((item) => item.is_featured)
      
      const itemsChanged = newItems.length !== visibleItems.value.length || 
        newItems.some((newItem, index) => {
          const oldItem = visibleItems.value[index]
          return !oldItem || 
            newItem.id !== oldItem.id || 
            newItem.price_per_unit !== oldItem.price_per_unit ||
            newItem.is_featured !== oldItem.is_featured
        })
      
      if (itemsChanged) {
        // Проверяем все товары на наличие в избранном и корзине
        visibleItems.value = newItems.map(item => {
          // Проверяем наличие в избранном и корзине
          const isInFavorites = isProductInFavorites(item.id);
          const isInCart = cart.value.some(cartItem => cartItem.id === item.id);
          
          return {
            ...item,
            isFavorite: isInFavorites,
            isAdded: isInCart || item.isAdded
          };
        });
      } else {
        visibleItems.value.forEach((item, index) => {
          if (index < newItems.length) {
            // Проверяем наличие в избранном и корзине
            const isInFavorites = isProductInFavorites(item.id);
            const isInCart = cart.value.some(cartItem => cartItem.id === item.id);
            
            item.isFavorite = isInFavorites;
            item.isAdded = isInCart || newItems[index].isAdded;
            item.quantity = newItems[index].quantity;
          }
        });
      }
      
      isLoading.value = false
    }

    const initializeSlider = () => {
      if (visibleItems.value.length > 0 && sliderRef.value) {
        if (sliderInstance.value) {
          sliderInstance.value.update()
          return
        }
        
        sliderInstance.value = new KeenSlider(sliderRef.value, {
          loop: true,
          mode: 'free-snap',
          slides: { perView: 'auto', spacing: 10 },
          breakpoints: {
            '(min-width: 320px)': { slides: { perView: 1, spacing: 10 } },
            '(min-width: 480px)': { slides: { perView: 2, spacing: 10 } },
            '(min-width: 768px)': { slides: { perView: 3, spacing: 10 } },
            '(min-width: 1024px)': { slides: { perView: 4, spacing: 10 } },
            '(min-width: 1280px)': { slides: { perView: 5, spacing: 10 } }
          },
          created() {
            isLoading.value = false
          }
        })
        
        let timeout
        let mouseOver = false
        
        function clearNextTimeout() {
          clearTimeout(timeout)
        }
        
        function nextTimeout() {
          clearTimeout(timeout)
          if (mouseOver) return
          timeout = setTimeout(() => {
            if (sliderInstance.value) sliderInstance.value.next()
          }, 4000)
        }
        
        sliderInstance.value.on('created', () => {
          sliderRef.value.addEventListener('mouseover', () => {
            mouseOver = true
            clearNextTimeout()
          })
          sliderRef.value.addEventListener('mouseout', () => {
            mouseOver = false
            nextTimeout()
          })
          nextTimeout()
        })
        
        sliderInstance.value.on('dragStarted', clearNextTimeout)
        sliderInstance.value.on('animationEnded', nextTimeout)
        sliderInstance.value.on('updated', nextTimeout)
      }
    }

    watch(
      () => props.bestItems,
      async () => {
        await updateVisibleItems()
        nextTick(() => {
          initializeSlider()
        })
      },
      { deep: true }
    )

    // Добавляем наблюдатель за изменениями в избранном - улучшенная версия
    watch(favorites, () => {
      console.log('Список избранного изменился, обновляем статусы в BestItemsSlider');
      const changed = updateFavoritesStatus();
      
      // Если были изменения и слайдер инициализирован, обновляем его
      if (changed && sliderInstance.value) {
        nextTick(() => {
          sliderInstance.value.update();
        });
      }
    }, { deep: true });
    
    // Добавляем наблюдатель за изменениями в корзине
    watch(cart, () => {
      console.log('Корзина изменилась, обновляем статусы в BestItemsSlider');
      
      // Обновляем isAdded для каждого товара
      visibleItems.value.forEach(item => {
        const isInCart = cart.value.some(cartItem => cartItem.id === item.id);
        if (item.isAdded !== isInCart) {
          item.isAdded = isInCart;
          console.log(`Обновлен статус корзины для товара ${item.id} на ${isInCart}`);
        }
      });
    }, { deep: true });

    onMounted(() => {
      // При монтировании компонента загружаем и синхронизируем данные
      updateVisibleItems().then(() => {
        // После загрузки данных, проверяем статусы избранного
        updateFavoritesStatus();
        
        nextTick(() => {
          initializeSlider()
        })
      })
    })

    onBeforeUnmount(() => {
      if (sliderInstance.value) {
        sliderInstance.value.destroy()
        sliderInstance.value = null
      }
    })

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
      const itemToUpdate = visibleItems.value.find(item => item.id === itemData.id);
      if (itemToUpdate) {
        itemToUpdate.isAdded = true;
      }
      
      console.log('BestItemsSlider: Добавление товара в корзину:', itemData);
      emit('addToCart', itemData)
    }

    return { sliderRef, visibleItems, isLoading, onClickFavorite, onClickAdd }
  }
}
</script>

<template>
  <div v-cloak>
    <div v-if="!isLoading && visibleItems.length > 0">
      <div
        ref="sliderRef"
        class="keen-slider featured-products-slider"
        role="region"
        aria-label="Свежая поставка пиломатериалов"
      >
        <div v-for="item in visibleItems" :key="item.id" class="keen-slider__slide">
          <Item
            class="border-2 border-black"
            :id="item.id"
            :title="item.title"
            :image-url="item.imageUrl"
            :price_per_unit="Number(item.price_per_unit)"
            :price_per_cubic_meter="Number(item.price_per_cubic_meter)"
            :price_per_square_meter="Number(item.price_per_square_meter)"
            :price_per_linear_meter="Number(item.price_per_linear_meter)"
            :primary_unit="item.primary_unit"
            :unit_value="item.unit_value"
            :unit_label="item.unit_label"
            :isFavorite="item.isFavorite"
            :onClickFavorite="() => onClickFavorite(item)"
            :onClickAdd="onClickAdd"
            :isAdded="item.isAdded"
            :quantity="item.quantity"
            :custom_url="item.custom_url"
            :product_type="item.product_type"
            :is_available="item.is_available"
            :is_featured="item.is_featured"
          />
        </div>
      </div>
    </div>
    <div v-else>Загрузка товаров...</div>
  </div>
</template>

<style scoped>
[v-cloak] {
  display: none;
}

.keen-slider {
  height: 420px;
  position: relative;
}

.keen-slider__slide {
  height: 100%;
  display: flex;
  align-items: stretch;
  padding: 10px; /* Reduce padding */
  box-sizing: border-box;
}

:deep(.item-container) {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 20px;
  overflow: hidden;
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  border: 1px solid #eaeaea; /* Add subtle border */
}

:deep(.item-container:hover) {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

:deep(.product-image-container) {
  flex: 0 0 50%; /* Fixed ratio, don't grow or shrink */
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

:deep(.product-image) {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

:deep(.product-info) {
  padding: 10px;
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0; /* Allow it to shrink if needed */
  overflow: hidden; /* Prevent content from overflowing */
}

:deep(.product-title) {
  font-size: 0.875rem;
  line-height: 1.25rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 0.5rem;
}

:deep(.product-footer) {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto; /* Push to bottom */
  padding-top: 0.5rem;
}

:deep(.price-container) {
  display: flex;
  flex-direction: column;
  margin-bottom: 0.5rem;
}

:deep(.price-label) {
  font-size: 0.75rem;
  color: #6b7280;
}

:deep(.price-value) {
  font-size: 1rem;
  font-weight: 600;
}

:deep(.add-icon) {
  width: 24px;
  height: 24px;
  cursor: pointer;
}

/* Responsive adjustments for the slider */
@media (min-width: 1280px) {
  /* Specific adjustments for 5-item layout */
  :deep(.product-footer) {
    gap: 2px;
  }
  
  :deep(.stock-status) {
    font-size: 0.7rem;
  }
  
  :deep(.add-to-cart-btn) {
    font-size: 0.8rem;
  }
}

@media (max-width: 767px) {
  .keen-slider {
    height: 400px;
  }
  
  :deep(.product-info) {
    padding: 8px;
  }
}

@media (max-width: 640px) {
  .keen-slider {
    height: 380px;
  }
}

@media (max-width: 480px) {
  .keen-slider {
    height: 360px;
  }
  
  :deep(.product-title) {
    font-size: 0.8rem;
    line-height: 1.2rem;
  }
}

.keen-slider {
  user-select: none;
  touch-action: pan-y;
  -webkit-user-drag: none;
}
:deep(img) {
  -webkit-user-drag: none;
}
</style>
