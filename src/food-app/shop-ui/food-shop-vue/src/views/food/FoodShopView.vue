<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { watch } from 'vue';
import ShopItem from '@/components/shop/ShopItem.vue';
import { environment } from '@/environments/environment';
import type { CartItem } from '@/models/cart-item';
import { logger } from '@/services/logger';
import { useCartStore } from '@/stores/cart';
import { useCatalogStore } from '@/stores/catalog';

const catalog = useCatalogStore();
const cart = useCartStore();
const { items: food, loaded } = storeToRefs(catalog);
const { items: cartItems, persist } = storeToRefs(cart);
const persistCart = environment.features.persistCart;

if (persistCart) {
  ensureStorageFeature();
}

watch(
  loaded,
  (value) => {
    if (!value) {
      catalog.getAll();
    }
  },
  { immediate: true },
);

function getItemsInCart(id: number): number {
  return cart.quantityOf(id);
}

function updateCart(f: CartItem) {
  cart.set(f);
  logger.logEvent('Cart updated', { ...f });
}

function ensureStorageFeature() {
  watch([cartItems, persist], ([, persistValue]) => {
    if (persistValue) {
      cart.saveToStorage();
    }
  });

  watch(
    persist,
    (value) => {
      if (value) {
        cart.loadFromStorage();
      }
    },
    { immediate: true },
  );
}
</script>

<template>
  <section class="box" aria-labelledby="food-title">
    <div class="title">
      <span class="tile"><span class="material-icons" aria-hidden="true">local_dining</span></span>
      <h1 id="food-title" class="pageTitle">Food</h1>
    </div>
    <ShopItem
      v-for="f in food"
      :key="f.id"
      :food="f"
      :in-cart="getItemsInCart(f.id)"
      @amount-change="updateCart"
    />
  </section>
</template>

<style scoped>
.box {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.title {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px 24px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}

.tile {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-control);
  background-color: var(--color-primary-soft);
  color: var(--color-on-primary-soft);
}

.pageTitle {
  margin: 0;
  font-size: 20px;
  line-height: 28px;
  font-weight: 700;
  letter-spacing: -0.01em;
}
</style>
