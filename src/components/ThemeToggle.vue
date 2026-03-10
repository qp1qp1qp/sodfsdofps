<script setup>
const props = defineProps({
  isDarkMode: Boolean
})

const emit = defineEmits(['toggle'])

const toggleTheme = () => {
  emit('toggle')
}
</script>

<template>
  <button
    @click="toggleTheme"
    type="button"
    :class="[
      'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-indigo-600 focus:ring-offset-2',
      isDarkMode ? 'bg-indigo-600' : 'bg-[#90b1f4]'
    ]"
    role="switch"
    :aria-checked="isDarkMode"
  >
    <span class="sr-only">Toggle dark mode</span>
    <span
      :class="[
        'pointer-events-none relative inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
        isDarkMode ? 'translate-x-5' : 'translate-x-0'
      ]"
    >
      <span
        :class="[
          'absolute inset-0 flex h-full w-full items-center justify-center transition-opacity',
          isDarkMode ? 'opacity-0 duration-0 ease-out' : 'opacity-100 duration-200 ease-in'
        ]"
        aria-hidden="true"
      >
        <img src="/light-mode.svg" alt="Light mode" class="h-3 w-3" />
      </span>
      <span
        :class="[
          'absolute inset-0 flex h-full w-full items-center justify-center transition-opacity',
          isDarkMode ? 'opacity-100 duration-200 ease-in' : 'opacity-0 duration-0 ease-out'
        ]"
        aria-hidden="true"
      >
        <img src="/dark-mode.svg" alt="Dark mode" class="h-3 w-3" />
      </span>
    </span>
  </button>
</template>

<style scoped>
@keyframes toggleAnimation {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(0.9);
  }
  100% {
    transform: scale(1);
  }
}

.animate-toggle img {
  animation: toggleAnimation 0.3s ease-in-out;
}
</style>
