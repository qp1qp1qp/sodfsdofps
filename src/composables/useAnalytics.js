import { onMounted, onUnmounted } from 'vue'
import analytics from '@/utils/analytics'

export function useAnalytics(pageName) {
  let pageStartTime

  onMounted(() => {
    pageStartTime = Date.now()
    analytics.trackPageView(pageName)
  })

  onUnmounted(() => {
    if (pageStartTime) {
      const duration = (Date.now() - pageStartTime) / 1000
      analytics.trackTimeOnPage(pageName, duration)
    }
  })

  return {
    trackClick: analytics.trackClick.bind(analytics),
    trackAddToCart: analytics.trackAddToCart.bind(analytics),
    trackToggleFavorite: analytics.trackToggleFavorite.bind(analytics),
    trackSearch: analytics.trackSearch.bind(analytics),
  }
}


// Пример использования в компоненте:
/*
<script setup>
import { useAnalytics } from '@/composables/useAnalytics'

const { trackClick, trackAddToCart } = useAnalytics('ProductPage')

const handleAddToCart = (product) => {
  trackAddToCart(product)
  // ... остальная логика
}

const handleFilterClick = (filterName) => {
  trackClick('filter', { filter_name: filterName })
}
</script>
*/