<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useRouter } from 'vue-router';
import CurrentUser from '@/components/auth/CurrentUser.vue';
import { environment } from '@/environments/environment';
import { useAuthStore } from '@/stores/auth';
import { useCartStore } from '@/stores/cart';
import { toEuro } from '@/utils/euro';

const router = useRouter();
const cart = useCartStore();
const auth = useAuthStore();
const { items, count, sumTotal, persist } = storeToRefs(cart);
const { authEnabled } = storeToRefs(auth);

const persistCart = environment.features.persistCart;

function logout() {
  auth.logout();
}

function doCheckout() {
  router.push('/food/checkout');
}
</script>

<template>
  <aside class="panel" aria-label="Actions">
    <h2 class="heading">Actions</h2>

    <div class="cartInfo">
      <span class="cartIcon"><span class="material-icons" aria-hidden="true">shopping_cart</span></span>
      <span class="cartCount">{{ count }} items in cart</span>
    </div>
    <div class="sum">
      <span class="sumLabel">Sum Total</span>
      <span class="sumValue">{{ toEuro(sumTotal) }}</span>
    </div>
    <label v-if="persistCart" class="toggle">
      <input type="checkbox" role="switch" :checked="persist" @change="cart.togglePersist()" />
      <span class="toggle-track"></span>
      <span>Keep cart</span>
    </label>
    <button class="btn btn-primary checkout" :disabled="items.length === 0" @click="doCheckout()">
      <span class="material-icons" aria-hidden="true">shopping_cart</span>Checkout
    </button>
    <div v-if="authEnabled" class="user">
      <CurrentUser />
      <button class="btn logout" @click="logout()">
        <span class="material-icons" aria-hidden="true">logout</span>Logout
      </button>
    </div>
  </aside>
</template>

<style scoped>
.panel {
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 20px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}

.heading {
  margin: 0;
  font-size: 16px;
  line-height: 24px;
  font-weight: 700;
}

.cartInfo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.cartIcon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--radius-pill);
  background-color: var(--color-primary-soft);
  color: var(--color-on-primary-soft);
}

.cartCount {
  font-size: 15px;
  font-weight: 500;
}

.sum {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}

.sumLabel {
  font-size: 14px;
  color: var(--color-text-muted);
}

.sumValue {
  font-size: 22px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}

.checkout,
.logout {
  border-radius: var(--radius-control);
  width: 100%;
  height: 48px;
}

.user {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-top: 16px;
  border-top: 1px solid var(--color-border);
}
</style>
