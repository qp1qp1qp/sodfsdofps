<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: Number,
  title: String,
  imageUrl: String,
  price: Number,
  quantity: Number
})

const emit = defineEmits(['onClickRemove', 'onUpdateQuantity'])

const fullImageUrl = computed(() => {
  if (props.imageUrl) {
    if (props.imageUrl.startsWith('http')) return props.imageUrl;
    const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/api\/?$/, '');
    return `${baseUrl}${props.imageUrl.startsWith('/') ? '' : '/'}${props.imageUrl}`;
  }
  return ''
})

const incrementQuantity = (e) => {
  e.stopPropagation()
  emit('onUpdateQuantity', props.id, props.quantity + 1)
}

const decrementQuantity = (e) => {
  e.stopPropagation()
  if (props.quantity > 1) {
    emit('onUpdateQuantity', props.id, props.quantity - 1)
  }
}

const handleRemove = (e) => {
  e.stopPropagation()
  emit('onClickRemove')
}
</script>

<template>
  <div class="flex items-center border border-slate-200 p-4 rounded-xl gap-4">
    <img class="w-16 h-16 object-cover" :src="fullImageUrl" :alt="title" />

    <div class="flex flex-col flex-1">
      <p>{{ title }}</p>

      <div class="flex justify-between mt-2">
        <b class="flex-1">{{ price }} Руб</b>
        <div class="quantity-controls">
          <button @click="decrementQuantity" class="quantity-btn">-</button>
          <span class="quantity">{{ quantity }}</span>
          <button @click="incrementQuantity" class="quantity-btn">+</button>
        </div>
        <img
          @click="handleRemove"
          class="opacity-40 hover:opacity-100 cursor-pointer transition"
          src="/close.svg"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.quantity-controls {
  display: flex;
  align-items: center;
  margin-right: 10px;
}

.quantity-btn {
  width: 24px;
  height: 24px;
  background-color: #f3f4f6;
  border: none;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  color: #000;
}

.quantity {
  margin: 0 8px;
  font-size: 14px;
}

:root.dark .quantity-btn {
  background-color: #374151;
  color: #fff;
}
</style>
