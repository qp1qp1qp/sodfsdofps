<script setup>
import { ref, computed, onMounted, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import Footer from '../components/Footer.vue'
import api from '../api'
import { useHead } from '@vueuse/head'

useHead({
  title: 'Подбор пиломатериалов | WoodDon',
  meta: [
    { name: 'description', content: 'Ответьте на 4 вопроса и получите персональную рекомендацию по пиломатериалам от WoodDon.' },
    { name: 'keywords', content: 'подбор пиломатериалов, брус доска вагонка блок-хаус, WoodDon Ростов' }
  ]
})

const router = useRouter()
const route  = useRoute()
const { isDarkMode } = inject('theme', { isDarkMode: ref(false) })

// ─── Данные ──────────────────────────────────────────────────────────────────
const allMaterials = [
  { id: 'blockhouse', label: 'Блок-хаус',         icon: '🏠' },
  { id: 'beam',       label: 'Брус',               icon: '🪜' },
  { id: 'board',      label: 'Доска обрезная',     icon: '📋' },
  { id: 'board_tu',   label: 'Доска обрезная ТУ',  icon: '📄' },
  { id: 'lining',     label: 'Евровагонка',        icon: '🪵' },
  { id: 'imitation',  label: 'Имитация бруса',     icon: '🏡' },
  { id: 'floor',      label: 'Половая доска',      icon: '🪣' },
  { id: 'unknown',    label: 'Не знаю',            icon: '🤷' },
]

const recommendations = {
  bath:    ['lining', 'blockhouse', 'imitation'],
  house:   ['blockhouse', 'imitation', 'beam'],
  fence:   ['board', 'board_tu'],
  terrace: ['floor', 'board', 'lining'],
  roof:    ['board', 'board_tu', 'beam'],
  floor:   ['floor', 'board_tu', 'lining'],
}

const structureLabels = {
  bath: 'Баня', house: 'Дом', fence: 'Забор',
  terrace: 'Терраса', roof: 'Крыша', floor: 'Пол'
}
const volumeLabels = {
  small: 'До 1 м³', medium: '1–5 м³', large: '5–20 м³',
  xlarge: 'Более 20 м³', unknown: 'Не знаю'
}
const timingLabels = {
  asap: 'Как можно скорее', week: 'В течение недели',
  month: 'В течение месяца', planning: 'Пока планирую'
}

const steps = [
  {
    id: 2,
    emoji: '🪵',
    text: 'Какой материал вас интересует?',
    // options формируются динамически
  },
  {
    id: 3,
    emoji: '📐',
    text: 'Какой объём вам нужен?',
    options: [
      { id: 'small',   label: 'До 1 м³',      sub: 'небольшой ремонт', icon: '🔨' },
      { id: 'medium',  label: '1–5 м³',        sub: 'строительство',   icon: '🏗️' },
      { id: 'large',   label: '5–20 м³',       sub: 'большой объект',  icon: '🏢' },
      { id: 'xlarge',  label: 'Более 20 м³',   sub: 'оптовая партия',  icon: '🚛' },
      { id: 'unknown', label: 'Не знаю',       sub: 'менеджер поможет',icon: '🤷' },
    ]
  },
  {
    id: 4,
    emoji: '📅',
    text: 'Когда вам нужны материалы?',
    options: [
      { id: 'asap',     label: 'Как можно скорее', icon: '⚡' },
      { id: 'week',     label: 'В течение недели', icon: '📆' },
      { id: 'month',    label: 'В течение месяца', icon: '🗓️' },
      { id: 'planning', label: 'Пока планирую',    icon: '💭' },
    ]
  }
]

// ─── Состояние ───────────────────────────────────────────────────────────────
const answers   = ref({})
const step      = ref(2)
const done      = ref(false)
const dir       = ref('forward')
const name      = ref('')
const phone     = ref('')
const email     = ref('')
const sending   = ref(false)
const showModal = ref(false)

// Ошибки валидации
const phoneError = ref('')
const emailError = ref('')

onMounted(() => {
  const a = route.query.answer
  if (a) answers.value[1] = a
})

// ─── Computed ────────────────────────────────────────────────────────────────
const materialOptions = computed(() => {
  const rec = recommendations[answers.value[1]] || []
  const sorted = allMaterials
    .filter(m => m.id !== 'unknown')
    .map(m => ({ ...m, recommended: rec.includes(m.id) }))
    .sort((a, b) => (b.recommended ? 1 : 0) - (a.recommended ? 1 : 0))
  // «Не знаю» всегда последний
  sorted.push({ id: 'unknown', label: 'Не знаю', icon: '🤷', recommended: false })
  return sorted
})

const currentStep = computed(() => {
  const s = steps.find(s => s.id === step.value)
  if (!s) return null
  return s.id === 2 ? { ...s, options: materialOptions.value } : s
})

const progress = computed(() => done.value ? 100 : Math.round(((step.value - 1) / 4) * 100))

const recHint = computed(() => {
  const sid = answers.value[1]
  if (!sid || step.value !== 2) return ''
  const labels = (recommendations[sid] || [])
    .map(id => allMaterials.find(m => m.id === id)?.label)
    .filter(Boolean).slice(0, 2).join(', ')
  return labels ? `💡 Рекомендуем для вашей задачи: ${labels}` : ''
})

const getMaterialLabel = (id) => allMaterials.find(m => m.id === id)?.label || id

const recommendedList = computed(() => {
  const sid = answers.value[1]
  const mid = answers.value[2]
  const base = recommendations[sid] || []
  const all = mid && mid !== 'unknown' ? [mid, ...base.filter(id => id !== mid)] : base
  return [...new Set(all)].slice(0, 3).map(getMaterialLabel).join(', ')
})

// Валидация — та же логика что в Checkout
const validatePhone = (val) => {
  const cleaned = val.replace(/[\s\-\(\)]/g, '')
  return /^\+?[78]?\d{10}$/.test(cleaned)
}
const validateEmail = (val) => {
  if (!val) return true
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val)
}

