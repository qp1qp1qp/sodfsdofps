<template>
  <div class="bubbles-container">
    <canvas ref="bubblesCanvas" class="bubbles-canvas"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';

const bubblesCanvas = ref(null);
const bubbles = ref([]);
const isLowPowerMode = ref(false);
const isMobile = ref(false);
let ctx = null;
let animationFrameId = null;
let lastFrameTime = 0;
let frameSkip = 0;

// Адаптивное количество пузырей в зависимости от устройства и производительности
const bubbleCount = computed(() => {
  if (isLowPowerMode.value) return 15;
  if (isMobile.value) return 30;
  return 50;
});

// Обнаружение мобильных устройств и низкопроизводительных устройств
const detectDeviceCapabilities = () => {
  // Проверка на мобильное устройство
  isMobile.value = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) || window.innerWidth < 768;
  
  // Проверка на низкую производительность
  // Если первые 10 кадров анимации рендерятся медленнее 30 FPS
  let frameCount = 0;
  let totalFrameTime = 0;
  
  const checkPerformance = (timestamp) => {
    if (frameCount === 0) {
      lastFrameTime = timestamp;
      frameCount++;
      requestAnimationFrame(checkPerformance);
      return;
    }
    
    const frameTime = timestamp - lastFrameTime;
    totalFrameTime += frameTime;
    lastFrameTime = timestamp;
    frameCount++;
    
    if (frameCount < 10) {
      requestAnimationFrame(checkPerformance);
    } else {
      const avgFPS = 1000 / (totalFrameTime / 10);
      isLowPowerMode.value = avgFPS < 30;
      console.log(`Detected device performance: ${avgFPS.toFixed(2)} FPS, low power mode: ${isLowPowerMode.value}`);
      
      // Настройка частоты обновления
      frameSkip = isLowPowerMode.value ? 2 : (isMobile.value ? 1 : 0);
      
      // Инициализация пузырей и запуск анимации
      initBubbles();
      startAnimation();
    }
  };
  
  requestAnimationFrame(checkPerformance);
};

const initCanvas = () => {
  const canvas = bubblesCanvas.value;
  if (!canvas) return;
  
  ctx = canvas.getContext('2d');
  
  // Установка размеров canvas в соответствии с размерами окна
  const setCanvasSize = () => {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
    
    // При изменении размера адаптируем положения пузырей
    if (bubbles.value.length) {
      bubbles.value.forEach(bubble => {
        if (bubble.x > canvas.width) bubble.x = Math.random() * canvas.width;
        if (bubble.y > canvas.height) bubble.y = Math.random() * canvas.height;
      });
    }
  };
  
  setCanvasSize();
  window.addEventListener('resize', setCanvasSize);
};

const initBubbles = () => {
  // Очистка существующих пузырей
  bubbles.value = [];
  
  // Создание новых пузырей с адаптивным количеством
  bubbles.value = Array.from({ length: bubbleCount.value }, (_, i) => {
    // Определяем, будет ли пузырь размещен у края
    const nearEdge = Math.random() < 0.7;
    
    let x, y;
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    if (nearEdge) {
      // Размещение возле одного из краев
      const edge = Math.floor(Math.random() * 4);
      
      switch (edge) {
        case 0: // верх
          x = Math.random() * width;
          y = Math.random() * (height * 0.2);
          break;
        case 1: // право
          x = width - Math.random() * (width * 0.2);
          y = Math.random() * height;
          break;
        case 2: // низ
          x = Math.random() * width;
          y = height - Math.random() * (height * 0.2);
          break;
        case 3: // лево
          x = Math.random() * (width * 0.2);
          y = Math.random() * height;
          break;
      }
    } else {
      // Случайное положение в любом месте
      x = Math.random() * width;
      y = Math.random() * height;
    }
    
    // Оптимизация размеров и цветов для производительности
    const size = isLowPowerMode.value 
      ? Math.random() * 15 + 10 // Более крупные, но меньше пузырей для низкой производительности
      : Math.random() * 20 + 5;
      
    // Использование заранее определенных цветов вместо случайных
    const colorSet = [
      'rgba(173, 216, 230, 0.3)', // светло-голубой
      'rgba(135, 206, 235, 0.3)', // небесно-голубой
      'rgba(176, 224, 230, 0.3)', // голубовато-серый
      'rgba(100, 149, 237, 0.3)', // васильковый
      'rgba(154, 206, 235, 0.3)'  // средне-голубой
    ];
    
    return {
      id: i,
      x,
      y,
      size,
      color: colorSet[Math.floor(Math.random() * colorSet.length)],
      // Более медленная анимация для экономии ресурсов
      animationDuration: 4 + Math.random() * 6,
      offsetX: Math.random() * 100 - 50, // Меньший диапазон движения
      offsetY: Math.random() * 100 - 50, // Меньший диапазон движения
      startTime: Date.now(),
      initialX: x,
      initialY: y,
      phaseOffset: Math.random() * Math.PI * 2, // Фазовый сдвиг для естественного движения
      visible: true // Флаг видимости для оптимизации
    };
  });
};

