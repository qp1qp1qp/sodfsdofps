<script setup>
import { ref, computed, inject, watch } from 'vue'
import { useRouter } from 'vue-router'
import { createOrder } from '../api'
import Footer from '../components/Footer.vue'
import { useHead } from '@vueuse/head'
import { vMaska } from "maska/vue"

useHead({
  title: 'Оформление заказа | WoodDon',
  meta: [
    {
      name: 'description',
      content:
        'Оформление заказа на пиломатериалы и стройматериалы в компании WoodDon. Удобный процесс покупки и доставки.'
    },
    {
      name: 'keywords',
      content: 'оформление заказа, покупка, пиломатериалы, стройматериалы, WoodDon'
    }
  ]
})

const router = useRouter()
const { cart, clearCart } = inject('cart', { value: [], clearCart: () => {} })
const { isDarkMode } = inject('theme', { isDarkMode: ref(false) })

const customerType = ref('individual')
const firstName = ref('')
const lastName = ref('')
const phone = ref('')
const email = ref('')
const comment = ref('')
const deliveryMethod = ref('')

const phoneError = ref('')
const emailError = ref('')

const deliveryMethods = [
  { id: 1, name: 'Самовывоз', price: 0 },
  { id: 2, name: 'Доставка по Ростову-на-Дону 1.5т от 3000 руб', price: 3000 },
  { id: 3, name: 'Доставка по Ростову-на-Дону 6т от 8000 руб', price: 8000 },
  { id: 4, name: 'Доставка по Ростову-на-Дону 10т от 10000 руб', price: 10000 }
]

const orderNumber = ref('')

const generateOrderNumber = () => {
  return Math.floor(10000000 + Math.random() * 90000000).toString()
}

const deliveryPrice = computed(() => {
  if (!deliveryMethod.value) return 0
  const selectedMethod = deliveryMethods.find((method) => method.name === deliveryMethod.value)
  return selectedMethod ? selectedMethod.price : 0
})

const totalPrice = computed(() => {
  const itemsTotal = cart.value.reduce((total, item) => total + item.price * item.quantity, 0)
  return itemsTotal + deliveryPrice.value
})

const validatePhone = (value) => {
  const cleaned = value.replace(/[\s\-\(\)]/g, '')
  return /^\+?[78]?\d{10}$/.test(cleaned)
}

const validateEmail = (value) => {
  if (!value) return true // Email is optional
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(value)
}

watch(phone, (newValue) => {
  if (!validatePhone(newValue)) {
    phoneError.value = 'Пожалуйста, введите корректный номер телефона'
  } else {
    phoneError.value = ''
  }
})

watch(email, (newValue) => {
  if (newValue && !validateEmail(newValue)) {
    emailError.value = 'Пожалуйста, введите корректный email или оставьте поле пустым'
  } else {
    emailError.value = ''
  }
})

const isFormValid = computed(() => {
  return (
    firstName.value.trim().length >= 2 &&
    validatePhone(phone.value) &&
    deliveryMethod.value &&
    (email.value === '' || validateEmail(email.value))
  )
})

const showPopup = ref(false)
const isSubmitting = ref(false)

const handleCreateOrder = async () => {
  if (!isFormValid.value || isSubmitting.value) return
  isSubmitting.value = true

  const orderData = {
    customer_type: customerType.value,
    first_name: firstName.value,
    last_name: lastName.value,
    phone: phone.value,
    email: email.value,
    comment: comment.value,
    delivery_method: deliveryMethod.value,
    items: cart.value.map((item) => ({
      product_id: item.id,
      title: item.title,
      quantity: item.quantity,
      price: item.price,
      imageUrl: item.imageUrl
    })),
    total_price: totalPrice.value
  }

  try {
    const response = await createOrder(orderData)
    console.log('Заказ успешно создан:', response.data)
    clearCart()
    showPopup.value = true
  } catch (error) {
    console.error('Ошибка при оформлении заказа:', error.response?.data || error.message)
  } finally {
    isSubmitting.value = false
  }
}

const closePopup = () => {
  showPopup.value = false
  router.push('/')
}

const getFullImageUrl = (imageUrl) => {
  if (!imageUrl) return ''
  if (imageUrl.startsWith('http')) {
    return imageUrl
  }
  const baseUrl = (import.meta.env.VITE_API_URL || '').replace(/\/api\/?$/, '');
  return `${baseUrl}${imageUrl.startsWith('/') ? '' : '/'}${imageUrl}`
}
</script>

