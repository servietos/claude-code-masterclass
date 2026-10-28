import { mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { describe, expect, it } from 'vitest';
import CurrentUser from './CurrentUser.vue';

describe('CurrentUser', () => {
  it('should create', () => {
    const wrapper = mount(CurrentUser, {
      global: { plugins: [createPinia()] },
    });

    expect(wrapper.vm).toBeTruthy();
  });
});