const startAnimation = () => {
  let frameCount = 0;
  
  const animate = (timestamp) => {
    // Пропуск кадров для экономии ресурсов
    frameCount++;
    if (frameSkip > 0 && frameCount % (frameSkip + 1) !== 0) {
      animationFrameId = requestAnimationFrame(animate);
      return;
    }
    
    // Очистка canvas
    ctx.clearRect(0, 0, bubblesCanvas.value.width, bubblesCanvas.value.height);
    
    const currentTime = Date.now();
    const width = bubblesCanvas.value.width;
    const height = bubblesCanvas.value.height;
    
    // Отрисовка каждого пузыря
    bubbles.value.forEach(bubble => {
      // Обновление позиции с использованием тригонометрических функций
      const elapsed = currentTime - bubble.startTime;
      const xFactor = Math.sin((elapsed / (bubble.animationDuration * 1000)) * Math.PI + bubble.phaseOffset);
      const yFactor = Math.cos((elapsed / (bubble.animationDuration * 1000)) * Math.PI + bubble.phaseOffset);
      
      bubble.x = bubble.initialX + bubble.offsetX * xFactor;
      bubble.y = bubble.initialY + bubble.offsetY * yFactor;
      
      // Проверка, находится ли пузырь в видимой области
      bubble.visible = (
        bubble.x + bubble.size > 0 && 
        bubble.x - bubble.size < width && 
        bubble.y + bubble.size > 0 && 
        bubble.y - bubble.size < height
      );
      
      // Рисуем только видимые пузыри
      if (bubble.visible) {
        // Использование встроенной функции для рисования круга
        ctx.beginPath();
        ctx.arc(bubble.x, bubble.y, bubble.size, 0, Math.PI * 2);
        ctx.fillStyle = bubble.color;
        ctx.fill();
      }
    });
    
    animationFrameId = requestAnimationFrame(animate);
  };
  
  animationFrameId = requestAnimationFrame(animate);
};

// Обработчик видимости страницы
const handleVisibilityChange = () => {
  if (document.hidden) {
    // Останавливаем анимацию, если страница не видна
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  } else {
    // Возобновляем анимацию, когда страница снова видна
    if (!animationFrameId) {
      startAnimation();
    }
  }
};

onMounted(() => {
  initCanvas();
  detectDeviceCapabilities();
  
  // Добавляем обработчик видимости страницы
  document.addEventListener('visibilitychange', handleVisibilityChange);
  
  // Обработчик для потери фокуса окна
  window.addEventListener('blur', () => {
    if (animationFrameId) {
      cancelAnimationFrame(animationFrameId);
      animationFrameId = null;
    }
  });
  
  // Обработчик для возвращения фокуса
  window.addEventListener('focus', () => {
    if (!animationFrameId) {
      startAnimation();
    }
  });
});

onUnmounted(() => {
  // Очистка ресурсов при размонтировании компонента
  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }
  
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  window.removeEventListener('resize', () => {});
  window.removeEventListener('blur', () => {});
  window.removeEventListener('focus', () => {});
});
</script>

<style scoped>
.bubbles-container {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom right, #f0f4ff, #e6e9ff); /* Светлый градиент */
  overflow: hidden;
}

:root.dark .bubbles-container {
  background: linear-gradient(to bottom right, #1a1c20, #2c3e50); /* Темный градиент */
}

.bubbles-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
</style>