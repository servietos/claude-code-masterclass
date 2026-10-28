<script setup lang="ts">
import { computed, reactive, ref, watch } from 'vue';
import { CatalogItem } from '@/models/catalog-item';

type FoodForm = {
  id: number;
  name: string;
  inStock: number | null;
  price: number | null;
};

type ValidationErrors = Record<string, unknown>;
type Validator = (value: unknown) => ValidationErrors | null;
type ControlName = 'name' | 'inStock' | 'price';

const props = withDefaults(defineProps<{ food?: CatalogItem }>(), {
  food: () => new CatalogItem(),
});

const emit = defineEmits<{
  saveFood: [item: CatalogItem];
}>();

function isEmpty(value: unknown): boolean {
  return value == null || ((typeof value === 'string' || Array.isArray(value)) && value.length === 0);
}

const required: Validator = (value) => (isEmpty(value) ? { required: true } : null);

const minLength =
  (length: number): Validator =>
  (value) =>
    !isEmpty(value) && typeof value === 'string' && value.length < length
      ? { minlength: { requiredLength: length, actualLength: value.length } }
      : null;

const min =
  (minimum: number): Validator =>
  (value) => {
    if (isEmpty(value)) {
      return null;
    }
    const parsed = parseFloat(String(value));
    return !isNaN(parsed) && parsed < minimum ? { min: { min: minimum, actual: value } } : null;
  };

const initial = new CatalogItem();
const form = reactive<FoodForm>({
  id: initial.id,
  name: initial.name,
  inStock: initial.inStock,
  price: initial.price,
});

const validators: Record<ControlName, Validator[]> = {
  name: [required, minLength(3)],
  inStock: [required, min(1)],
  price: [],
};

const touched = reactive<Record<ControlName, boolean>>({ name: false, inStock: false, price: false });
const submitted = ref(false);

function validate(control: ControlName): ValidationErrors | null {
  const merged = validators[control].reduce<ValidationErrors>(
    (errors, validator) => ({ ...errors, ...validator(form[control]) }),
    {},
  );
  return Object.keys(merged).length ? merged : null;
}

const errors = computed<Record<ControlName, ValidationErrors | null>>(() => ({
  name: validate('name'),
  inStock: validate('inStock'),
  price: validate('price'),
}));

function errorState(control: ControlName): boolean {
  return errors.value[control] !== null && (touched[control] || submitted.value);
}

function ariaInvalid(control: ControlName): boolean | undefined {
  const isRequired = validators[control].includes(required);
  return isEmpty(form[control]) && isRequired ? undefined : errorState(control);
}

function numberModel(control: 'inStock' | 'price') {
  return computed<number | null, number | string | null>({
    get: () => form[control],
    set: (value) => {
      form[control] = typeof value === 'number' ? value : null;
    },
  });
}

const inStock = numberModel('inStock');
const price = numberModel('price');

function patchValue(value: Partial<FoodForm>) {
  for (const key of Object.keys(form) as (keyof FoodForm)[]) {
    if (key in value) {
      Object.assign(form, { [key]: value[key] });
    }
  }
}

watch(
  () => props.food,
  (food) => patchValue(food),
  { immediate: true },
);

function saveForm() {
  submitted.value = true;
  emit('saveFood', { ...form } as CatalogItem);
}
</script>

<template>
  <form class="card" novalidate aria-labelledby="edit-title" @submit.prevent="saveForm()">
    <div class="heading">
      <h2 id="edit-title" class="title">Edit</h2>
      <span class="subject">{{ food.name }}</span>
    </div>
    <div class="fields">
      <div class="field name">
        <label class="field-label" for="edit-name">Name</label>
        <input
          id="edit-name"
          v-model="form.name"
          class="field-input"
          :class="{ invalid: errorState('name') }"
          type="text"
          required
          aria-required="true"
          :aria-invalid="ariaInvalid('name')"
          @blur="touched.name = true"
        />
        <span v-if="touched.name && errors.name !== null" class="field-error">Name is required &amp; must be more than 3 chars</span>
      </div>
      <div class="field">
        <label class="field-label" for="edit-price">Price</label>
        <input
          id="edit-price"
          v-model.number="price"
          class="field-input"
          :class="{ invalid: errorState('price') }"
          type="number"
          aria-required="false"
          :aria-invalid="ariaInvalid('price')"
          @blur="touched.price = true"
        />
        <span class="field-suffix">€</span>
        <span v-if="touched.price && errors.price !== null" class="field-error">Price must be greater than 1€</span>
      </div>
      <div class="field">
        <label class="field-label" for="edit-stock">In stock</label>
        <input
          id="edit-stock"
          v-model.number="inStock"
          class="field-input"
          :class="{ invalid: errorState('inStock') }"
          type="number"
          required
          aria-required="true"
          :aria-invalid="ariaInvalid('inStock')"
          @blur="touched.inStock = true"
        />
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-primary" type="submit">Save</button>
    </div>
  </form>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 0;
  padding: 24px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}

.heading {
  display: flex;
  align-items: baseline;
  gap: 12px;
}

.title {
  margin: 0;
  font-size: 18px;
  line-height: 26px;
  font-weight: 600;
}

.subject {
  font-size: 14px;
  color: var(--color-text-muted);
}

.fields {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.field {
  flex: 1 1 160px;
  min-width: 0;
}

.field.name {
  flex: 2 1 240px;
}

.field-input.invalid:not(:focus) {
  border-color: var(--color-danger);
}

.actions {
  display: flex;
  justify-content: flex-end;
}

.actions button {
  border-radius: var(--radius-control);
  height: 44px;
  padding: 0 24px;
  font-size: 15px;
  font-weight: 600;
}
</style>
