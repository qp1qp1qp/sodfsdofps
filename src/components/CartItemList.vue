<script setup>
import { inject } from 'vue'
import CartItem from './CartItem.vue'

const { cart, removeFromCart, updateCartItemQuantity } = inject('cart')

const handleUpdateQuantity = (itemId, newQuantity) => {
  // Stop event propagation to prevent it from affecting other components
  updateCartItemQuantity(itemId, newQuantity)
}

const handleRemoveFromCart = (item) => {
  // Stop event propagation to prevent it from affecting other components
  removeFromCart(item)
}
</script>

<template>
  <div class="flex flex-col flex-1 gap-4 justify-between" v-auto-animate>
    <CartItem
      v-for="item in cart"
      :key="item.id"
      :id="item.id"
      :title="item.title"
      :price="item.price"
      :image-url="item.imageUrl"
      :quantity="item.quantity"
      @on-click-remove="() => handleRemoveFromCart(item)"
      @on-update-quantity="handleUpdateQuantity"
    />
  </div>
</template>
