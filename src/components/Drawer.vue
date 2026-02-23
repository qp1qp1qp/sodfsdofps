<script setup>
import { ref, inject, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import DrawerHead from './DrawerHead.vue'
import CartItemList from './CartItemList.vue'
import InfoBlock from './infoBlock.vue'

const props = defineProps({
  totalPrice: {
    type: Number,
    required: true
  }
})

const router = useRouter()

const { cart, closeDrawer } = inject('cart')

const orderId = ref(null)
const buttonDisabled = ref(false)
const drawerContentRef = ref(null)

const updateQuantity = (item, change) => {
  const index = cart.value.findIndex((cartItem) => cartItem.id === item.id)
  if (index !== -1) {
    cart.value[index].quantity += change
    if (cart.value[index].quantity <= 0) {
      cart.value.splice(index, 1)
    }
  }
}

const handleCreateOrder = () => {
  closeDrawer()
  router.push('/checkout')
}

watch(
  cart,
  () => {
    if (drawerContentRef.value) {
      drawerContentRef.value.style.height = 'auto'
      drawerContentRef.value.style.height = `${drawerContentRef.value.scrollHeight}px`
    }
  },
  { deep: true }
)
</script>

<template>
  <div
    class="drawer-overlay fixed top-0 left-0 h-full w-full bg-black z-50 opacity-70"
    @click="closeDrawer"
  ></div>
  <div class="bg-white dark:bg-gray-800 w-full sm:w-96 h-full fixed right-0 top-0 z-50 flex flex-col">
    <div ref="drawerContentRef" class="p-4 sm:p-8 flex-grow overflow-y-auto transition-all duration-300">
      <DrawerHead />

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

      <div v-else>
        <CartItemList :cart="cart" @update-quantity="updateQuantity" />
      </div>
    </div>

    <div v-if="cart.length && !orderId" class="p-4 sm:p-8 border-t dark:border-gray-700">
      <div class="flex flex-col gap-4">
        <div class="flex gap-2 text-sm sm:text-base">
          <span class="dark:text-gray-300">Общая стоимость:</span>
          <div class="flex-1 border-b border-dashed dark:border-gray-600"></div>
          <b class="dark:text-white">{{ totalPrice }} Rub</b>
        </div>

        <button
          :disabled="buttonDisabled"
          @click="handleCreateOrder"
          class="mt-4 bg-lime-500 transition w-full rounded-xl py-3 hover:bg-lime-600 cursor-pointer active:bg-lime-700 disabled:bg-slate-400 dark:bg-lime-600 dark:hover:bg-lime-700 dark:active:bg-lime-800 dark:disabled:bg-slate-600"
        >
          Оформить заказ
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
</style>
