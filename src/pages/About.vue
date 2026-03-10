<script setup>
import { ref } from 'vue'
import Footer from '../components/Footer.vue'
import { useHead } from '@vueuse/head'

const stats = ref([
  { label: 'Лет на рынке', value: new Date().getFullYear() - 2006 },
  { label: 'Отгружено м³ в месяц', value: '500+' },
  { label: 'Довольных клиентов', value: '1000+' },
  { label: 'Видов продукции', value: '100+' }
])

const timeline = ref([
  { year: 2006, event: 'Основание компании' },
  { year: 2010, event: 'Расширение ассортимента' },
  { year: 2015, event: 'Открытие нового склада' },
  { year: 2020, event: 'Запуск онлайн-магазина' },
  { year: new Date().getFullYear(), event: 'Продолжаем расти и развиваться' }
])

const partners = ref([
  'Вологодский шиферный завод',
  'Белгородский шиферный завод',
  'Металлпрофиль',
  'Гранд лайн',
  'Технониколь'
])

useHead({
  title: 'О компании WoodDon | Пиломатериалы и стройматериалы',
  meta: [
    {
      name: 'description',
      content:
        'WoodDon - ваш надежный поставщик пиломатериалов и стройматериалов с 2006 года. Узнайте о нашей истории, достижениях и партнерах.'
    },
    {
      name: 'keywords',
      content: 'WoodDon, история компании, пиломатериалы, стройматериалы, достижения'
    }
  ]
})
</script>

<template>
  <div class="main-container bg-gray-50 dark:bg-gray-900">
    <div class="content mt-20">
      <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold mb-8 text-gray-800 dark:text-white text-center">
          О нашей компании
        </h1>

        <div class="grid md:grid-cols-2 gap-8 mb-12">
          <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">Наша история</h2>
            <p class="text-gray-600 dark:text-gray-400 mb-4">
              С 2006 года мы специализируемся на поставке высококачественных стройматериалов для
              строительства домов, кровли и внутренней отделки. Наш основной фокус - пиломатериалы,
              которые мы получаем напрямую с лучших лесокомбинатов России.
            </p>
            <p class="text-gray-600 dark:text-gray-400">
              Мы гордимся тем, что помогаем нашим клиентам выбрать идеальные материалы для их
              проектов, обеспечивая оптимальное соотношение цены и качества.
            </p>
          </div>
          <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h2 class="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">
              Наши преимущества
            </h2>
            <ul class="list-disc pl-5 text-gray-600 dark:text-gray-400 space-y-2">
              <li>Благодаря сотрудничеству с разными лесопилками, предоставляем лучшие цены</li>
              <li>Широкий ассортимент пиломатериалов и сопутствующих товаров</li>
              <li>Экспертная консультация по выбору материалов</li>
              <li>Точные и своевременные поставки</li>
              <li>Доставка по городу и области</li>
              <li>Возможность заказа редких товаров</li>
              <li>Скидки для постоянных клиентов</li>
            </ul>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mb-12">
          <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-white text-center">
            Наши достижения
          </h2>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div v-for="stat in stats" :key="stat.label" class="text-center p-2">
              <div class="text-2xl sm:text-3xl font-bold text-blue-600 dark:text-blue-400">
                {{ stat.value }}
              </div>
              <div class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">
                {{ stat.label }}
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mb-12">
          <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-white text-center">
            Наша история
          </h2>
          <div class="relative">
            <div
              class="absolute left-1/2 transform -translate-x-1/2 h-full w-1 bg-blue-200 dark:bg-blue-800"
            ></div>
            <div
              v-for="(item, index) in timeline"
              :key="item.year"
              :class="['flex items-center mb-8', index % 2 === 0 ? 'flex-row-reverse' : '']"
            >
              <div class="w-5/12"></div>
              <div
                class="z-10 flex items-center justify-center w-12 h-12 rounded-full bg-blue-600 text-white font-bold"
              >
                {{ item.year }}
              </div>
              <div class="w-5/12 px-4">
                <div class="p-3 bg-blue-100 dark:bg-blue-900 rounded shadow">
                  {{ item.event }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md mb-12">
          <h2 class="text-2xl font-semibold mb-6 text-gray-800 dark:text-white text-center">
            Наши партнеры
          </h2>
          <div class="flex flex-wrap justify-center gap-4">
            <div
              v-for="partner in partners"
              :key="partner"
              class="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-full text-sm text-gray-800 dark:text-gray-200"
            >
              {{ partner }}
            </div>
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
