<script setup>
import { ref, computed, watch } from 'vue'
import rawListings from './data/listings.json'
import ListingCard from './components/ListingCard.vue'
import ListingModal from './components/ListingModal.vue'

// Состояние фильтров
const searchQuery = ref('')
const minPrice = ref('')
const maxPrice = ref('')
const selectedRooms = ref('all')
const selectedDistrict = ref('all')
const showOnlyFavorites = ref(false)

// Выбранное объявление для модального окна
const activeListing = ref(null)

// Избранное с сохранением в localStorage
const STORAGE_KEY = 'housing_board_favorites'
const savedFavorites = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]')
const favoriteIds = ref(new Set(savedFavorites))

watch(
  favoriteIds,
  (newSet) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...newSet]))
  },
  { deep: true }
)

function toggleFavorite(id) {
  if (favoriteIds.value.has(id)) {
    favoriteIds.value.delete(id)
  } else {
    favoriteIds.value.add(id)
  }
}

// Уникальные районы из загруженных данных для выпадающего списка
const availableDistricts = computed(() => {
  const districts = rawListings
    .map((item) => item.district)
    .filter((district) => Boolean(district))
  return [...new Set(districts)].sort()
})

// Основная реактивная фильтрация
const filteredListings = computed(() => {
  return rawListings.filter((item) => {
    // 1. Вкладка «Избранное»
    if (showOnlyFavorites.value && !favoriteIds.value.has(item.id)) {
      return false
    }

    // 2. Поиск по названию
    if (searchQuery.value.trim()) {
      const title = (item.title || '').toLowerCase()
      const query = searchQuery.value.trim().toLowerCase()
      if (!title.includes(query)) return false
    }

    // 3. Фильтр по цене (от)
    if (minPrice.value !== '' && minPrice.value !== null) {
      if (item.price === null || item.price < Number(minPrice.value)) {
        return false
      }
    }

    // 4. Фильтр по цене (до)
    if (maxPrice.value !== '' && maxPrice.value !== null) {
      if (item.price === null || item.price > Number(maxPrice.value)) {
        return false
      }
    }

    // 5. Фильтр по количеству комнат
    if (selectedRooms.value !== 'all') {
      if (item.rooms === null || item.rooms === undefined) return false
      if (selectedRooms.value === '3+') {
        if (item.rooms < 3) return false
      } else if (item.rooms !== Number(selectedRooms.value)) {
        return false
      }
    }

    // 6. Фильтр по району
    if (selectedDistrict.value !== 'all') {
      if (item.district !== selectedDistrict.value) return false
    }

    return true
  })
})

function resetFilters() {
  searchQuery.value = ''
  minPrice.value = ''
  maxPrice.value = ''
  selectedRooms.value = 'all'
  selectedDistrict.value = 'all'
  showOnlyFavorites.value = false
}
</script>

<template>
  <div class="app-container">
    <header class="header">
      <div>
        <h1>Аренда жилья</h1>
        <p class="subtitle">Актуальные предложения с доски объявлений</p>
      </div>

      <div class="tabs">
        <button
          type="button"
          class="tab-btn"
          :class="{ active: !showOnlyFavorites }"
          @click="showOnlyFavorites = false"
        >
          Все объявления ({{ rawListings.length }})
        </button>
        <button
          type="button"
          class="tab-btn"
          :class="{ active: showOnlyFavorites }"
          @click="showOnlyFavorites = true"
        >
          ♥ Избранное ({{ favoriteIds.size }})
        </button>
      </div>
    </header>

    <!-- Панель поиска и фильтров -->
    <section class="filters-panel">
      <div class="filter-group search-group">
        <label>Поиск по названию</label>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Например: студия, 2-комн., у парка..."
        />
      </div>

      <div class="filter-group">
        <label>Район</label>
        <select v-model="selectedDistrict">
          <option value="all">Все районы</option>
          <option
            v-for="district in availableDistricts"
            :key="district"
            :value="district"
          >
            {{ district }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Комнат</label>
        <select v-model="selectedRooms">
          <option value="all">Любое</option>
          <option value="0">Студия</option>
          <option value="1">1 комната</option>
          <option value="2">2 комнаты</option>
          <option value="3+">3 и более</option>
        </select>
      </div>

      <div class="filter-group price-group">
        <label>Цена, ₽/мес.</label>
        <div class="price-inputs">
          <input v-model="minPrice" type="number" min="0" placeholder="От" />
          <input v-model="maxPrice" type="number" min="0" placeholder="До" />
        </div>
      </div>
    </section>

    <!-- Строка статуса -->
    <div class="results-bar">
      <span>
        Найдено объявлений: <strong>{{ filteredListings.length }}</strong>
      </span>
      <button type="button" class="reset-link" @click="resetFilters">
        Сбросить фильтры
      </button>
    </div>

    <!-- Сетка объявлений -->
    <main v-if="filteredListings.length > 0" class="listings-grid">
      <ListingCard
        v-for="item in filteredListings"
        :key="item.id"
        :listing="item"
        :is-favorite="favoriteIds.has(item.id)"
        @toggle-favorite="toggleFavorite"
        @open-details="activeListing = $event"
      />
    </main>

    <!-- Пустое состояние -->
    <div v-else class="empty-state">
      <h3>По выбранным условиям объявления не найдены</h3>
      <p>
        {{
          showOnlyFavorites
            ? 'В списке избранного пока нет подходящих вариантов.'
            : 'Попробуйте изменить параметры фильтрации или поисковый запрос.'
        }}
      </p>
      <button type="button" class="primary-btn" @click="resetFilters">
        Показать все объявления
      </button>
    </div>

    <!-- Модальное окно -->
    <ListingModal
      v-if="activeListing"
      :listing="activeListing"
      :is-favorite="favoriteIds.has(activeListing.id)"
      @close="activeListing = null"
      @toggle-favorite="toggleFavorite"
    />
  </div>
</template>

<style>
* {
  box-sizing: border-box;
}

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f1f5f9;
  color: #0f172a;
}

.app-container {
  max-width: 1140px;
  margin: 0 auto;
  padding: 24px 16px 48px;
}

.header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.header h1 {
  margin: 0;
  font-size: 28px;
}

.subtitle {
  margin: 4px 0 0;
  color: #64748b;
  font-size: 14px;
}

.tabs {
  display: flex;
  gap: 8px;
}

.tab-btn {
  padding: 10px 16px;
  border-radius: 8px;
  border: 1px solid #cbd5e1;
  background: #ffffff;
  font-weight: 600;
  cursor: pointer;
}

.tab-btn.active {
  background: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.filters-panel {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1.5fr;
  gap: 14px;
  background: #ffffff;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  margin-bottom: 16px;
}

@media (max-width: 820px) {
  .filters-panel {
    grid-template-columns: 1fr;
  }
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #475569;
}

.filter-group input,
.filter-group select {
  padding: 9px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 14px;
  width: 100%;
}

.price-inputs {
  display: flex;
  gap: 8px;
}

.results-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  font-size: 14px;
  color: #475569;
}

.reset-link {
  background: none;
  border: none;
  color: #2563eb;
  cursor: pointer;
  font-size: 14px;
  text-decoration: underline;
}

.listings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(310px, 1fr));
  gap: 20px;
}

.empty-state {
  text-align: center;
  background: #ffffff;
  padding: 48px 24px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
}

.empty-state h3 {
  margin: 0 0 8px;
}

.empty-state p {
  color: #64748b;
  margin: 0 0 20px;
}

.primary-btn {
  padding: 10px 20px;
  background: #2563eb;
  color: #ffffff;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}
</style>