const isFormValid = computed(() =>
  name.value.trim().length >= 2 &&
  validatePhone(phone.value) &&
  validateEmail(email.value)
)

// ─── Методы ──────────────────────────────────────────────────────────────────
const pick = (optionId) => {
  answers.value[step.value] = optionId
  dir.value = 'forward'
  setTimeout(() => step.value < 4 ? step.value++ : done.value = true, 0)
}

const back = () => {
  dir.value = 'back'
  if (step.value > 2) step.value--
  else router.push('/')
}

const submit = async () => {
  // Показываем ошибки перед отправкой
  phoneError.value = validatePhone(phone.value) ? '' : 'Введите корректный номер телефона'
  emailError.value = validateEmail(email.value)  ? '' : 'Введите корректный email'
  if (!isFormValid.value || sending.value) return

  sending.value = true
  try {
    await api.post('/quiz/submit/', {
      name:        name.value.trim(),
      phone:       phone.value.trim(),
      email:       email.value.trim(),
      structure:   structureLabels[answers.value[1]] || answers.value[1] || '',
      material:    getMaterialLabel(answers.value[2]),
      volume:      volumeLabels[answers.value[3]] || '',
      timing:      timingLabels[answers.value[4]] || '',
      recommended: recommendedList.value,
    })
  } catch (e) {
    console.error('Quiz submit:', e)
  } finally {
    sending.value = false
    showModal.value = true
  }
}

const closeModal = () => { showModal.value = false; router.push('/') }
</script>

