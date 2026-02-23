import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/'

const api = axios.create({
  baseURL: BASE_URL,
  withCredentials: true, // Используем сессии Django вместо API ключа
  headers: {
    'Content-Type': 'application/json',
  }
})

// Добавляем CSRF-токен для секьющих запросов (Django CSRF) 
function getCookie(name) {
  const value = `; ${document.cookie}`
  const parts = value.split(`; ${name}=`)
  if (parts.length === 2) return parts.pop().split(';').shift()
  return null
}

api.interceptors.request.use((config) => {
  const method = config.method?.toUpperCase()
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrfToken = getCookie('csrftoken')
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken
    }
  }
  return config
})

// Обработчик ошибок для всех запросов
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Логируем ошибки, но не в консоль в production
    if (import.meta.env.DEV) {
      console.error('API Error:', error.response?.data || error.message)
    }
    return Promise.reject(error)
  }
)

export const getProducts = (params) => {
  return api.get('/products/', { params })
}

export const getFeaturedProducts = (limit = 10) => {
  return getProducts({ is_featured: true, limit })
}

export const getProduct = (id) => api.get(`/products/${id}/`)
export const getFavorites = () => api.get('/favorites/')
export const addFavorite = (productId) =>
  api.post(`/favorites/toggle/${productId}/`)
    .then(response => response.data)
    .catch(error => {
      if (import.meta.env.DEV) {
        console.error('Error adding favorite:', error);
      }
      throw error;
    });
export const removeFavorite = (productId) =>
  api.delete(`/favorites/toggle/${productId}/`).then((response) => response.data)
export const getHeroImages = () => api.get('/hero-images/')
export const getGalleryImages = () => api.get('/gallery-images/')
export const createOrder = (orderData) => api.post('/orders/', orderData)
let productTypesCache = null;
let productTypesCacheTime = 0;
const CACHE_DURATION = 60000; // 60 seconds

export const getProductTypes = () => {
  const now = Date.now();
  if (productTypesCache && (now - productTypesCacheTime < CACHE_DURATION)) {
    return productTypesCache;
  }

  productTypesCache = api.get('/product-types/');
  productTypesCacheTime = now;

  productTypesCache.catch(() => {
    productTypesCache = null;
  });

  return productTypesCache;
}
export const getProductTypeBySlug = (slug) => api.get(`/product-types/${slug}/`)
export const getCharacteristics = (params) => api.get('/characteristics/', { params })
export const getProductByCustomUrl = (customUrl) => api.get(`/products/by-custom-url/${customUrl}/`)

export default api
