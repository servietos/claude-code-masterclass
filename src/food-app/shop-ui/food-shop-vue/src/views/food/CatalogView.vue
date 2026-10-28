<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { ref, watch } from 'vue';
import FoodEdit from '@/components/catalog/FoodEdit.vue';
import FoodList from '@/components/catalog/FoodList.vue';
import type { CatalogItem } from '@/models/catalog-item';
import { logger } from '@/services/logger';
import { useCatalogStore } from '@/stores/catalog';

const catalog = useCatalogStore();
const { items: food, loaded } = storeToRefs(catalog);
const selected = ref<CatalogItem | null>(null);

watch(
  loaded,
  (isLoaded) => {
    if (!isLoaded) {
      catalog.getAll();
      logger.logEvent('loaded data food from catalog');
    }
  },
  { immediate: true },
);

function addFood(item: CatalogItem) {
  selected.value = item;
}

function selectFood(f: CatalogItem) {
  selected.value = { ...f };
}

function deleteFood(f: CatalogItem) {
  catalog.remove(f.id);
}

function foodSaved(f: CatalogItem) {
  if (f.id == 0) {
    catalog.add(f);
  } else {
    catalog.update(f);
  }
}
</script>

<template>
  <section class="container" aria-labelledby="catalog-title">
    <FoodList
      :food="food"
      :selected="selected"
      @food-selected="selectFood"
      @food-deleted="deleteFood"
      @food-adding="addFood"
    />

    <FoodEdit v-if="selected" :food="selected" @save-food="foodSaved" />
  </section>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: 24px;
}
</style>
