<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { computed } from 'vue';
import { RouterView, useRoute } from 'vue-router';
import LoginCard from '@/components/auth/LoginCard.vue';
import AppNavbar from '@/components/layout/AppNavbar.vue';
import AppSidebar from '@/components/layout/AppSidebar.vue';
import { environment } from '@/environments/environment';
import { useAuthStore } from '@/stores/auth';
import { useSidenavStore } from '@/stores/sidenav';

const route = useRoute();
const { isAuthenticated } = storeToRefs(useAuthStore());
const { visible: sidenavVisible } = storeToRefs(useSidenavStore());

const authEnabled = environment.authEnabled;
const isIframe = window !== window.parent && !window.opener;
const isHome = computed(() => route.path === '/');
const publicRoute = computed(() => route.fullPath.includes('about'));
</script>

<template>
  <div v-if="!isAuthenticated && !publicRoute" class="loginsplash">
    <LoginCard />
  </div>
  <div v-if="isAuthenticated || publicRoute" class="maingrid">
    <div class="gdNavbar"><AppNavbar /></div>
    <div class="gdMainrow">
      <main class="layout">
        <AppSidebar v-if="sidenavVisible && !isHome" class="aside" />
        <div class="content">
          <RouterView />
        </div>
      </main>
    </div>
  </div>
  <div v-if="authEnabled" style="display: none">
    <RouterView v-if="!isIframe" />
  </div>
</template>

<style scoped>
.loginsplash {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}

.maingrid {
  display: grid;
  grid-template-rows: auto 1fr;
  grid-template-columns: auto;
  grid-template-areas:
    "navbar"
    "mainrow";
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
}

.gdNavbar {
  grid-area: navbar;
}

.gdMainrow {
  grid-area: mainrow;
  min-width: 0;
  background-color: var(--color-bg);
}

.layout {
  box-sizing: border-box;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  gap: 32px;
  width: 100%;
  max-width: var(--layout-max-width);
  margin: 0 auto;
  padding: 32px var(--layout-pad-x) 40px;
  padding-bottom: max(40px, env(safe-area-inset-bottom));
}

.aside {
  flex: 1 1 260px;
  min-width: 0;
}

.content {
  flex: 999 1 560px;
  min-width: 0;
}

@media (max-width: 600px) {
  .layout {
    padding: 20px var(--layout-pad-x) 32px;
    gap: 20px;
  }
}
</style>
