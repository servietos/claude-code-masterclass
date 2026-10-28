import { mount, type VueWrapper } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import FoodShopView from './FoodShopView.vue';

vi.mock('@/api/catalog', () => ({
  getAll: vi.fn(async () => []),
}));

describe('FoodShopView', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    wrapper = mount(FoodShopView, {
      global: { plugins: [createPinia()] },
    });
  });

  it('should create', () => {
    expect(wrapper.vm).toBeTruthy();
  });
});
