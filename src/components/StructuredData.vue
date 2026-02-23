<script setup>
import { onMounted, onUnmounted } from 'vue'

const structuredData = {
  '@context': 'https://schema.org',
  '@type': 'Organization',
  name: 'WoodDon',
  url: 'https://www.wooddon.ru',
  logo: 'https://www.wooddon.ru/logo.png',
  contactPoint: {
    '@type': 'ContactPoint',
    telephone: '+7-928-12-326-80',
    contactType: 'customer service'
  },
  address: {
    '@type': 'PostalAddress',
    addressLocality: 'Ростов-на-Дону',
    addressRegion: 'Ростовская область',
    postalCode: '344064',
    streetAddress: 'пер. Нефтяной 2а'
  },
  sameAs: [
    'https://www.facebook.com/wooddon',
    'https://www.instagram.com/wooddon_ru',
    'https://vk.com/wooddon'
  ]
}

onMounted(() => {
  const script = document.createElement('script')
  script.setAttribute('type', 'application/ld+json')
  script.textContent = JSON.stringify(structuredData)
  document.head.appendChild(script)
})

onUnmounted(() => {
  const script = document.head.querySelector('script[type="application/ld+json"]')
  if (script) {
    document.head.removeChild(script)
  }
})
</script>
