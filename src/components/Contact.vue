<template>
  <section class="my-16" aria-labelledby="contact-title">
    <div class="custom-container">
      <h2
        id="contact-title"
        class="text-3xl font-bold text-gray-800 dark:text-gray-100 mb-8 text-center"
      >
        Контакты
      </h2>
      <div class="flex flex-col xl:flex-row gap-8">
        <div class="w-full xl:w-1/4 bg-white dark:bg-gray-700 rounded-lg shadow-xl p-6">
          <h3 class="text-xl font-bold text-gray-800 dark:text-gray-100 mb-4">Свяжитесь с нами</h3>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
            Мы здесь, чтобы помочь со всеми вашими потребностями в пиломатериалах.
          </p>
          <div class="space-y-4">
            <div class="flex items-start">
              <img
                :src="mapIcon"
                alt="Map"
                class="h-5 w-5 text-amber-500 mr-4 mt-1 flex-shrink-0"
              />
              <span class="text-gray-600 dark:text-gray-300"
                >г. Ростов-на-Дону, пер. Нефтяной 2а</span
              >
            </div>
            <div class="flex items-center">
              <img :src="phoneIcon" alt="Phone" class="h-5 w-5 text-amber-500 mr-4 flex-shrink-0" />
              <span class="text-gray-600 dark:text-gray-300">+7 (928) 12-326-80</span>
            </div>
            <div class="flex items-center">
              <img :src="phoneIcon" alt="Phone" class="h-5 w-5 text-amber-500 mr-4 flex-shrink-0" />
              <span class="text-gray-600 dark:text-gray-300">+7 (988) 516-03-20</span>
            </div>
            <div class="flex items-center">
              <img :src="mailIcon" alt="Mail" class="h-5 w-5 text-amber-500 mr-4 flex-shrink-0" />
              <span class="text-gray-600 dark:text-gray-300">elenarev@yandex.ru</span>
            </div>
          </div>
        </div>
        <div class="w-full xl:w-3/4 rounded-lg shadow-xl overflow-hidden h-64 xl:h-auto">
          <!-- Placeholder for map -->
          <iframe
            src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d2707.9358349345493!2d39.624456014923474!3d47.256957978859894!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x40e3c7706d115745%3A0xa79be24f1cc273e3!2z0L_QtdGALiDQndC10YTRgtGP0L3QvtC5LCAy0LAsINCg0L7RgdGC0L7Qsi3QvdCwLdCU0L7QvdGDLCDQoNC-0YHRgtC-0LLRgdC60LDRjyDQvtCx0LsuLCAzNDQwNjQ!5e0!3m2!1sru!2sru!4v1647421579150!5m2!1sru!2sru"
            width="100%"
            height="100%"
            style="border: 0"
            allowfullscreen=""
            loading="lazy"
          ></iframe>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed, inject } from 'vue'

// Инжектируем состояние темы из Header.vue
const { isDarkMode } = inject('theme')

const mapIcon = computed(() =>
  isDarkMode.value ? '/contact/map-pin-icon.svg' : '/contact/map-pin-black.svg'
)
const phoneIcon = computed(() =>
  isDarkMode.value ? '/contact/phone.svg' : '/contact/phone-black.svg'
)
const mailIcon = computed(() =>
  isDarkMode.value ? '/contact/mail.svg' : '/contact/mail-black.svg'
)
</script>

<style scoped>
.custom-container {
  width: 100%;
  max-width: 1936px;
  margin-left: auto;
  margin-right: auto;
  padding-left: 0rem;
  padding-right: 0rem;
}

@media (max-width: 450px) {
  .custom-container {
    padding-left: 0rem;
    padding-right: 0rem;
  }
}
</style>
