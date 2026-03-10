<script setup>
import { ref } from 'vue'
import Footer from '../components/Footer.vue'
import { useHead } from '@vueuse/head'

useHead({
  title: 'Условия доставки | WoodDon',
  meta: [
    {
      name: 'description',
      content:
        'Информация о доставке пиломатериалов и стройматериалов от компании WoodDon. Виды доставки, сроки и условия.'
    },
    {
      name: 'keywords',
      content: 'доставка, пиломатериалы, стройматериалы, условия доставки, WoodDon'
    }
  ]
})

const activeTab = ref('types')

const deliveryTypes = [
  {
    name: 'Газель 1.5 т.',
    description:
      'Подойдет при покупке доски от 0.01 м3 до 2 м3 или других товаров на вес от 0.01 т. до 1.5 т.',
    imageSrc: '/gazelle.svg'
  },
  {
    name: 'Манипулятор 6 т.',
    description:
      'Подойдет при покупке доски от 2 м3 до 6 м3 или других товаров на вес от 1.5 т. до 6 т.',
    imageSrc: '/manipulator.svg'
  },
  {
    name: 'Камаз 10 т.',
    description: 'Подойдет при покупке доски от 6 м3 до 10 м3 или других товаров на вес более 6 т.',
    imageSrc: '/truck.svg'
  }
]

const deliveryInfo = [
  {
    title: 'Необходимая информация',
    content: [
      'номер дома (корпус, особенности или приметы);',
      'подъезд к дому (с какой улицы, двор, арка, пропуск, место для разгрузки);',
      'номер квартиры, код парадной, этаж, наличие лифта;',
      'номер телефона (на адресе, контактный);',
      'лицо, ответственное за прием материала, его координаты.'
    ]
  },
  {
    title: 'Стоимость',
    content: [
      'В зависимости от веса, объема и габаритов приобретенного Вами товара, а также вида доставки Вам будет предложена машина грузоподъемностью от 0,7 до 15 тонн, с манипулятором или без.',
      'Стоимость доставки зависит от грузоподъемности ТС, адреса и вида доставки, количества точек разгрузки.',
      'Такие услуги как разгрузка, пронос свыше 50 метров и подъем товара оплачиваются отдельно от доставки.',
      'Если Вы оплатили заказ по безналичному расчёту, при доставке Вас попросят предъявить доверенность, заполненную в соответствии с законодательством РФ. Доставка возможна также при наличии на объекте круглой печати.',
      'При осуществлении доплаты на объекте чек на сумму доплаты будет выдан Вам в строительном центре, в котором была произведена отгрузка товара, или передан водителем при следующей доставке.'
    ]
  },
  {
    title: 'Время доставки',
    content: [
      'Время доставки зависит от выбранного Вами вида доставки.',
      'Время доставки не распространяется на подъём.',
      'В случае если Вы оформляете несколько доставок на один адрес, время доставки на каждую следующую машину выставляется с интервалом в 1 час.'
    ]
  },
  {
    title: 'Общие правила',
    content: [
      'Водитель позвонит в момент выезда на Ваш адрес.',
      'В день доставки Вам следует быть постоянно на связи по указанным в заказе контактным телефонам (доставка осуществляется только после того, как Вы подтвердите свою готовность принять машину).',
      'Позаботьтесь о том, чтобы обеспечить машине беспрепятственный подъезд к месту разгрузки. В ином случае доставка будет осуществлена максимально близко к месту планируемой выгрузки без нарушения ПДД и вероятности повреждения автомобиля.',
      'На то, чтобы разгрузить машину, Вам будет выделено 30 минут с момента подачи, если речь идёт об автомобиле до 1,8 тонн включительно, и 60 минут для автомобилей свыше 1,8 тонн. Далее оплачивается простой в размере 300 руб. за каждый час — для машин до 1,8 тонн и 600 руб. за каждый час простоя — для машин свыше 1,8 тонн.',
      'Оплата заказа водителю производится возле автомобиля до начала разгрузки товара.',
      'В случае возникновения вопросов по количеству или качеству товара вы можете обратиться к представителю компании или позвонить по телефону Службы поддержки клиентов, который указан в товарном чеке.'
    ]
  },
  {
    title: 'Разгрузка манипулятором',
    content: [
      'Услуга «Разгрузка манипулятором» включает только разгрузку товара. К сожалению, мы не осуществляем иные виды работ манипулятором.',
      'Разгрузка манипулятором запрещена под линией электропередач, над бытовыми объектами и заборами.',
      'Разгрузка манипулятором осуществляется на расстоянии 2-15 метров от кузова автомобиля в зависимости от технических характеристик манипулятора, т. е. в радиусе действия стрелы и в зоне прямой видимости места разгрузки.'
    ]
  }
]
</script>

<template>
  <div class="main-container bg-gray-50 dark:bg-gray-900">
    <div class="content mt-20">
      <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold mb-8 text-gray-800 dark:text-white text-center">Доставка</h1>

        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
          <p class="text-gray-700 dark:text-gray-300 mb-6 text-center">
            Пожалуйста, ознакомьтесь с нашими правилами — их соблюдение поможет нам привезти Ваш
            заказ максимально быстро и качественно.
          </p>
        </div>

        <div class="mb-8">
          <div class="flex justify-center space-x-4 mb-6">
            <button
              @click="activeTab = 'types'"
              :class="[
                'px-4 py-2 rounded-full font-semibold focus:outline-none',
                activeTab === 'types'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              ]"
            >
              Виды доставки
            </button>
            <button
              @click="activeTab = 'info'"
              :class="[
                'px-4 py-2 rounded-full font-semibold focus:outline-none',
                activeTab === 'info'
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
              ]"
            >
              Информация о доставке
            </button>
          </div>

          <div v-if="activeTab === 'types'" class="grid md:grid-cols-3 gap-6">
            <div
              v-for="(delivery, index) in deliveryTypes"
              :key="index"
              class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md transition-transform duration-300 hover:scale-105"
            >
              <img
                :src="delivery.imageSrc"
                :alt="delivery.name"
                class="w-12 h-12 text-blue-500 mb-4"
              />
              <h3 class="text-xl font-semibold mb-2 text-gray-800 dark:text-white">
                {{ delivery.name }}
              </h3>
              <p class="text-gray-600 dark:text-gray-400">{{ delivery.description }}</p>
            </div>
          </div>

          <div v-if="activeTab === 'info'" class="space-y-6">
            <div
              v-for="(info, index) in deliveryInfo"
              :key="index"
              class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md"
            >
              <h3 class="text-xl font-semibold mb-4 text-gray-800 dark:text-white">
                {{ info.title }}
              </h3>
              <ul class="list-disc pl-5 text-gray-600 dark:text-gray-400 space-y-2">
                <li v-for="(item, itemIndex) in info.content" :key="itemIndex">{{ item }}</li>
              </ul>
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
