<script setup>
import { ref } from 'vue'
import Footer from '../components/Footer.vue'
import { useHead } from '@vueuse/head'

const contactInfo = ref([
  {
    icon: '/contact/map-pin-icon.svg',
    title: 'Наш адрес',
    content: 'г. Ростов-на-Дону, пер. Нефтяной 2а',
    link: 'https://maps.google.com/?q=пер. Нефтяной, 2а, Ростов-на-Дону, Ростовская обл., 344064'
  },
  {
    icon: '/contact/phone.svg',
    title: 'Телефон',
    content: '+7 (928) 12-326-80',
    link: 'tel:+79281232680'
  },
  {
    icon: '/contact/phone.svg',
    title: 'Телефон',
    content: '+7 (988) 516-03-20',
    link: 'tel:+79885160320'
  },
  {
    icon: '/contact/mail.svg',
    title: 'Почта',
    content: 'elenarev@yandex.ru',
    link: 'mailto:elenarev@yandex.ru'
  },
  {
    icon: '/contact/time.svg',
    title: 'Часы работы',
    content: 'Пн-Пт: 9:00 - 17:00\nСб-Вс: выходной'
  }
])

const socialLinks = ref([
  { name: 'Instagram', url: 'https://www.instagram.com/wooddon.ru/', icon: '/contact/inst.svg' }
])

useHead({
  title: 'Контакты | WoodDon',
  meta: [
    {
      name: 'description',
      content:
        'Свяжитесь с нами для заказа пиломатериалов и стройматериалов. Адрес, телефон и другие контактные данные компании WoodDon.'
    },
    { name: 'keywords', content: 'контакты, адрес, телефон, email, WoodDon' }
  ]
})
</script>

<template>
  <div class="main-container bg-gray-50 dark:bg-gray-900">
    <div class="content mt-20">
      <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold mb-8 text-gray-800 dark:text-white text-center">
          Свяжитесь с нами
        </h1>

        <div class="grid md:grid-cols-2 gap-8 mb-12">
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-white">
              Контактная информация
            </h2>
            <div class="space-y-6">
              <div v-for="item in contactInfo" :key="item.title" class="flex items-start">
                <img
                  :src="item.icon"
                  alt=""
                  class="w-6 h-6 text-blue-600 dark:text-blue-400 mr-3 flex-shrink-0"
                />
                <div>
                  <h3 class="font-semibold text-gray-800 dark:text-white">{{ item.title }}</h3>
                  <p v-if="item.link" class="text-gray-600 dark:text-gray-400">
                    <a
                      :href="item.link"
                      class="hover:text-blue-600 dark:hover:text-blue-400 transition duration-300"
                    >
                      {{ item.content }}
                    </a>
                  </p>
                  <p v-else class="text-gray-600 dark:text-gray-400 whitespace-pre-line">
                    {{ item.content }}
                  </p>
                </div>
              </div>
            </div>

            <h3 class="text-xl font-semibold mt-8 mb-4 text-gray-800 dark:text-white">
              Мы в социальных сетях
            </h3>
            <div class="flex space-x-4">
              <a
                v-for="link in socialLinks"
                :key="link.name"
                :href="link.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 transition duration-300"
              >
                <span class="sr-only">{{ link.name }}</span>
                <img :src="link.icon" alt="" class="w-6 h-6" />
              </a>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
            <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-white">
              Наше расположение
            </h2>
            <div class="w-full h-64 md:h-80 lg:h-96 mb-4">
              <!-- Здесь будет ваша карта -->
              <div
                class="w-full h-full bg-gray-200 dark:bg-gray-700 rounded-lg flex items-center justify-center"
              >
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
            <p class="text-gray-600 dark:text-gray-400">
              Мы находимся в центре города, легко доступны на общественном транспорте и имеем
              удобную парковку для наших клиентов.
            </p>
          </div>
        </div>
      </div>
    </div>
    <Footer />
  </div>
</template>

<style scoped>
.main-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
}
</style>
