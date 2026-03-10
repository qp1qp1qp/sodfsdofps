import { watch } from 'vue'

export function useFavoriteSync(items, favorites) {
    watch(
        favorites,
        (newFavorites) => {
            let hasChanges = false
            const updated = [...items.value]
            updated.forEach(item => {
                const should = newFavorites.includes(item.id)
                if (item.isFavorite !== should) {
                    item.isFavorite = should
                    hasChanges = true
                }
            })
            if (hasChanges) items.value = updated
        },
        { deep: true }
    )
}