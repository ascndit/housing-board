<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  listing: {
    type: Object,
    required: true
  },
  isFavorite: {
    type: Boolean,
    default: false
  }
})

defineEmits(['toggle-favorite', 'open-details'])

const imgFailed = ref(false)

const placeholderImage =
  'https://placehold.co/600x400/e2e8f0/475569?text=Нет+фотографии'

const mainPhoto = computed(() => {
  if (imgFailed.value || !props.listing.photos || props.listing.photos.length === 0) {
    return placeholderImage
  }
  return props.listing.photos[0]
})

const formattedPrice = computed(() => {
  if (props.listing.price === null || props.listing.price === undefined) {
    return 'Цена не указана'
  }
  return `${new Intl.NumberFormat('ru-RU').format(props.listing.price)} ₽/мес.`
})

const formattedRooms = computed(() => {
  if (props.listing.rooms === null || props.listing.rooms === undefined) {
    return 'Комнаты: не указано'
  }
  if (props.listing.rooms === 0) return 'Студия'
  return `${props.listing.rooms}-комн.`
})
</script>

<template>
  <article class="card">
    <div class="card-image-wrapper" @click="$emit('open-details', listing)">
      <img
        :src="mainPhoto"
        :alt="listing.title || 'Объявление о жилье'"
        class="card-image"
        @error="imgFailed = true"
      />
      <span v-if="listing.photos?.length > 1" class="photo-badge">
        📷 {{ listing.photos.length }}
      </span>
      <button
        type="button"
        class="fav-btn"
        :class="{ active: isFavorite }"
        :title="isFavorite ? 'Убрать из избранного' : 'Добавить в избранное'"
        @click.stop="$emit('toggle-favorite', listing.id)"
      >
        {{ isFavorite ? '♥' : '♡' }}
      </button>
    </div>

    <div class="card-body">
      <div class="card-price">{{ formattedPrice }}</div>
      <h3 class="card-title" @click="$emit('open-details', listing)">
        {{ listing.title || 'Без названия' }}
      </h3>

      <div class="card-meta">
        <span>📍 {{ listing.district || 'Район не указан' }}</span>
        <span>🚪 {{ formattedRooms }}</span>
        <span>📐 {{ listing.area ? `${listing.area} м²` : 'Площадь не указана' }}</span>
      </div>

      <p class="card-desc">
        {{ listing.description || 'Описание отсутствует.' }}
      </p>

      <button
        type="button"
        class="details-btn"
        @click="$emit('open-details', listing)"
      >
        Подробнее
      </button>
    </div>
  </article>
</template>

<style scoped>
.card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  transition: transform 0.15s ease, box-shadow 0.15s ease;
}

.card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(15, 23, 42, 0.08);
}

.card-image-wrapper {
  position: relative;
  height: 200px;
  background: #f1f5f9;
  cursor: pointer;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.photo-badge {
  position: absolute;
  bottom: 10px;
  left: 10px;
  background: rgba(15, 23, 42, 0.75);
  color: #fff;
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 6px;
}

.fav-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.92);
  font-size: 20px;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.15s ease, color 0.15s ease;
}

.fav-btn:hover {
  transform: scale(1.08);
}

.fav-btn.active {
  color: #ef4444;
}

.card-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex-grow: 1;
}

.card-price {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 4px;
}

.card-title {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  cursor: pointer;
}

.card-title:hover {
  color: #2563eb;
}

.card-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
  font-size: 13px;
  color: #475569;
  margin-bottom: 10px;
}

.card-desc {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 16px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  flex-grow: 1;
}

.details-btn {
  width: 100%;
  padding: 9px 14px;
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s ease;
}

.details-btn:hover {
  background: #dbeafe;
}
</style>