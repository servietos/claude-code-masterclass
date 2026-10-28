<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { http } from '@/api/http';
import type { NavItem } from '@/models/nav-item';
import { useTheme } from '@/services/theme';
import { useSidenavStore } from '@/stores/sidenav';

const sidenav = useSidenavStore();
const { theme, toggle: toggleTheme } = useTheme();
const menuItems = ref<NavItem[]>([]);

onMounted(async () => {
  menuItems.value = await http<NavItem[]>('/assets/nav-items.json');
});

function toggleMenu() {
  sidenav.toggle();
}
</script>

<template>
  <header class="bar">
    <button type="button" class="btn-icon menuButton" aria-label="Open menu" @click="toggleMenu()">
      <span class="material-icons" aria-hidden="true">menu</span>
    </button>
    <div class="brand">
      <span class="logo"><span class="material-icons" aria-hidden="true">restaurant</span></span>
      <span class="brandName">Passion for Food</span>
    </div>
    <nav class="links" aria-label="Main">
      <RouterLink
        v-for="mi in menuItems"
        :key="mi.url"
        :to="mi.url"
        class="navLink"
        active-class=""
        exact-active-class="navLink-active"
      >
        {{ mi.title }}
      </RouterLink>
    </nav>
    <button
      type="button"
      class="btn-icon themeToggle"
      :aria-label="theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'"
      @click="toggleTheme()"
    >
      <span class="material-icons" aria-hidden="true">{{ theme === 'dark' ? 'light_mode' : 'dark_mode' }}</span>
    </button>
  </header>
</template>

<style scoped>
.bar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  padding: 10px max(var(--layout-pad-x), calc((100% - var(--layout-max-width)) / 2 + var(--layout-pad-x)));
  padding-top: max(10px, env(safe-area-inset-top));
  background-color: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.menuButton {
  color: var(--color-text-muted);
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 16px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 9px;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.logo .material-icons {
  width: 18px;
  height: 18px;
  font-size: 18px;
}

.brandName {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.links {
  flex: 1 1 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.navLink {
  display: flex;
  align-items: center;
  min-height: 44px;
  padding: 0 14px;
  border-radius: var(--radius-pill);
  color: var(--color-text-muted);
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
}

.navLink:hover {
  background-color: var(--color-surface-muted);
}

.navLink-active,
.navLink-active:hover {
  background-color: var(--color-primary-soft);
  color: var(--color-on-primary-soft);
  font-weight: 600;
}

.themeToggle {
  margin-left: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-control);
  color: var(--color-label);
}
</style>
