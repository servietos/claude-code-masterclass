import { defineStore } from 'pinia';
import { computed, ref } from 'vue';
import type { CartItem } from '@/models/cart-item';
import { storage } from '@/services/storage';

function updateCart(state: CartItem[], item: CartItem): CartItem[] {
  let cart: CartItem[] = [...state];
  if (cart.length == 0) {
    cart.push({ ...item });
  } else {
    const idx = cart.findIndex((i) => i.id == item.id);
    if (idx > -1) {
      if (item.quantity == 0) {
        cart = cart.filter((i) => i.id != item.id);
      } else {
        cart[idx] = { ...item };
      }
    } else {
      cart.push({ ...item });
    }
  }
  return cart;
}

export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([]);
  const persist = ref(true);

  const count = computed(() => items.value.reduce((runningSum, v) => runningSum + v.quantity, 0));
  const sumTotal = computed(() => items.value.reduce((runningSum, v) => runningSum + v.quantity * v.price, 0));

  function quantityOf(id: number): number {
    const ct = items.value.find((i) => i.id === id);
    return ct ? ct.quantity : 0;
  }

  function set(item: CartItem) {
    items.value = updateCart(items.value, item);
  }

  function clear() {
    items.value = [];
    storage.clearStorage();
  }

  function togglePersist() {
    persist.value = !persist.value;
    if (!persist.value) {
      storage.clearStorage();
    }
  }

  function saveToStorage() {
    storage.saveToStorage(items.value);
  }

  function loadFromStorage() {
    items.value = storage.loadFromStorage() || [];
  }

  return { items, persist, count, sumTotal, quantityOf, set, clear, togglePersist, saveToStorage, loadFromStorage };
});
