<script setup>
import { ref } from 'vue'
import Footer from '../components/Footer.vue'
import { useHead } from '@vueuse/head'

const faqs = ref([
  {
    category: 'Выбор пиломатериалов',
    questions: [
      {
        q: 'Какие виды древесины вы предлагаете?',
        a: 'Мы предлагаем широкий ассортимент пиломатериалов, включая сосну, ель, лиственницу, дуб и березу. Каждый вид древесины имеет свои уникальные характеристики и подходит для различных целей.',
        isOpen: false
      },
      {
        q: 'Как выбрать правильный пиломатериал для моего проекта?',
        a: 'Выбор зависит от назначения проекта, требуемой прочности, устойчивости к влаге и бюджета. Наши специалисты всегда готовы проконсультировать вас и помочь выбрать оптимальный вариант.',
        isOpen: false
      },
      {
        q: 'Что означают сорта пиломатериалов?',
        a: 'Сорта (1, 2, 3, 4) определяют качество древесины. Первый сорт имеет минимальное количество дефектов и подходит для видимых конструкций, в то время как 4-й сорт может использоваться для черновых работ.',
        isOpen: false
      }
    ]
  },
  {
    category: 'Доставка и оплата',
    questions: [
      {
        q: 'Как осуществляется доставка пиломатериалов?',
        a: 'Мы предлагаем доставку по городу и области. Сроки и стоимость зависят от объема заказа и расстояния. Также возможен самовывоз со склада.',
        isOpen: false
      },
      {
        q: 'Какие способы оплаты вы принимаете?',
        a: 'Мы принимаем наличные, банковские карты и безналичный расчет для юридических лиц. Возможна оплата как при получении, так и в офисе.',
        isOpen: false
      },
      {
        q: 'Можно ли оплатить с сайта?',
        a: 'Мы не принимаем оплату на сайте.',
        isOpen: false
      },
      {
        q: 'Есть ли у вас минимальный объем заказа?',
        a: 'Минимальный объем заказа зависит от типа пиломатериала. Для большинства позиций он составляет от 1 м³. Точную информацию уточняйте у наших менеджеров.',
        isOpen: false
      }
    ]
  },
  {
    category: 'Хранение и обработка',
    questions: [
      {
        q: 'Как правильно хранить пиломатериалы?',
        a: 'Пиломатериалы следует хранить в сухом, проветриваемом помещении, защищенном от прямых солнечных лучей и осадков. Штабеля должны быть уложены на ровную поверхность с прокладками между рядами.',
        isOpen: false
      },
      {
        q: 'Нужно ли обрабатывать пиломатериалы перед использованием?',
        a: 'Это зависит от назначения. Для наружных работ рекомендуется обработка антисептиками и влагозащитными составами. Для внутренних работ может потребоваться шлифовка и покрытие лаком или краской.',
        isOpen: false
      },
      {
        q: 'Предоставляете ли вы услуги по обработке пиломатериалов?',
        a: 'Да, мы предлагаем услуги по распилу, строганию и сушке пиломатериалов. Подробности и стоимость уточняйте у наших менеджеров.',
        isOpen: false
      }
    ]
  }
])

const toggleQuestion = (category, index) => {
  faqs.value[category].questions[index].isOpen = !faqs.value[category].questions[index].isOpen
}

useHead({
  title: 'FAQ | WoodDon - Ответы на вопросы о пиломатериалах',
  meta: [
    {
      name: 'description',
      content:
        'Ответы на часто задаваемые вопросы о выборе, доставке и хранении пиломатериалов от компании WoodDon. Узнайте все о покупке качественных пиломатериалов.'
    },
    {
      name: 'keywords',
      content:
        'FAQ, вопросы и ответы, пиломатериалы, выбор древесины, доставка пиломатериалов, хранение древесины, WoodDon'
    }
  ]
})
</script>

<template>
  <div class="main-container bg-gray-50 dark:bg-gray-900">
    <div class="content mt-20">
      <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold mb-8 text-gray-800 dark:text-white text-center">
          Часто задаваемые вопросы
        </h1>

        <div v-for="(category, categoryIndex) in faqs" :key="category.category" class="mb-12">
          <h2 class="text-2xl font-semibold mb-4 text-gray-700 dark:text-gray-200">
            {{ category.category }}
          </h2>
          <div
            v-for="(faq, faqIndex) in category.questions"
            :key="faq.q"
            class="mb-4 bg-white dark:bg-gray-800 rounded-lg shadow-md"
          >
            <button
              @click="toggleQuestion(categoryIndex, faqIndex)"
              class="w-full text-left p-4 flex justify-between items-center focus:outline-none"
            >
              <h3 class="text-xl font-medium text-gray-800 dark:text-white">
                {{ faq.q }}
              </h3>
              <svg
                v-if="!faq.isOpen"
                class="h-6 w-6 text-gray-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                />
              </svg>
              <svg
                v-else
                class="h-6 w-6 text-gray-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M18 12H6"
                />
              </svg>
            </button>
            <div v-show="faq.isOpen" class="px-4 pb-4">
              <p class="text-gray-600 dark:text-gray-300">
                {{ faq.a }}
              </p>
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
