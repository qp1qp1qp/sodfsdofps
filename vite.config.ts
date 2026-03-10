import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueJsx from '@vitejs/plugin-vue-jsx'
import VueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => ({
  plugins: [
    vue(),
    vueJsx(),
    // VueDevTools только для разработки
    mode !== 'production' ? VueDevTools() : undefined
  ].filter(Boolean),
  optimizeDeps: {
    include: ['vue', 'vue-router', 'keen-slider', 'vue-virtual-scroller']
  },
  build: {
    sourcemap: false, // отключаем sourcemap для production
    minify: 'terser', // лучшее сжатие
    terserOptions: {
      compress: {
        drop_console: true // удаляем console.log для production
      }
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
}))