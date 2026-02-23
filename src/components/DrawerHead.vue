<script setup>
import { inject } from 'vue'

const { closeDrawer } = inject('cart')
const { isDarkMode } = inject('theme', { isDarkMode: false })
</script>

<template>
  <div class="flex items-center gap-5 mb-8">
    <svg
      @click="closeDrawer"
      class="opacity-30 cursor-pointer hover:opacity-100 transition hover:-translate-x-1 dark:stroke-white"
      width="16"
      height="14"
      viewBox="0 0 16 14"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M1 7H14.7143"
        :stroke="isDarkMode ? 'white' : 'black'"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
      <path
        d="M8.71436 1L14.7144 7L8.71436 13"
        :stroke="isDarkMode ? 'white' : 'black'"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
    <h2 class="text-2xl font-bold dark:text-white">Корзина</h2>
  </div>
</template>
