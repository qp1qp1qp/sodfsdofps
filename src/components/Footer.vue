<script setup>
import { ref, onMounted } from 'vue'
import { getProductTypes } from '../api'
import api from '../api'

const productTypes = ref([])
const email = ref('')

onMounted(async () => {
  await fetchProductTypes()
})

const fetchProductTypes = async () => {
  try {
    const response = await getProductTypes()
    productTypes.value = Array.isArray(response.data) ? response.data : response.data.results || []
  } catch (err) {
    console.error('Ошибка при загрузке типов товаров:', err)
  }
}

const subscribeNewsletter = async () => {
  try {
    const response = await api.post('/newsletter/subscribe/', { email: email.value })
    alert('Вы успешно подписались на рассылку!')
    email.value = ''
  } catch (error) {
    console.error('Ошибка при подписке на рассылку:', error)
    alert('Произошла ошибка при подписке. Пожалуйста, попробуйте позже.')
  }
}
</script>

<template>
  <footer class="bg-gray-800 dark:bg-gray-900 text-white py-12">
    <div class="container mx-auto px-4">
      <div class="grid md:grid-cols-4 gap-8">
        <div>
          <h3 class="text-xl font-bold mb-4">WoodDon</h3>
          <div class="text-gray-400 space-y-2">
            <p class="font-bold">Контакты:</p>
            <div class="flex items-center">
              <img
                src="/contact/phone-black.svg"
                alt="Phone"
                class="h-5 w-5 text-amber-500 mr-4 flex-shrink-0"
              />
              <span class="text-amber-500">+7 (928) 12-326-80</span>
            </div>
            <div class="flex items-center">
              <img
                src="/contact/phone-black.svg"
                alt="Phone"
                class="h-5 w-5 text-amber-500 mr-4 flex-shrink-0"
              />
              <span class="text-amber-500">+7 (988) 516-03-20</span>
            </div>
            <div class="flex items-start">
              <img
                src="/contact/map-pin-black.svg"
                alt="Map"
                class="h-5 w-5 text-amber-500 mr-4 mt-1 flex-shrink-0"
              />
              <span class="text-amber-500">г. Ростов-на-Дону, пер. Нефтяной 2а</span>
            </div>
            <div class="flex items-center">
              <img
                src="/contact/mail-black.svg"
                alt="Mail"
                class="h-5 w-5 text-amber-500 mr-4 flex-shrink-0"
              />
              <span class="text-amber-500">elenarev@yandex.ru</span>
            </div>
            <p class="font-semibold">Время работы:</p>
            <p class="text-amber-500">ПН-СБ: 9:00 – 17:00</p>
          </div>
        </div>
        <div>
          <h4 class="text-lg font-semibold mb-4">Каталог</h4>
          <ul class="space-y-2">
            <li v-for="type in productTypes" :key="type.id">
              <router-link
                :to="`/all-products/${type.slug}`"
                class="text-gray-400 hover:text-white transition duration-200"
              >
                {{ type.name }}
              </router-link>
            </li>
          </ul>
        </div>
        <div>
          <h4 class="text-lg font-semibold mb-4">Информация</h4>
          <ul class="space-y-2">
            <li>
              <router-link to="/faq" class="text-gray-400 hover:text-white transition duration-200"
                >FAQ</router-link
              >
            </li>
            <li>
              <router-link
                to="/delivery"
                class="text-gray-400 hover:text-white transition duration-200"
                >Доставка</router-link
              >
            </li>
            <li>
              <router-link
                to="/contacts"
                class="text-gray-400 hover:text-white transition duration-200"
                >Контакты</router-link
              >
            </li>
            <li>
              <router-link
                to="/about"
                class="text-gray-400 hover:text-white transition duration-200"
                >О компании</router-link
              >
            </li>
          </ul>
        </div>
        <div>
          <h4 class="text-lg font-semibold mb-4">Подписка на новости</h4>
          <p class="text-gray-400 mb-4">Будьте в курсе наших последних предложений</p>
          <form @submit.prevent="subscribeNewsletter" class="flex flex-col space-y-2">
            <input
              v-model="email"
              type="email"
              placeholder="Ваш email"
              class="w-full bg-gray-700 text-white px-4 py-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-amber-500"
              maxlength="50"
              required
            />
            <button
              type="submit"
              class="w-full sm:w-auto bg-amber-500 hover:bg-amber-600 text-white px-4 py-2 rounded-lg whitespace-nowrap transition duration-200 dark:bg-amber-500 dark:hover:bg-amber-600"
            >
              Подписаться
            </button>
          </form>
        </div>
      </div>
      <div class="mt-8 pt-8 border-t border-gray-700 text-center">
        <p class="text-gray-400">&copy; 2024 WoodDon. Все права защищены.</p>
      </div>
    </div>
  </footer>
</template>