<template>
  <div :class="['main-container', { dark: isDarkMode }]">
    <div class="content mt-20 bg-gray-100 dark:bg-gray-900 min-h-screen">
      <div class="container mx-auto px-8 py-8">
        <h1 class="text-3xl font-bold mb-8 text-gray-800 dark:text-gray-100">Оформление заказа</h1>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-gray-100">
              Данные заказа
            </h2>
            <div class="space-y-6">
              <div class="space-y-2">
                <div class="font-medium text-gray-700 dark:text-gray-300 mb-2">Тип клиента:</div>
                <div class="flex flex-col space-y-2">
                  <label class="inline-flex items-center">
                    <input
                      type="radio"
                      v-model="customerType"
                      value="individual"
                      class="form-radio text-indigo-600"
                    />
                    <span class="ml-2 text-gray-700 dark:text-gray-300">Физическое лицо</span>
                  </label>
                  <label class="inline-flex items-center">
                    <input
                      type="radio"
                      v-model="customerType"
                      value="legal"
                      class="form-radio text-indigo-600"
                    />
                    <span class="ml-2 text-gray-700 dark:text-gray-300">Юридическое лицо</span>
                    </label>
                    <p v-if="customerType === 'legal'" class="text-sm text-gray-500 dark:text-gray-400 ml-6">
                      +20% НДС или запрос счета через менеджера
                    </p>
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label
                    for="firstName"
                    class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                    >Имя *</label
                  >
                  <input
                    v-model="firstName"
                    id="firstName"
                    type="text"
                    class="form-input w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                  <p v-if="firstName.length > 0 && firstName.trim().length < 2" class="mt-1 text-sm text-red-600">
                    Имя должно содержать минимум 2 символа
                  </p>
                </div>
                <div>
                  <label
                    for="lastName"
                    class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                    >Фамилия</label
                  >
                  <input
                    v-model="lastName"
                    id="lastName"
                    type="text"
                    class="form-input w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label
                    for="phone"
                    class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                    >Телефон *</label
                  >
                  <input
                    v-model="phone"
                    v-maska
                    data-maska="+7 (###) ###-##-##"
                    id="phone"
                    type="tel"
                    placeholder="+7 (999) 999-99-99"
                    class="form-input w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                    required
                  />
                  <p v-if="phoneError" class="mt-1 text-sm text-red-600">{{ phoneError }}</p>
                </div>
                <div>
                  <label
                    for="email"
                    class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                    >Email</label
                  >
                  <input
                    v-model="email"
                    id="email"
                    type="email"
                    class="form-input w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                  />
                  <p v-if="emailError" class="mt-1 text-sm text-red-600">{{ emailError }}</p>
                </div>
              </div>

              <div>
                <label
                  for="comment"
                  class="block mb-2 text-sm font-medium text-gray-700 dark:text-gray-300"
                  >Комментарий</label
                >
                <textarea
                  v-model="comment"
                  id="comment"
                  rows="3"
                  class="form-textarea w-full px-3 py-2 rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                ></textarea>
              </div>

              <div>
                <h3 class="text-xl font-semibold mb-4 text-gray-800 dark:text-gray-100">
                  Способ доставки *
                </h3>
                <div class="space-y-2">
                  <div v-for="method in deliveryMethods" :key="method.id" class="flex items-center">
                    <input
                      type="radio"
                      v-model="deliveryMethod"
                      :id="method.id"
                      :value="method.name"
                      class="form-radio text-indigo-600"
                    />
                    <label :for="method.id" class="ml-2 text-gray-700 dark:text-gray-300">{{
                      method.name
                    }}</label>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-gray-100">Ваш заказ</h2>
            <div class="max-h-96 overflow-y-auto mb-6">
              <div
                v-for="item in cart"
                :key="item.id"
                class="flex items-center space-x-4 mb-4 pb-4 border-b border-gray-200 dark:border-gray-700"
              >
                <img
                  :src="getFullImageUrl(item.imageUrl)"
                  :alt="item.title"
                  class="w-16 h-16 object-cover rounded-md"
                />
                <div class="flex-1">
                  <h3 class="font-medium text-gray-800 dark:text-gray-200">{{ item.title }}</h3>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ item.quantity }} x {{ item.price_per_unit }} ₽ за шт.
                  </p>
                  <p class="text-sm text-gray-600 dark:text-gray-400">
                    {{ item.price_per_cubic_meter }} ₽ за м³
                  </p>
                </div>
                <div class="text-right">
                  <p class="font-medium text-gray-800 dark:text-gray-200">
                    {{ item.price * item.quantity }} ₽
                  </p>
                </div>
              </div>
            </div>
            <div class="border-t border-gray-200 dark:border-gray-700 pt-4">
              <div v-if="deliveryPrice > 0" class="flex justify-between">
                <span>Стоимость доставки:</span>
                <span>{{ deliveryPrice }} Rub</span>
              </div>

              <div
                class="flex justify-between items-center font-semibold text-lg text-gray-800 dark:text-gray-100"
              >
                <span>Итого:</span>
                <span>{{ totalPrice }} ₽</span>
              </div>
            </div>
            <button
              @click="handleCreateOrder"
              :disabled="!isFormValid || isSubmitting"
              :class="isSubmitting ? 'opacity-50 cursor-not-allowed' : ''"
              class="w-full mt-6 bg-indigo-600 text-white py-3 px-4 rounded-lg font-semibold hover:bg-indigo-700 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              Оформить заказ
            </button>
          </div>
        </div>
      </div>
    </div>
    <Footer />
    <div
      v-if="showPopup"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
    >
      <div class="bg-white dark:bg-gray-800 rounded-lg p-8 max-w-md w-full mx-4 relative">
        <button
          @click="closePopup"
          class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
        >
          <svg
            class="w-6 h-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        </button>
        <div class="text-center">
          <svg
            class="w-16 h-16 text-green-500 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            ></path>
          </svg>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
            Спасибо за заказ, {{ firstName }}!
          </h2>
          <p class="text-gray-600 dark:text-gray-300 mb-4">
          Ваш заказ успешно принят! Наш менеджер свяжется с вами в ближайшее время для подтверждения деталей.
        </p>
        <p class="text-gray-600 dark:text-gray-300 mb-6">
          Если у вас есть вопросы — вы можете позвонить нам сами:
        </p>
        <a
          href="tel:+79885160320"
          class="inline-flex items-center gap-2 bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-full font-semibold transition-colors"
        >
          <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
            <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
          </svg>
          +7 (988) 516-03-20
        </a>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.container {
  max-width: 100%;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideIn {
  from {
    transform: translateY(-20px);
  }
  to {
    transform: translateY(0);
  }
}

.fixed {
  animation: fadeIn 0.3s ease-out;
}

.fixed > div {
  animation: slideIn 0.3s ease-out;
}
</style>
