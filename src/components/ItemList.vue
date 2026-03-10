<script setup>
import Item from './Item.vue'

defineProps({
  items: Array
})

const emit = defineEmits(['addToFavorite', 'addToCart'])
</script>

<template>
  <div class="all-products-list product-items-list">
    <div
      class="grid grid-cols-1 min-[379px]:grid-cols-2 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-2 xs:gap-3 sm:gap-4 regular-products-grid"
    >
      <Item
        v-for="item in items"
        :key="item.id"
        :id="item.id"
        :title="item.title"
        :image-url="item.imageUrl"
        :price_per_unit="Number(item.price_per_unit)"
        :price_per_cubic_meter="item.price_per_cubic_meter ? Number(item.price_per_cubic_meter) : null"
        :price_per_square_meter="item.price_per_square_meter ? Number(item.price_per_square_meter) : null"
        :price_per_linear_meter="item.price_per_linear_meter ? Number(item.price_per_linear_meter) : null"
        :volume_per_unit="item.volume_per_unit ? Number(item.volume_per_unit) : 0"
        :estimated_volume="item.estimated_volume ? Number(item.estimated_volume) : 0"
        :primary_unit="item.primary_unit"
        :unit_value="item.unit_value"
        :unit_label="item.unit_label"
        :isFavorite="item.isFavorite"
        :custom_url="item.custom_url"
        :product_type="item.product_type"
        :onClickFavorite="() => emit('addToFavorite', item)"
        :onClickAdd="(itemData) => emit('addToCart', itemData)"
        :isAdded="item.isAdded"
        :is_available="item.is_available"
        :quantity="item.quantity"
        :is_featured="item.is_featured"
      />
    </div>
  </div>
</template>

<style scoped>
/* Adjust the gap between items at different screen sizes */
@media (max-width: 640px) {
  .grid {
    gap: 8px;
  }
}

@media (max-width: 378px) {
  .grid {
    gap: 12px;
  }
}

/* Adjust grid columns at specific breakpoints to match the requirements */
@media (min-width: 441px) and (max-width: 669px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 670px) and (max-width: 900px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 901px) and (max-width: 1200px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1201px) and (max-width: 1600px) {
  .grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

@media (min-width: 1601px) {
  .grid {
    grid-template-columns: repeat(5, 1fr);
  }
}
</style>
