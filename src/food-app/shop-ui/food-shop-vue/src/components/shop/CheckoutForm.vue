<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import type { Order } from '@/models/order';
import { toEuro } from '@/utils/euro';

type Validator = (value: string) => boolean;

const EMAIL_REGEXP =
  /^(?=.{1,254}$)(?=.{1,64}@)[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_`{|}~-]+)*@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;

const required: Validator = (value) => value.length > 0;
const email: Validator = (value) => value.length === 0 || EMAIL_REGEXP.test(value);

const validators = {
  customer: { id: [required], name: [required], email: [email, required], phone: [required] },
  shippingAddress: { street: [required], city: [required], country: [required], zipCode: [required] },
  payment: { type: [required], accountNumber: [required] },
};

type Groups = typeof validators;
type GroupName = keyof Groups;
type FieldName<G extends GroupName> = keyof Groups[G] & string;

const props = defineProps<{
  order: Order;
}>();

const emit = defineEmits<{
  checkout: [order: Order];
}>();

const orderForm = reactive({
  customer: { id: '', name: '', email: '', phone: '' },
  shippingAddress: { street: '', city: '', country: '', zipCode: '' },
  payment: { type: '', accountNumber: '' },
});

const touched = reactive<Record<string, boolean>>({});
const submitted = ref(false);

watch(
  () => props.order,
  (order) => {
    Object.assign(orderForm.customer, order.customer);
    Object.assign(orderForm.shippingAddress, order.shippingAddress);
    Object.assign(orderForm.payment, order.payment);
  },
  { immediate: true },
);

function valueOf<G extends GroupName>(group: G, name: FieldName<G>): string {
  return (orderForm[group] as Record<string, string>)[name] ?? '';
}

function controlValid<G extends GroupName>(group: G, name: FieldName<G>): boolean {
  const rules = (validators[group] as Record<string, Validator[]>)[name] ?? [];
  return rules.every((rule) => rule(valueOf(group, name)));
}

function errorState<G extends GroupName>(group: G, name: FieldName<G>): boolean {
  return !controlValid(group, name) && (touched[`${group}.${name}`] === true || submitted.value);
}

function ariaInvalid<G extends GroupName>(group: G, name: FieldName<G>): boolean | undefined {
  return valueOf(group, name).length === 0 ? undefined : errorState(group, name);
}

function touch<G extends GroupName>(group: G, name: FieldName<G>) {
  touched[`${group}.${name}`] = true;
}

const valid = computed(() =>
  (Object.keys(validators) as GroupName[]).every((group) =>
    Object.keys(validators[group]).every((name) => controlValid(group, name as FieldName<typeof group>)),
  ),
);

function onSubmit() {
  submitted.value = true;
}

function completeCheckout() {
  const value = {
    customer: { ...orderForm.customer },
    shippingAddress: { ...orderForm.shippingAddress },
    payment: { ...orderForm.payment },
  };
  const o = Object.assign({ ...props.order }, value, { items: [...props.order.items] });
  emit('checkout', o);
}
</script>

<template>
  <div>
    <div class="toolbar">
      <span>Checkout</span>
    </div>
    <form class="border" novalidate @submit.prevent="onSubmit">
      <div class="column border">
        <label class="field" :class="{ invalid: errorState('customer', 'id') }">
          <span class="field-label">Id</span>
          <input
            v-model="orderForm.customer.id"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('customer', 'id')"
            @blur="touch('customer', 'id')"
          />
        </label>
        <label class="field" :class="{ invalid: errorState('customer', 'name') }">
          <span class="field-label">Name</span>
          <input
            v-model="orderForm.customer.name"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('customer', 'name')"
            @blur="touch('customer', 'name')"
          />
        </label>
        <label class="field" :class="{ invalid: errorState('customer', 'email') }">
          <span class="field-label">E-Mail</span>
          <input
            v-model="orderForm.customer.email"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('customer', 'email')"
            @blur="touch('customer', 'email')"
          />
        </label>
        <label class="field" :class="{ invalid: errorState('customer', 'phone') }">
          <span class="field-label">Phone</span>
          <input
            v-model="orderForm.customer.phone"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('customer', 'phone')"
            @blur="touch('customer', 'phone')"
          />
        </label>
      </div>

      <div class="column border">
        <label class="field" :class="{ invalid: errorState('payment', 'type') }">
          <span class="field-label">Payment type</span>
          <input
            v-model="orderForm.payment.type"
            class="field-input"
            placeholder="Payment type"
            required
            :aria-invalid="ariaInvalid('payment', 'type')"
            @blur="touch('payment', 'type')"
          />
        </label>
        <label class="field" :class="{ invalid: errorState('payment', 'accountNumber') }">
          <span class="field-label">Account</span>
          <input
            v-model="orderForm.payment.accountNumber"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('payment', 'accountNumber')"
            @blur="touch('payment', 'accountNumber')"
          />
        </label>
      </div>

      <div class="column border">
        <label class="field" :class="{ invalid: errorState('shippingAddress', 'street') }">
          <span class="field-label">Street</span>
          <input
            v-model="orderForm.shippingAddress.street"
            class="field-input"
            placeholder="Street"
            required
            :aria-invalid="ariaInvalid('shippingAddress', 'street')"
            @blur="touch('shippingAddress', 'street')"
          />
        </label>
        <label class="field" :class="{ invalid: errorState('shippingAddress', 'zipCode') }">
          <span class="field-label">zipCode</span>
          <input
            v-model="orderForm.shippingAddress.zipCode"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('shippingAddress', 'zipCode')"
            @blur="touch('shippingAddress', 'zipCode')"
          />
        </label>
        <label class="field" :class="{ invalid: errorState('shippingAddress', 'city') }">
          <span class="field-label">city</span>
          <input
            v-model="orderForm.shippingAddress.city"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('shippingAddress', 'city')"
            @blur="touch('shippingAddress', 'city')"
          />
        </label>
        <label class="field" :class="{ invalid: errorState('shippingAddress', 'country') }">
          <span class="field-label">country</span>
          <input
            v-model="orderForm.shippingAddress.country"
            class="field-input"
            required
            :aria-invalid="ariaInvalid('shippingAddress', 'country')"
            @blur="touch('shippingAddress', 'country')"
          />
        </label>
      </div>

      <div class="border">
        <div v-for="(item, i) in order.items" :key="i" class="row">
          <input type="text" :value="item.quantity" class="quantity" disabled />
          <input type="text" :value="item.name" class="name" disabled />
          <label>item price:</label>
          <input type="text" :value="item.price" class="price" disabled />
        </div>
      </div>
      <div class="border">Total: {{ toEuro(order.total) }}</div>

      <button class="btn btn-primary" :disabled="!valid" type="submit" @click="completeCheckout()">
        Complete Checkout
      </button>
    </form>
  </div>
</template>

<style scoped>
.column {
  display: flex;
  flex-direction: column;
}

.border {
  border: 1px solid var(--color-border);
  padding: 10px;
  margin-bottom: 10px;
}

.field {
  margin-bottom: 20px;
}

.field-label::after {
  margin-left: 1px;
  content: "*";
}

.field.invalid .field-label {
  color: var(--color-danger);
}

.field.invalid .field-input,
.field.invalid .field-input:hover,
.field.invalid .field-input:focus {
  border-color: var(--color-danger);
}

.row {
  display: flex;
  flex-direction: row;
  align-content: stretch;
  margin: 10px 0;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--color-border);
}

.row:last-child {
  border-bottom: none;
}

input:disabled {
  background-color: var(--color-surface);
  border: none;
}

form {
  display: flex;
  flex-direction: column;
}

.id,
.quantity {
  width: 50px;
  margin: 0 0.5rem;
}

.price {
  width: 100px;
  margin: 0 0.5rem;
}

.name {
  flex-grow: 4;
  margin: 0 0.5rem;
}

button {
  align-self: flex-end;
}
</style>
