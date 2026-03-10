<script setup>

import { computed } from 'vue'

const props = defineProps({
  totalVolume: { type: Number, default: 0 }
})

const emit = defineEmits(['suggest-delivery'])

const TIERS = [
  {
    id:       'gazelle',
    maxVol:   1.5,
    vehicle:  'Газель',
    icon:     '/van.svg',        // fallback emoji если нет SVG
    emoji:    '🚐',
    color:    '#16a34a',
    fill:     '#22c55e',
    bgLight:  '#dcfce7',
    bgDark:   'rgba(20,83,45,.45)',
    price:    'от 3 000 ₽',
    msg:      'Легко! Газель справится 💪',
    sub:      'Самый дешёвый вариант доставки',
    // deliveryMethod — name из Checkout.deliveryMethods
    method:   'Доставка по Ростову-на-Дону 1.5т от 3000 руб'
  },
  {
    id:       'gazelle_full',
    maxVol:   2,
    vehicle:  'Газель',
    icon:     '/van.svg',
    emoji:    '🚐',
    color:    '#ca8a04',
    fill:     '#eab308',
    bgLight:  '#fef9c3',
    bgDark:   'rgba(66,32,6,.45)',
    price:    'от 3 000 ₽',
    msg:      'Газель загружена под завязку 😅',
    sub:      'Рессоры скрипят — но довезём!',
    method:   'Доставка по Ростову-на-Дону 1.5т от 3000 руб'
  },
  {
    id:       'manipulator',
    maxVol:   6,
    vehicle:  'Манипулятор',
    icon:     '/crane.svg',
    emoji:    '🚛',
    color:    '#c2410c',
    fill:     '#f97316',
    bgLight:  '#ffedd5',
    bgDark:   'rgba(67,20,7,.45)',
    price:    'от 8 000 ₽',
    msg:      'Нужен Манипулятор 🦾',
    sub:      'Газель не потянет — пора брать побольше',
    method:   'Доставка по Ростову-на-Дону 6т от 8000 руб'
  },
  {
    id:       'kamaz',
    maxVol:   10,
    vehicle:  'КамАЗ',
    icon:     '/truck.svg',
    emoji:    '🚚',
    color:    '#b91c1c',
    fill:     '#ef4444',
    bgLight:  '#fee2e2',
    bgDark:   'rgba(69,10,10,.45)',
    price:    'от 10 000 ₽',
    msg:      'Серьёзный объём — нужен КамАЗ! 💪',
    sub:      'Большая стройка!',
    method:   'Доставка по Ростову-на-Дону 10т от 10000 руб'
  },
  {
    id:       'multi',
    maxVol:   Infinity,
    vehicle:  'Несколько рейсов',
    icon:     '/truck.svg',
    emoji:    '🚚🚚',
    color:    '#7c3aed',
    fill:     '#8b5cf6',
    bgLight:  '#ede9fe',
    bgDark:   'rgba(46,16,101,.45)',
    price:    'уточните у менеджера',
    msg:      'Нужно несколько машин! 🏗️',
    sub:      'Менеджер рассчитает оптимальную логистику',
    method:   'Доставка по Ростову-на-Дону 10т от 10000 руб'
  }
]

const tier = computed(() => {
  const v = props.totalVolume
  const t = TIERS.find(t => v <= t.maxVol) || TIERS[TIERS.length - 1]
  emit('suggest-delivery', t.method)
  return t
})

// Прогресс шкалы внутри текущего диапазона
const barPercent = computed(() => {
  const v = props.totalVolume
  if (v <= 0) return 0
  if (v <= 2)  return Math.min((v / 2) * 100, 100)
  if (v <= 6)  return Math.min(((v - 2) / 4) * 100, 100)
  if (v <= 10) return Math.min(((v - 6) / 4) * 100, 100)
  return 100
})

const rangeLabel = computed(() => {
  const v = props.totalVolume
  if (v <= 2)  return '0 – 2 м³ (Газель)'
  if (v <= 6)  return '2 – 6 м³ (Манипулятор)'
  if (v <= 10) return '6 – 10 м³ (КамАЗ)'
  return 'более 10 м³'
})

const volFormatted = computed(() => {
  if (props.totalVolume <= 0) return null
  // убираем лишние нули: 1.3000 → 1.3
  return props.totalVolume.toFixed(3).replace(/\.?0+$/, '') + ' м³'
})

