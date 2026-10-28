<script setup lang="ts">
import { CatalogItem } from '@/models/catalog-item';
import { toEuro } from '@/utils/euro';

const { food = [], selected = null } = defineProps<{
  food?: CatalogItem[] | null;
  selected?: CatalogItem | null;
}>();

const emit = defineEmits<{
  foodSelected: [item: CatalogItem];
  foodDeleted: [item: CatalogItem];
  foodAdding: [item: CatalogItem];
}>();

function selectFood(p: CatalogItem) {
  emit('foodSelected', p);
}

function deleteFood(item: CatalogItem) {
  emit('foodDeleted', item);
}

function addFood() {
  emit('foodAdding', new CatalogItem());
}
</script>

<template>
  <div class="card">
    <div class="header">
      <div class="title">
        <span class="tile"><span class="material-icons" aria-hidden="true">restaurant_menu</span></span>
        <h1 id="catalog-title" class="pageTitle">Catalog</h1>
        <span class="count" :aria-label="(food?.length ?? 0) + ' items'">{{ food?.length ?? 0 }}</span>
      </div>
      <button class="btn btn-primary add" @click="addFood()">
        <span class="material-icons" aria-hidden="true">add</span>Add Food
      </button>
    </div>
    <div class="scroller">
      <table>
        <thead>
          <tr>
            <th class="idCol">Id</th>
            <th>Name</th>
            <th class="priceCol">Price</th>
            <th>In Stock</th>
            <th class="actionCol"></th>
            <th class="actionCol"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="row in food ?? []"
            :key="row.id"
            :class="{ selected: row.id === selected?.id }"
            :aria-selected="row.id === selected?.id"
            @click="selectFood(row)"
          >
            <td class="idCol">{{ row.id }}</td>
            <td class="nameCol">{{ row.name }}</td>
            <td class="priceCol">{{ toEuro(row.price) }}</td>
            <td>
              <span v-if="row.inStock < 5" class="badge low" :aria-label="row.inStock + ', low stock'">{{ row.inStock }}</span>
              <span v-else class="badge ok">{{ row.inStock }}</span>
            </td>
            <td class="actionCol">
              <button
                type="button"
                class="btn-icon rowAction"
                :aria-label="'Edit ' + row.name"
                title="Select"
                @click="selectFood(row)"
              >
                <span class="material-icons" aria-hidden="true">edit</span>
              </button>
            </td>
            <td class="actionCol">
              <button
                type="button"
                class="btn-icon rowAction danger"
                :aria-label="'Delete ' + row.name"
                title="Delete"
                @click="deleteFood(row)"
              >
                <span class="material-icons" aria-hidden="true">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<style scoped>
.header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px 16px;
  padding: 20px 24px;
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.title {
  display: flex;
  align-items: center;
  gap: 12px;
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

.count {
  padding: 2px 10px;
  border-radius: var(--radius-pill);
  background-color: var(--color-surface-muted);
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.add {
  margin-left: auto;
  border-radius: var(--radius-control);
  height: 44px;
  padding: 0 18px;
  font-size: 15px;
  font-weight: 600;
}

.add .material-icons {
  margin-left: -8px;
}

.card {
  overflow: hidden;
  margin-bottom: 0;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
}

.scroller {
  overflow-x: auto;
}

table {
  width: 100%;
  min-width: 560px;
  font-size: 15px;
  background-color: transparent;
}

thead tr {
  height: 44px;
  line-height: 20px;
}

tbody tr {
  height: 56px;
  font-size: 14px;
  line-height: 20px;
  cursor: pointer;
}

th {
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: start;
  letter-spacing: 0.006rem;
  padding: 12px 20px;
  background-color: var(--color-surface-muted);
  color: var(--color-text-muted);
  font-size: 13px;
  font-weight: 600;
}

td {
  box-sizing: border-box;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: start;
  letter-spacing: 0.016rem;
  padding: 6px 20px;
  white-space: nowrap;
  height: auto;
  border-bottom-color: var(--color-border);
}

tbody tr:last-child td {
  border-bottom: none;
}

tr.selected td {
  background-color: var(--color-row-selected);
}

tr.selected .rowAction:not(.danger) {
  background-color: var(--color-primary-soft);
  color: var(--color-on-primary-soft);
}

tr.selected .nameCol {
  font-weight: 600;
}

.idCol {
  width: 72px;
  color: var(--color-text-muted);
  font-variant-numeric: tabular-nums;
}

.priceCol {
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.nameCol {
  font-weight: 500;
}

.actionCol {
  width: 56px;
  text-align: right;
}

th.actionCol {
  padding: 12px 4px;
}

.actionCol:last-child {
  padding-right: 12px;
}

.rowAction {
  width: 44px;
  height: 44px;
  padding: 10px;
  color: var(--color-text-muted);
}

.rowAction.danger {
  color: var(--color-danger);
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
}

.badge.ok {
  background-color: var(--color-success-soft);
  color: var(--color-on-success-soft);
}

.badge.low {
  background-color: var(--color-warning-soft);
  color: var(--color-on-warning-soft);
}
</style>
