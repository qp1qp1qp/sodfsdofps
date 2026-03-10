<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const options = [
  { id: 'bath',    label: 'Баня',    icon: '🛁' },
  { id: 'house',   label: 'Дом',     icon: '🏡' },
  { id: 'fence',   label: 'Забор',   icon: '🔧' },
  { id: 'terrace', label: 'Терраса', icon: '🌿' },
  { id: 'roof',    label: 'Крыша',   icon: '🏚️' },
  { id: 'floor',   label: 'Пол',     icon: '🪵' },
]

const select = (id) => router.push({ path: '/quiz', query: { answer: id } })
</script>

<template>
  <div class="hq">
    <div class="hq__badge">⚡ Быстрый подбор</div>
    <h2 class="hq__title">Что планируете строить или отделывать?</h2>
    <p class="hq__sub">Выберите — подберём материал за 1 минуту</p>
    <div class="hq__grid">
      <button v-for="opt in options" :key="opt.id" class="hq__btn" @click="select(opt.id)">
        <span class="hq__icon">{{ opt.icon }}</span>
        <span class="hq__label">{{ opt.label }}</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.hq { display: flex; flex-direction: column; align-items: flex-start; gap: 14px; max-width: 520px; }

.hq__badge {
  display: inline-flex; align-items: center; gap: 6px;
  background: rgba(34,197,94,0.85); color: white;
  font-size: .75rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase;
  padding: 4px 12px; border-radius: 99px; backdrop-filter: blur(4px);
}

.hq__title {
  font-size: clamp(1.4rem, 3vw, 2.2rem); font-weight: 800; color: white;
  line-height: 1.2; margin: 0; text-shadow: 0 2px 12px rgba(0,0,0,.4);
}

.hq__sub { font-size: .95rem; color: rgba(255,255,255,.8); margin: 0; }

.hq__grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 10px; width: 100%; }

.hq__btn {
  display: flex; flex-direction: column; align-items: center; gap: 6px;
  padding: 12px 8px;
  background: rgba(255,255,255,.15); backdrop-filter: blur(8px);
  border: 1.5px solid rgba(255,255,255,.3); border-radius: 14px;
  color: white; cursor: pointer; transition: all .2s ease; font-size: .85rem;
}
.hq__btn:hover {
  background: rgba(255,255,255,.28); border-color: rgba(255,255,255,.7);
  transform: translateY(-3px); box-shadow: 0 8px 20px rgba(0,0,0,.2);
}

.hq__icon { font-size: 1.6rem; line-height: 1; }
.hq__label { font-weight: 600; text-align: center; line-height: 1.2; }

@media (max-width: 480px) {
  .hq__grid { gap: 8px; }
  .hq__btn { padding: 10px 6px; }
  .hq__icon { font-size: 1.3rem; }
  .hq__label { font-size: .72rem; }
}
</style>