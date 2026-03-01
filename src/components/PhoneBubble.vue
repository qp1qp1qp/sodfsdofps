<script setup>
import { ref } from 'vue'

const isExpanded = ref(true)

const toggle = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<template>
  <div class="phone-bubble-wrapper">
    <!-- ИСПРАВЛЕНИЕ 1: Один Transition вместо двух -->
    <Transition name="bubble">
      
      <!-- Свёрнутый вид — только кружок -->
      <button
        v-if="!isExpanded"
        class="bubble-collapsed"
        @click="toggle"
        aria-label="Позвонить нам"
      >
        <svg class="phone-icon" fill="currentColor" viewBox="0 0 24 24">
          <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
        </svg>
      </button>

      <!-- ИСПРАВЛЕНИЕ 2: v-else для развернутого вида -->
      <!-- Развёрнутый вид — карточка -->
      <div v-else class="bubble-expanded">
        <!-- Кнопка свернуть -->
        <button class="collapse-btn" @click="toggle" aria-label="Свернуть">
          <svg fill="currentColor" viewBox="0 0 24 24" class="w-3 h-3">
            <path d="M19 13H5v-2h14v2z"/>
          </svg>
        </button>

        <!-- Заголовок -->
        <p class="bubble-tagline">Закажи пиломатериалы</p>

        <!-- Телефон -->
        <a href="tel:+79885160320" class="bubble-phone">
          <span class="phone-icon-small">
            <svg fill="currentColor" viewBox="0 0 24 24" class="w-4 h-4">
              <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
            </svg>
          </span>
          +7 (988) 516-03-20
        </a>

        <!-- Адрес -->
        <div class="bubble-address">
          <svg fill="currentColor" viewBox="0 0 24 24" class="w-3 h-3 flex-shrink-0 mt-0.5">
            <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
          </svg>
          <span>пер. Нефтяной 2а, Ростов-на-Дону</span>
        </div>

        <!-- Кнопка звонка -->
        <a href="tel:+79885160320" class="bubble-call-btn">
          Позвонить
        </a>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.phone-bubble-wrapper {
  position: fixed;
  bottom: 28px;
  left: 28px;
  z-index: 9999;
}

/* ИСПРАВЛЕНИЕ 3: Позиционируем оба элемента абсолютно, чтобы они не толкали друг друга */
.bubble-collapsed,
.bubble-expanded {
  position: absolute;
  bottom: 0;
  left: 0;
  transform-origin: bottom left; /* Чтобы окно "вырастало" из левого нижнего угла */
}

/* Свёрнутый кружок */
.bubble-collapsed {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.45);
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  animation: vibrate 6s ease-in-out infinite;
}

.bubble-collapsed:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 24px rgba(34, 197, 94, 0.6);
}

.phone-icon {
  width: 24px;
  height: 24px;
}

/* Вибрация */
@keyframes vibrate {
  0%, 88%, 100% { transform: rotate(0deg); }
  90% { transform: rotate(-12deg); }
  92% { transform: rotate(12deg); }
  94% { transform: rotate(-10deg); }
  96% { transform: rotate(10deg); }
  98% { transform: rotate(-6deg); }
}

/* Развёрнутая карточка */
.bubble-expanded {
  background: white;
  border-radius: 16px;
  padding: 14px 16px;
  width: 220px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.2);

  position: absolute;
  bottom: 0;
  left: 0;
  transform-origin: bottom left;
  overflow: hidden; 
}

/* Полоска сверху */
.bubble-expanded::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #22c55e, #16a34a);
}

.collapse-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #f3f4f6;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: background 0.2s;
}

.collapse-btn:hover {
  background: #e5e7eb;
}

.bubble-tagline {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #22c55e;
  margin: 0 0 8px 0;
}

.bubble-phone {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.95rem;
  font-weight: 700;
  color: #111827;
  text-decoration: none;
  margin-bottom: 8px;
  transition: color 0.2s;
}

.bubble-phone:hover {
  color: #22c55e;
}

.phone-icon-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  animation: vibrate 6s ease-in-out infinite;
}

.bubble-address {
  display: flex;
  align-items: flex-start;
  gap: 5px;
  font-size: 0.72rem;
  color: #6b7280;
  margin-bottom: 12px;
  line-height: 1.4;
}

.bubble-address svg {
  color: #9ca3af;
}

.bubble-call-btn {
  display: block;
  width: 100%;
  text-align: center;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  text-decoration: none;
  padding: 8px 0;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  transition: opacity 0.2s, transform 0.2s;
}

.bubble-call-btn:hover {
  opacity: 0.9;
  transform: translateY(-1px);
}

/* Анимация появления/скрытия */
.bubble-enter-active,
.bubble-leave-active {
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1), transform 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ИСПРАВЛЕНИЕ 4: Сделал scale(0.5) вместо 0.85 и убрал translateY, 
так как с transform-origin: bottom left анимация масштабирования от угла выглядит красивее */
.bubble-enter-from,
.bubble-leave-to {
  opacity: 0;
  transform: scale(0.5);
}

/* Тёмная тема */
:root.dark .bubble-expanded {
  background: #1f2937;
  border-color: rgba(34, 197, 94, 0.3);
}

:root.dark .bubble-phone {
  color: #f9fafb;
}

:root.dark .bubble-phone:hover {
  color: #22c55e;
}

:root.dark .collapse-btn {
  background: #374151;
  color: #9ca3af;
}

:root.dark .collapse-btn:hover {
  background: #4b5563;
}

:root.dark .bubble-address {
  color: #9ca3af;
}
</style>