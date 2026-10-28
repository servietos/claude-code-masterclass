<script setup lang="ts">
import { watch } from 'vue';
import type { OrderEventResponse } from '@/models/order-event-response';
import { logger } from '@/services/logger';

const props = withDefaults(
  defineProps<{
    response?: OrderEventResponse | null;
  }>(),
  {
    response: null,
  },
);

watch(
  () => props.response,
  (value) => {
    logger.logEvent('checkout response', value as unknown as Record<string, unknown>);
  },
  { immediate: true },
);
</script>

<template>
  <div>
    <div class="card">
      <div class="card-header">
        <div class="card-title">Your order was submitted</div>
      </div>
      <div class="card-content">
        <p>Thank you for your order!</p>
        <p>Your order number is {{ response?.orderId }}</p>
        <p>We'll let you know after your payment was processed</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.card-content:last-child {
  padding-bottom: 1rem;
  padding-top: 1rem;
}
</style>
