<script setup lang="ts">
import { ref, watch } from 'vue';

const props = withDefaults(
  defineProps<{
    modelValue: number;
    increment?: number;
    itemName?: string;
    disabled?: boolean;
  }>(),
  {
    increment: 1,
    itemName: '',
    disabled: false,
  },
);

const emit = defineEmits<{
  'update:modelValue': [value: number];
  amountChanged: [value: number];
}>();

const quantity = ref(props.modelValue);

watch(
  () => props.modelValue,
  (value) => {
    quantity.value = value;
  },
);

function onAdd() {
  if (!props.disabled) {
    quantity.value += props.increment;
    emit('update:modelValue', quantity.value);
    emit('amountChanged', quantity.value);
  }
}

function onRemove() {
  if (!props.disabled && quantity.value > 0) {
    quantity.value -= props.increment;
    emit('update:modelValue', quantity.value);
    emit('amountChanged', quantity.value);
  }
}
</script>

<template>
  <div class="container" role="group" :aria-label="itemName ? 'Quantity of ' + itemName : 'Quantity'">
    <button
      type="button"
      class="btn-icon remove"
      :aria-label="'Remove one ' + itemName"
      :disabled="disabled || quantity <= 0"
      @click="onRemove()"
    >
      <span class="material-icons" aria-hidden="true">remove</span>
    </button>
    <span class="quantity" aria-live="polite">{{ quantity }}</span>
    <button
      type="button"
      class="btn-icon add"
      :aria-label="'Add one ' + itemName"
      :disabled="disabled"
      @click="onAdd()"
    >
      <span class="material-icons" aria-hidden="true">add</span>
    </button>
  </div>
</template>

<style scoped>
.container {
  display: flex;
  align-items: center;
  gap: 2px;
  background-color: var(--color-surface-muted);
  border-radius: var(--radius-pill);
}

.container button {
  width: 44px;
  height: 44px;
  padding: 0;
  border-radius: var(--radius-pill);
}

.remove {
  color: var(--color-text);
}

.remove:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.add {
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.add:hover {
  background-color: var(--color-primary);
}

.quantity {
  min-width: 24px;
  text-align: center;
  font-size: 16px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}
</style>
