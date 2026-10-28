<script setup lang="ts">
import { ref, watch } from 'vue';
import NumberPicker from '@/components/shared/NumberPicker.vue';
import type { CartItem } from '@/models/cart-item';
import { CatalogItem } from '@/models/catalog-item';
import { toEuro } from '@/utils/euro';

const props = withDefaults(
  defineProps<{
    food?: CatalogItem;
    inCart?: number | null;
  }>(),
  {
    food: () => new CatalogItem(),
    inCart: 0,
  },
);

const emit = defineEmits<{
  amountChange: [item: CartItem];
}>();

const nbrPicker = ref(props.inCart ?? 0);

watch(
  () => props.inCart,
  (value) => {
    nbrPicker.value = value ?? 0;
  },
);

function handleAmountChange(amount: number) {
  const ci: CartItem = {
    id: props.food.id,
    name: props.food.name,
    price: props.food.price,
    quantity: amount,
  };
  emit('amountChange', ci);
}
</script>

<template>
  <article class="card" :class="{ inCart: (inCart ?? 0) > 0 }">
    <img class="image" :src="`assets/images/${food.pictureUrl ?? ''}`" :alt="food.name" />
    <div class="text">
      <h2 class="title">{{ food.name }}</h2>
      <p class="description">{{ food.description }}</p>
    </div>
    <div class="side">
      <span class="price">{{ toEuro(food.price) }}</span>
      <NumberPicker v-model="nbrPicker" :item-name="food.name" @amount-changed="handleAmountChange" />
    </div>
  </article>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 0;
  padding: 16px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}

.inCart {
  border-color: var(--color-primary-border);
}

.image {
  flex: 0 0 176px;
  width: 176px;
  height: 128px;
  object-fit: cover;
  border-radius: 12px;
}

.text {
  flex: 999 1 260px;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-top: 4px;
}

.title {
  margin: 0;
  font-size: 18px;
  line-height: 26px;
  font-weight: 600;
}

.description {
  margin: 0;
  max-width: 68ch;
  font-size: 15px;
  line-height: 24px;
  color: var(--color-text-muted);
}

.side {
  flex: 1 0 auto;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-end;
  gap: 12px;
  padding-top: 4px;
}

.price {
  font-size: 18px;
  font-weight: 700;
  font-variant-numeric: tabular-nums;
}
</style>
