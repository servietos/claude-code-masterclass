import { defineStore } from 'pinia';
import { ref } from 'vue';
import * as api from '@/api/catalog';
import type { CatalogItem } from '@/models/catalog-item';

function sortByName(a: CatalogItem, b: CatalogItem): number {
  return a.name.localeCompare(b.name);
}

function sorted(list: CatalogItem[]): CatalogItem[] {
  return [...list].sort(sortByName);
}

function message(err: unknown): string {
  return err instanceof Error ? err.message : String(err);
}

export const useCatalogStore = defineStore('catalog', () => {
  const items = ref<CatalogItem[]>([]);
  const loaded = ref(false);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function getAll() {
    loading.value = true;
    error.value = null;
    try {
      items.value = sorted(await api.getAll());
      loaded.value = true;
    } catch (err) {
      error.value = message(err);
    } finally {
      loading.value = false;
    }
  }

  async function add(item: CatalogItem) {
    loading.value = true;
    error.value = null;
    try {
      const saved = await api.add(item);
      items.value = sorted([...items.value.filter((i) => i.id !== saved.id), saved]);
    } catch (err) {
      error.value = message(err);
    } finally {
      loading.value = false;
    }
  }

  async function update(item: CatalogItem) {
    loading.value = true;
    error.value = null;
    try {
      const saved = await api.update(item);
      items.value = sorted(items.value.map((i) => (i.id === item.id ? { ...i, ...item, ...(saved ?? {}) } : i)));
    } catch (err) {
      error.value = message(err);
    } finally {
      loading.value = false;
    }
  }

  async function remove(id: number) {
    loading.value = true;
    error.value = null;
    items.value = items.value.filter((i) => i.id !== id);
    try {
      await api.remove(id);
    } catch (err) {
      error.value = message(err);
    } finally {
      loading.value = false;
    }
  }

  return { items, loaded, loading, error, getAll, add, update, remove };
});