<template>
  <div :class="['qp', { dark: isDarkMode }]">

    <!-- SEO -->
    <div class="seo-only">
      <h1>Подбор пиломатериалов онлайн — WoodDon, Ростов-на-Дону</h1>
      <p>Ответьте на 4 вопроса и получите персональную рекомендацию: блок-хаус, брус, доска обрезная,
         доска ТУ, евровагонка, имитация бруса или половая доска.</p>
    </div>

    <div class="qp__inner">
      <!-- Прогресс -->
      <div class="qp__progress">
        <div class="qp__track">
          <div class="qp__fill" :style="{ width: progress + '%' }"></div>
        </div>
        <span class="qp__prog-label">
          {{ done ? 'Последний шаг!' : `Шаг ${step - 1} из 4` }}
        </span>
      </div>

      <Transition :name="dir === 'forward' ? 'sf' : 'sb'" mode="out-in">

        <!-- Финальная форма -->
        <div v-if="done" key="done" class="qp__card">
          <div class="qp__big-emoji">🎯</div>
          <h2 class="qp__title">Мы подберём лучшее предложение!</h2>

          <div class="qp__tags">
            <span v-if="answers[1]" class="qp__tag">🏗️ {{ structureLabels[answers[1]] }}</span>
            <span v-if="answers[2]" class="qp__tag">🪵 {{ getMaterialLabel(answers[2]) }}</span>
            <span v-if="answers[3]" class="qp__tag">📐 {{ volumeLabels[answers[3]] }}</span>
            <span v-if="answers[4]" class="qp__tag">📅 {{ timingLabels[answers[4]] }}</span>
          </div>

          <p class="qp__hint-text">Оставьте контакты — менеджер свяжется для уточнения деталей.</p>

          <div class="qp__form">
            <input
              v-model="name"
              type="text"
              placeholder="Ваше имя *"
              class="qp__input"
            />

            <div class="qp__field">
              <input
                v-model="phone"
                type="tel"
                placeholder="+7 (999) 999-99-99 *"
                class="qp__input"
                :class="{ 'qp__input--err': phoneError }"
                @blur="phoneError = validatePhone(phone) ? '' : 'Введите корректный номер телефона'"
              />
              <p v-if="phoneError" class="qp__err">{{ phoneError }}</p>
            </div>

            <div class="qp__field">
              <input
                v-model="email"
                type="email"
                placeholder="Email (необязательно)"
                class="qp__input"
                :class="{ 'qp__input--err': emailError }"
                @blur="emailError = validateEmail(email) ? '' : 'Введите корректный email'"
              />
              <p v-if="emailError" class="qp__err">{{ emailError }}</p>
            </div>

            <button
              class="qp__submit"
              :disabled="!isFormValid || sending"
              @click="submit"
            >
              <template v-if="sending">
                <svg class="qp__spin" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"
                    stroke-dasharray="30 60" stroke-linecap="round"/>
                </svg>
                Отправляем...
              </template>
              <template v-else>Получить расчёт →</template>
            </button>

            <p class="qp__privacy">Нажимая кнопку, вы соглашаетесь на обработку персональных данных</p>
          </div>

          <button class="qp__back" @click="done = false; step = 4">← Изменить ответы</button>
        </div>

        <!-- Вопрос -->
        <div v-else :key="step" class="qp__card">
          <div class="qp__big-emoji">{{ currentStep?.emoji }}</div>
          <h2 class="qp__title">{{ currentStep?.text }}</h2>
          <p v-if="recHint" class="qp__rec-hint">{{ recHint }}</p>

          <div :class="['qp__grid', step === 2 && 'qp__grid--wide']">
            <button
              v-for="opt in currentStep?.options"
              :key="opt.id"
              :class="[
                'qp__opt',
                answers[step] === opt.id && 'qp__opt--sel',
                opt.recommended && 'qp__opt--rec',
                opt.id === 'unknown' && 'qp__opt--unknown'
              ]"
              @click="pick(opt.id)"
            >
              <span v-if="opt.recommended" class="qp__star">★</span>
              <span class="qp__opt-icon">{{ opt.icon }}</span>
              <span class="qp__opt-label">{{ opt.label }}</span>
              <span v-if="opt.sub" class="qp__opt-sub">{{ opt.sub }}</span>
            </button>
          </div>

          <button class="qp__back" @click="back">← Назад</button>
        </div>

      </Transition>
    </div>

    <!-- Модалка успеха — закрыть только кнопкой -->
    <Transition name="modal">
      <div v-if="showModal" class="qp__overlay">
        <div class="qp__modal">
          <svg class="qp__check" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="11" stroke="#22c55e" stroke-width="2"/>
            <path d="M7 12.5l3.5 3.5 6.5-7" stroke="#22c55e" stroke-width="2.5"
              stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
          <h2 class="qp__modal-title">Заявка принята!</h2>
          <p class="qp__modal-text">Наш менеджер свяжется с вами для подтверждения деталей.</p>
          <p class="qp__modal-text">Если хотите — позвоните сами:</p>
          <a href="tel:+79885160320" class="qp__modal-call">📞 +7 (988) 516-03-20</a>
          <button class="qp__modal-btn" @click="closeModal">На главную</button>
        </div>
      </div>
    </Transition>

    <Footer />
  </div>
</template>

