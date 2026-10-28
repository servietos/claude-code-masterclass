import { createRouter, createWebHistory, START_LOCATION, type RouteRecordRaw } from 'vue-router';
import { logger } from '@/services/logger';
import AboutView from '@/views/AboutView.vue';
import HomeView from '@/views/HomeView.vue';

export const routes: RouteRecordRaw[] = [
  { path: '/', component: HomeView },
  { path: '/about', component: AboutView },
  { path: '/food', component: () => import('@/views/food/FoodShopView.vue') },
  { path: '/food/checkout', component: () => import('@/views/food/CheckoutView.vue') },
  { path: '/food/catalog', component: () => import('@/views/food/CatalogView.vue') },
];

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

router.afterEach((_to, from, failure) => {
  if (failure || from === START_LOCATION) {
    return;
  }
  logger.trackPageView(document.title, window.location.href);
});

export default router;
