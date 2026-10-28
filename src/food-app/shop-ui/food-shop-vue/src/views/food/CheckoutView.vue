<script setup lang="ts">
import { computed, ref } from 'vue';
import { checkout } from '@/api/orders';
import CheckoutForm from '@/components/shop/CheckoutForm.vue';
import CheckoutResponse from '@/components/shop/CheckoutResponse.vue';
import { Order } from '@/models/order';
import type { OrderEventResponse } from '@/models/order-event-response';
import { useCartStore } from '@/stores/cart';

const mockOrder = {
  customer: { id: '1', name: 'Giro Kastil', phone: '+43 664 436 07 77', email: 'giro.kastil@integrations.at' },
  payment: { type: 'Bank Account', accountNumber: '1234' },
  shippingAddress: { street: 'Himmelstraße 115', city: 'Wien', country: 'Austria', zipCode: '1190' },
  items: [],
};

const cart = useCartStore();

const order = computed<Order>(() =>
  Object.assign(new Order(), mockOrder, { items: [...cart.items] }, { total: cart.sumTotal }),
);

const response = ref<OrderEventResponse | null>(null);

async function completeCheckout(o: Order) {
  response.value = await checkout(o);
  cart.clear();
}
</script>

<template>
  <div class="container">
    <CheckoutForm v-if="order.items.length > 0" :order="order" @checkout="completeCheckout" />
    <CheckoutResponse v-if="response != null && order.items.length == 0" :response="response" />
  </div>
</template>

<style scoped>
.container {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
</style>