<style scoped>
.qp {
  min-height: 100vh; display: flex; flex-direction: column;
  background: linear-gradient(135deg,#f0fdf4 0%,#dcfce7 50%,#f0fdf4 100%);
}
.qp.dark { background: linear-gradient(135deg,#0f1a0f 0%,#111f11 50%,#0f1a0f 100%); }

.seo-only {
  position: absolute; width: 1px; height: 1px;
  overflow: hidden; clip: rect(0,0,0,0); white-space: nowrap;
}

.qp__inner {
  flex: 1; display: flex; flex-direction: column;
  align-items: center; padding: 100px 16px 48px; gap: 20px;
}

/* Progress */
.qp__progress { width: 100%; max-width: 580px; display: flex; flex-direction: column; gap: 6px; }
.qp__track { height: 7px; border-radius: 99px; overflow: hidden; background: #d1fae5; }
.dark .qp__track { background: #14290f; }
.qp__fill {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg,#22c55e,#15803d);
  transition: width .5s ease;
}
.qp__prog-label { font-size: .8rem; color: #6b7280; align-self: flex-end; }
.dark .qp__prog-label { color: #9ca3af; }

/* Card */
.qp__card {
  width: 100%; max-width: 580px;
  background: #fff; border-radius: 24px; padding: 36px 32px;
  box-shadow: 0 20px 60px rgba(0,0,0,.08);
  display: flex; flex-direction: column; align-items: center; gap: 20px;
}
.dark .qp__card { background: #1f2937; box-shadow: 0 20px 60px rgba(0,0,0,.45); }

.qp__big-emoji { font-size: 3rem; line-height: 1; }
.qp__title {
  font-size: 1.45rem; font-weight: 700; color: #111827;
  text-align: center; line-height: 1.3; margin: 0;
}
.dark .qp__title { color: #f9fafb; }

.qp__rec-hint {
  font-size: .82rem; color: #16a34a; background: #dcfce7;
  border-radius: 8px; padding: 6px 14px; margin: 0; text-align: center;
}
.dark .qp__rec-hint { background: #14532d; color: #86efac; }

.qp__hint-text { text-align: center; color: #6b7280; font-size: .95rem; line-height: 1.6; margin: 0; }
.dark .qp__hint-text { color: #9ca3af; }

/* Options */
.qp__grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; width: 100%; }
.qp__grid--wide { grid-template-columns: repeat(auto-fill, minmax(128px,1fr)); }

.qp__opt {
  position: relative; display: flex; flex-direction: column;
  align-items: center; gap: 6px; padding: 16px 12px;
  border: 2px solid #e5e7eb; border-radius: 16px;
  background: #fff; cursor: pointer; text-align: center;
  transition: all .2s ease;
}
.dark .qp__opt { background: #374151; border-color: #4b5563; }
.qp__opt:hover {
  border-color: #22c55e; background: #f0fdf4;
  transform: translateY(-2px); box-shadow: 0 4px 12px rgba(34,197,94,.15);
}
.dark .qp__opt:hover { background: #1c3a20; border-color: #22c55e; }
.qp__opt--sel  { border-color: #16a34a !important; background: #dcfce7 !important; }
.dark .qp__opt--sel  { background: #14532d !important; }
.qp__opt--rec  { border-color: #86efac; }
.dark .qp__opt--rec  { border-color: #166534; }
/* «Не знаю» — чуть приглушённый */
.qp__opt--unknown { opacity: .75; }
.qp__opt--unknown:hover { opacity: 1; }

.qp__star { position: absolute; top: 6px; right: 8px; font-size: .65rem; color: #16a34a; font-weight: 700; }
.qp__opt-icon  { font-size: 1.8rem; }
.qp__opt-label { font-size: .83rem; font-weight: 600; color: #374151; line-height: 1.3; }
.dark .qp__opt-label { color: #e5e7eb; }
.qp__opt-sub   { font-size: .7rem; color: #9ca3af; }

/* Tags */
.qp__tags  { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.qp__tag {
  background: #dcfce7; color: #15803d;
  border-radius: 99px; padding: 4px 12px; font-size: .8rem; font-weight: 600;
}
.dark .qp__tag { background: #14532d; color: #86efac; }

/* Form */
.qp__form { width: 100%; display: flex; flex-direction: column; gap: 10px; }
.qp__field { width: 100%; display: flex; flex-direction: column; gap: 4px; }

.qp__input {
  width: 100%; padding: 12px 16px;
  border: 2px solid #e5e7eb; border-radius: 12px;
  font-size: .95rem; outline: none; transition: border-color .2s;
  box-sizing: border-box; background: #fff; color: #111827;
}
.dark .qp__input { background: #374151; border-color: #4b5563; color: #f9fafb; }
.qp__input:focus { border-color: #22c55e; }
.qp__input::placeholder { color: #9ca3af; }
.qp__input--err { border-color: #ef4444 !important; }

.qp__err { font-size: .78rem; color: #ef4444; margin: 0; }

.qp__submit {
  width: 100%; padding: 14px;
  background: linear-gradient(135deg,#22c55e,#16a34a);
  color: #fff; border: none; border-radius: 12px;
  font-size: 1rem; font-weight: 700; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  transition: opacity .2s, transform .2s;
}
.qp__submit:hover:not(:disabled) { opacity: .9; transform: translateY(-1px); }
.qp__submit:disabled { opacity: .45; cursor: not-allowed; }

.qp__spin { width: 18px; height: 18px; animation: spin .8s linear infinite; }
@keyframes spin { to { transform: rotate(360deg); } }

.qp__privacy { text-align: center; font-size: .72rem; color: #9ca3af; margin: 0; }

.qp__back {
  background: none; border: none; color: #9ca3af;
  font-size: .85rem; cursor: pointer; padding: 4px 8px;
  border-radius: 8px; transition: color .2s; align-self: flex-start;
}
.qp__back:hover { color: #6b7280; }

/* Modal */
.qp__overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.55);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; padding: 16px;
}
.qp__modal {
  background: #fff; border-radius: 24px; padding: 40px 32px;
  max-width: 420px; width: 100%;
  display: flex; flex-direction: column; align-items: center; gap: 16px;
  box-shadow: 0 25px 80px rgba(0,0,0,.2);
}
.dark .qp__modal { background: #1f2937; }

.qp__check { width: 64px; height: 64px; }
.qp__modal-title { font-size: 1.6rem; font-weight: 800; color: #111827; text-align: center; margin: 0; }
.dark .qp__modal-title { color: #f9fafb; }
.qp__modal-text { text-align: center; color: #6b7280; font-size: .95rem; margin: 0; }
.dark .qp__modal-text { color: #9ca3af; }

.qp__modal-call {
  display: inline-flex; align-items: center; gap: 8px;
  background: linear-gradient(135deg,#22c55e,#16a34a);
  color: #fff; text-decoration: none; padding: 12px 28px;
  border-radius: 99px; font-weight: 700; font-size: 1rem; transition: opacity .2s;
}
.qp__modal-call:hover { opacity: .9; }

.qp__modal-btn {
  width: 100%; padding: 12px;
  background: #f3f4f6; color: #374151;
  border: none; border-radius: 12px;
  font-size: .95rem; font-weight: 600; cursor: pointer; transition: background .2s;
}
.dark .qp__modal-btn { background: #374151; color: #e5e7eb; }
.qp__modal-btn:hover { background: #e5e7eb; }
.dark .qp__modal-btn:hover { background: #4b5563; }

/* Transitions */
.sf-enter-active,.sf-leave-active,.sb-enter-active,.sb-leave-active { transition: all .3s ease; }
.sf-enter-from { opacity: 0; transform: translateX(40px); }
.sf-leave-to   { opacity: 0; transform: translateX(-40px); }
.sb-enter-from { opacity: 0; transform: translateX(-40px); }
.sb-leave-to   { opacity: 0; transform: translateX(40px); }

.modal-enter-active,.modal-leave-active { transition: all .25s ease; }
.modal-enter-from,.modal-leave-to { opacity: 0; }

@media (max-width: 480px) {
  .qp__card { padding: 24px 16px; }
  .qp__title { font-size: 1.2rem; }
  .qp__grid { gap: 8px; }
  .qp__grid--wide { grid-template-columns: repeat(auto-fill,minmax(100px,1fr)); }
  .qp__opt { padding: 12px 8px; }
  .qp__opt-icon { font-size: 1.4rem; }
  .qp__opt-label { font-size: .75rem; }
}
</style>