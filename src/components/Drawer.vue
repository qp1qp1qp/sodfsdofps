<script setup>
import { ref, inject, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import DrawerHead from './DrawerHead.vue'
import CartItemList from './CartItemList.vue'
import InfoBlock from './infoBlock.vue'
import TruckIndicator from './TruckIndicator.vue'

const props = defineProps({
  totalPrice: { type: Number, required: true }
})

const router = useRouter()
const { cart, closeDrawer } = inject('cart')

const orderId = ref(null)
const buttonDisabled = ref(false)

// ─── Рекомендованный метод доставки (приходит от TruckIndicator) ─────────────
const suggestedDelivery = ref(null)

// ─── Суммарный объём корзины в м³ ────────────────────────────────────────────
const totalVolume = computed(() =>
  cart.value.reduce((sum, item) => {
    
  
    let vol = Number(item.estimated_volume) || Number(item.volume_per_unit) || 0;
    
    // Fallback: If true volume is 0, roughly estimate using unit_value for linear/square items
    if (vol === 0 && item.unit_value) {
      if (item.primary_unit === 'linear') {
        // Very rough fallback estimate for linear: say, 0.005 m3 per linear meter
        vol = Number(item.unit_value) * 0.005; 
      } else if (item.primary_unit === 'square') {
        // Very rough fallback estimate for square: say, 0.05 m3 per square meter
        vol = Number(item.unit_value) * 0.05; 
      }
    }
    
    const qty = Number(item.quantity) || 0
    return sum + vol * qty
  }, 0)
)

const totalPriceFormatted = computed(() =>
  new Intl.NumberFormat('ru-RU').format(props.totalPrice)
)

const handleCreateOrder = () => {
  closeDrawer()
  router.push({
    path: '/checkout',
    // Передаём рекомендацию как state (не в URL)
    state: { suggestedDelivery: suggestedDelivery.value }
  })
}
</script>

<template>
  <div
    class="drawer-overlay fixed top-0 left-0 h-full w-full bg-black z-50 opacity-70"
    @click="closeDrawer"
  ></div>

  <div class="bg-white dark:bg-gray-800 w-full sm:w-96 h-full fixed right-0 top-0 z-50 flex flex-col">

    <!-- ── Верхняя часть: скролится ──────────────────────────────────────── -->
    <div class="flex-1 overflow-y-auto p-4 sm:p-6">
      <DrawerHead />

      <!-- Пустая корзина / успех -->
      <div v-if="!cart.length || orderId" class="flex h-full items-center justify-center">
        <InfoBlock
          v-if="!cart.length && !orderId"
          title="Корзина пустая"
          description="Добавьте хотя бы один товар, чтобы сделать заказ"
          image-url="/package-icon.png"
        />
        <InfoBlock
          v-if="orderId"
          title="Заказ оформлен!"
          :description="`Ваш заказ #${orderId} скоро будет обработан`"
          image-url="/order-success-icon.png"
        />
      </div>

      <!-- Список товаров -->
      <CartItemList v-else :cart="cart" />
    </div>

    <!-- ── Нижняя панель: фиксированная ─────────────────────────────────── -->
    <div
      v-if="cart.length && !orderId"
      class="border-t dark:border-gray-700 p-4 sm:p-5 flex flex-col gap-3 bg-white dark:bg-gray-800"
    >
      <!-- Индикатор машины -->
      <TruckIndicator
        :total-volume="totalVolume"
        @suggest-delivery="val => suggestedDelivery = val"
      />

      <!-- Итоговая цена -->
      <div class="flex gap-2 text-sm">
        <span class="text-gray-600 dark:text-gray-300">Итого:</span>
        <div class="flex-1 border-b border-dashed border-gray-300 dark:border-gray-600"></div>
        <b class="dark:text-white">{{ totalPriceFormatted }} ₽</b>
      </div>

      <!-- Кнопка -->
      <button
        :disabled="buttonDisabled"
        @click="handleCreateOrder"
        class="w-full rounded-xl py-3 font-semibold text-white bg-lime-500 hover:bg-lime-600 active:bg-lime-700 disabled:bg-slate-400 dark:bg-lime-600 dark:hover:bg-lime-700 transition"
      >
        Оформить заказ
      </button>

      <!-- Дисклеймер -->
      <p class="text-center text-xs text-gray-400 dark:text-gray-500 leading-snug">
        Цены носят информационный характер и&nbsp;не являются публичной офертой
        (ст.&nbsp;437 ГК РФ). Актуальная стоимость уточняется у&nbsp;менеджера.
      </p>
    </div>

  </div>
</template>

<style scoped>
/* Плавный скролл списка товаров */
.flex-1.overflow-y-auto::-webkit-scrollbar { width: 4px; }
.flex-1.overflow-y-auto::-webkit-scrollbar-track { background: transparent; }
.flex-1.overflow-y-auto::-webkit-scrollbar-thumb { background: #d1d5db; border-radius: 99px; }
</style>