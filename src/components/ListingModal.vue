<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

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

const emit = defineEmits(['close', 'toggle-favorite'])

const activePhotoIndex = ref(0)
const placeholderImage =
  'https://placehold.co/800x500/e2e8f0/475569?text=Нет+фотографии'

watch(
  () => props.listing,
  () => {
    activePhotoIndex.value = 0
  }
)

const photos = computed(() => {
  if (!props.listing.photos || props.listing.photos.length === 0) {
    return [placeholderImage]
  }
  return props.listing.photos
})

const formattedPrice = computed(() => {
  if (props.listing.price === null || props.listing.price === undefined) {
    return 'Цена не указана'
  }
  return `${new Intl.NumberFormat('ru-RU').format(props.listing.price)} ₽/мес.`
})

const formattedRooms = computed(() => {
  if (props.listing.rooms === null || props.listing.rooms === undefined) {
    return 'Не указано'
  }
  return props.listing.rooms === 0 ? 'Студия' : `${props.listing.rooms}`
})

function handleKeydown(event) {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => window.addEventListener('keydown', handleKeydown))
onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
</script>

<template>
  <div class="modal-backdrop" @click.self="$emit('close')">
    <div class="modal-window">
      <button type="button" class="close-btn" @click="$emit('close')">✕</button>

      <div class="gallery">
        <img
          :src="photos[activePhotoIndex]"
          :alt="listing.title || 'Фото жилья'"
          class="main-photo"
        />
        <div v-if="photos.length > 1" class="thumbnails">
          <img
            v-for="(photo, idx) in photos"
            :key="idx"
            :src="photo"
            class="thumb"
            :class="{ active: idx === activePhotoIndex }"
            @click="activePhotoIndex = idx"
          />
        </div>
      </div>

      <div class="modal-content">
        <div class="modal-header">
          <div>
            <h2 class="modal-title">{{ listing.title || 'Без названия' }}</h2>
            <div class="modal-price">{{ formattedPrice }}</div>
          </div>
          <button
            type="button"
            class="modal-fav-btn"
            :class="{ active: isFavorite }"
            @click="$emit('toggle-favorite', listing.id)"
          >
            {{ isFavorite ? '♥ В избранном' : '♡ В избранное' }}
          </button>
        </div>

        <div class="specs-grid">
          <div class="spec-item">
            <span class="spec-label">Район</span>
            <span class="spec-value">{{ listing.district || 'Не указан' }}</span>
          </div>
          <div class="spec-item">
            <span class="spec-label">Комнат</span>
            <span class="spec-value">{{ formattedRooms }}</span>
          </div>
          <div class="spec-item">
            <span class="spec-label">Площадь</span>
            <span class="spec-value">
              {{ listing.area ? `${listing.area} м²` : 'Не указана' }}
            </span>
          </div>
        </div>

        <div class="description-block">
          <h4>Описание</h4>
          <p>{{ listing.description || 'Автор объявления не добавил описание.' }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  z-index: 100;
}

.modal-window {
  position: relative;
  background: #ffffff;
  border-radius: 16px;
  max-width: 720px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.close-btn {
  position: absolute;
  top: 14px;
  right: 14px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.9);
  font-size: 16px;
  cursor: pointer;
  z-index: 10;
}

.gallery {
  background: #0f172a;
}

.main-photo {
  width: 100%;
  height: 340px;
  object-fit: cover;
  display: block;
}

.thumbnails {
  display: flex;
  gap: 8px;
  padding: 10px;
  background: #1e293b;
  overflow-x: auto;
}

.thumb {
  width: 68px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
  opacity: 0.6;
  cursor: pointer;
  border: 2px solid transparent;
}

.thumb.active {
  opacity: 1;
  border-color: #3b82f6;
}

.modal-content {
  padding: 24px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 20px;
}

.modal-title {
  margin: 0 0 6px;
  font-size: 22px;
  color: #0f172a;
}

.modal-price {
  font-size: 24px;
  font-weight: 700;
  color: #2563eb;
}

.modal-fav-btn {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #fff;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.modal-fav-btn.active {
  border-color: #fecaca;
  background: #fef2f2;
  color: #dc2626;
}

.specs-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  background: #f8fafc;
  padding: 14px;
  border-radius: 10px;
  margin-bottom: 20px;
}

.spec-item {
  display: flex;
  flex-direction: column;
}

.spec-label {
  font-size: 12px;
  color: #64748b;
}

.spec-value {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
}

.description-block h4 {
  margin: 0 0 8px;
  font-size: 16px;
  color: #0f172a;
}

.description-block p {
  margin: 0;
  line-height: 1.6;
  color: #334155;
}
</style>