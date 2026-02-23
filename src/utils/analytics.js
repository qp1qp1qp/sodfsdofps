class Analytics {
  constructor() {
    this.sessionId = this.getOrCreateSessionId()
    this.events = []
    this.flushInterval = 30000 // Отправка данных каждые 30 секунд
    this.startFlushTimer()
  }

  /**
   * Получает или создает ID сессии
   */
  getOrCreateSessionId() {
    let sessionId = sessionStorage.getItem('analytics_session_id')
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      sessionStorage.setItem('analytics_session_id', sessionId)
    }
    return sessionId
  }

  /**
   * Записывает событие
   */
  track(eventName, properties = {}) {
    const event = {
      event_name: eventName,
      timestamp: new Date().toISOString(),
      session_id: this.sessionId,
      url: window.location.href,
      properties: {
        ...properties,
        user_agent: navigator.userAgent,
        screen_resolution: `${window.screen.width}x${window.screen.height}`,
        viewport_size: `${window.innerWidth}x${window.innerHeight}`,
      }
    }

    this.events.push(event)

    // Логируем в консоль для разработки
    console.log('[Analytics]', eventName, properties)

    // Если накопилось слишком много событий, отправляем
    if (this.events.length >= 10) {
      this.flush()
    }
  }

  /**
   * Отслеживание клика по элементу
   */
  trackClick(elementName, additionalData = {}) {
    this.track('click', {
      element: elementName,
      ...additionalData
    })
  }

  /**
   * Отслеживание просмотра страницы
   */
  trackPageView(pageName, additionalData = {}) {
    this.track('page_view', {
      page: pageName,
      referrer: document.referrer,
      ...additionalData
    })
  }

  /**
   * Отслеживание добавления в корзину
   */
  trackAddToCart(product) {
    this.track('add_to_cart', {
      product_id: product.id,
      product_title: product.title,
      quantity: product.quantity,
      price: product.price_per_unit
    })
  }

  /**
   * Отслеживание добавления в избранное
   */
  trackToggleFavorite(product, isAdding) {
    this.track('toggle_favorite', {
      product_id: product.id,
      product_title: product.title,
      action: isAdding ? 'add' : 'remove'
    })
  }

  /**
   * Отслеживание поиска
   */
  trackSearch(searchQuery, resultsCount) {
    this.track('search', {
      query: searchQuery,
      results_count: resultsCount
    })
  }

  /**
   * Отслеживание создания заказа
   */
  trackOrder(orderData) {
    this.track('create_order', {
      order_number: orderData.order_number,
      total_price: orderData.total_price,
      items_count: orderData.items?.length || 0
    })
  }

  /**
   * Отслеживание времени на странице
   */
  trackTimeOnPage(pageName, duration) {
    this.track('time_on_page', {
      page: pageName,
      duration_seconds: duration
    })
  }

  /**
   * Отправка накопленных событий на сервер
   */
  async flush() {
    if (this.events.length === 0) return

    const eventsToSend = [...this.events]
    this.events = []

    try {
      // Импортируем API конфигурацию
      const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/'

      // Отправляем события на backend endpoint для аналитики
      // Используем сессии Django (credentials: 'include') вместо API ключа
      const response = await fetch(`${BASE_URL}analytics/events/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include', // Для отправки cookies/session Django
        body: JSON.stringify({
          events: eventsToSend
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      console.log('[Analytics] Sent', eventsToSend.length, 'events')
    } catch (error) {
      console.error('[Analytics] Error sending events:', error)
      // Возвращаем события обратно при ошибке
      this.events = [...eventsToSend, ...this.events]
    }
  }

  /**
   * Запуск таймера для автоматической отправки
   */
  startFlushTimer() {
    setInterval(() => {
      this.flush()
    }, this.flushInterval)

    // Отправка при выходе со страницы
    window.addEventListener('beforeunload', () => {
      this.flush()
    })
  }
}

// Создаем глобальный экземпляр
const analytics = new Analytics()

// Экспортируем для использования в компонентах
export default analytics