import type { CartItem } from '@/models/cart-item';

const CART_KEY = 'cart';

export const storage = {
  clearStorage(): boolean {
    localStorage.clear();
    return true;
  },

  loadFromStorage(): CartItem[] | null {
    const cart = localStorage.getItem(CART_KEY);
    return cart ? (JSON.parse(cart) as CartItem[]) : null;
  },

  saveToStorage(cart: CartItem[]): boolean {
    localStorage.setItem(CART_KEY, JSON.stringify(cart));
    return true;
  },
};
