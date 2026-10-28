import { flushPromises, mount } from '@vue/test-utils';
import { createPinia } from 'pinia';
import { describe, expect, it, vi } from 'vitest';
import { createMemoryHistory, createRouter } from 'vue-router';
import AppNavbar from './AppNavbar.vue';

const navItems = vi.hoisted(() => [
  { title: 'Home', url: '/' },
  { title: 'Food', url: '/food' },
  { title: 'About', url: '/about' },
]);

vi.mock('@/api/http', () => ({
  http: vi.fn(async () => navItems),
}));

describe('AppNavbar', () => {
  it('should have three menu items by default', async () => {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [{ path: '/:pathMatch(.*)*', component: { render: () => null } }],
    });
    router.push('/');
    await router.isReady();

    const wrapper = mount(AppNavbar, {
      global: { plugins: [createPinia(), router] },
    });
    await flushPromises();

    expect(wrapper.findAll('a.navLink').length).toBe(3);
  });
});
