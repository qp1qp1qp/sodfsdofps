import './assets/main.css'

import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import { createHead } from '@vueuse/head'
import { autoAnimatePlugin } from '@formkit/auto-animate/vue'
import App from './App.vue'

import Home from './pages/Home.vue'
import AllProducts from './pages/AllProducts.vue'
import NewProducts from './pages/NewProducts.vue'
import Contacts from './pages/Contacts.vue'
import Delivery from './pages/Delivery.vue'
import About from './pages/About.vue'
import Favorites from './pages/Favorites.vue'
import ProductPage from './pages/ProductPage.vue'
import Checkout from './pages/Checkout.vue'
import Faq from './pages/Faq.vue'

const app = createApp(App)
const head = createHead()

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/all-products', name: 'AllProducts', component: AllProducts },
  { path: '/new-products', name: 'NewProducts', component: NewProducts },
  { path: '/contacts', name: 'Contacts', component: Contacts },
  { path: '/delivery', name: 'Delivery', component: Delivery },
  { path: '/about', name: 'About', component: About },
  { path: '/favorites', name: 'Favorites', component: Favorites },
  { path: '/all-products/:typeSlug', name: 'ProductsByType', component: AllProducts },
  { path: '/all-products/:typeSlug/:productSlug', name: 'ProductPage', component: ProductPage },
  { path: '/checkout', name: 'Checkout', component: Checkout },
  { path: '/faq', name: 'Faq', component: Faq }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {

    return new Promise((resolve) => {
      setTimeout(() => {
        resolve({ top: 0, behavior: 'auto' });
      }, 350);
    });
  }
})

app.use(head)
app.use(router)
app.use(autoAnimatePlugin)

// Добавляем класс переходного состояния страницы
router.beforeEach((to, from, next) => {
  document.body.classList.add('page-transitioning');
  document.dispatchEvent(new Event('page-transition-start'))
  next();
});

// Убираем класс переходного состояния после завершения перехода
router.afterEach(() => {
  setTimeout(() => {
    document.body.classList.remove('page-transitioning');
    document.dispatchEvent(new Event('page-transition-end'))
  }, 350);
});

app.mount('#app')