</script>

<template>
  <div class="ti" :style="{ '--c': tier.fill, '--bg': tier.bgLight, '--bgd': tier.bgDark }">

    <!-- Заголовок ряд -->
    <div class="ti-head">
      <span class="ti-label">📦 Объём заказа</span>
      <span v-if="volFormatted" class="ti-vol" :style="{ color: tier.color }">
        {{ volFormatted }}
      </span>
    </div>

    <!-- Прогресс-бар -->
    <div class="ti-track" role="progressbar" :aria-valuenow="barPercent">
      <div
        class="ti-fill"
        :style="{ width: (volFormatted ? barPercent : 0) + '%', background: tier.fill }"
      ></div>
    </div>
    <div class="ti-range">{{ rangeLabel }}</div>

    <!-- Статус-блок -->
    <div class="ti-status">
      <!-- иконка: пробуем SVG, fallback — emoji -->
      <img
        :src="tier.icon"
        :alt="tier.vehicle"
        class="ti-vehicle-img"
        @error="$event.target.style.display='none'; $event.target.nextElementSibling.style.display='block'"
      />
      <span class="ti-vehicle-emoji" style="display:none">{{ tier.emoji }}</span>

      <div class="ti-text">
        <p class="ti-msg" :style="{ color: tier.color }">{{ tier.msg }}</p>
        <p class="ti-sub">{{ tier.sub }}</p>
      </div>
    </div>

    <!-- Итог -->
    <div class="ti-price-row">
      <span class="ti-vehicle-name">{{ tier.emoji }} {{ tier.vehicle }}</span>
      <span class="ti-price" :style="{ color: tier.color }">{{ tier.price }}</span>
    </div>

    <!-- Пустая корзина -->
    <p v-if="!volFormatted" class="ti-empty">
      Добавьте товары — покажем, какая машина нужна для доставки
    </p>

  </div>
</template>

<style scoped>
.ti {
  border: 1.5px solid var(--c, #e5e7eb);
  border-radius: 14px;
  padding: 12px 14px;
  display: flex;
  flex-direction: column;
  gap: 9px;
  background: #fff;
  transition: border-color .3s;
}
:global(.dark) .ti {
  background: #1f2937;
}

.ti-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ti-label { font-size: .78rem; font-weight: 600; color: #6b7280; }
:global(.dark) .ti-label { color: #9ca3af; }
.ti-vol   { font-size: .95rem; font-weight: 800; transition: color .3s; }

/* track */
.ti-track {
  height: 9px;
  background: #f3f4f6;
  border-radius: 99px;
  overflow: hidden;
}
:global(.dark) .ti-track { background: #374151; }
.ti-fill {
  height: 100%;
  border-radius: 99px;
  transition: width .5s cubic-bezier(.4,0,.2,1), background .3s;
  min-width: 3px;
}
.ti-range { font-size: .68rem; color: #9ca3af; text-align: right; margin-top: -4px; }

/* status */
.ti-status {
  display: flex;
  align-items: center;
  gap: 10px;
  background: var(--bg);
  border-radius: 10px;
  padding: 9px 11px;
  transition: background .3s;
}
:global(.dark) .ti-status { background: var(--bgd); }

.ti-vehicle-img  { width: 40px; height: 40px; object-fit: contain; flex-shrink: 0; }
.ti-vehicle-emoji { font-size: 2rem; flex-shrink: 0; }
.ti-text { display: flex; flex-direction: column; gap: 2px; }
.ti-msg  { font-size: .82rem; font-weight: 700; margin: 0; transition: color .3s; }
.ti-sub  { font-size: .7rem; color: #6b7280; margin: 0; }
:global(.dark) .ti-sub { color: #9ca3af; }

/* price row */
.ti-price-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px dashed #e5e7eb;
  padding-top: 7px;
}
:global(.dark) .ti-price-row { border-color: #374151; }
.ti-vehicle-name { font-size: .78rem; font-weight: 600; color: #374151; }
:global(.dark) .ti-vehicle-name { color: #d1d5db; }
.ti-price { font-size: .82rem; font-weight: 800; transition: color .3s; }

.ti-empty { font-size: .7rem; color: #9ca3af; text-align: center; margin: 0; font-style: italic; }
</style>