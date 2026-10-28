<script setup lang="ts">
import { environment } from '@/environments/environment';

const config = JSON.stringify(environment, null, 2);
</script>

<template>
  <div class="title">
    <span class="tile"><span class="material-icons" aria-hidden="true">info</span></span>
    <h1 class="pageTitle">About</h1>
  </div>
  <div class="card">
    <div class="card-header">
      <img class="card-avatar" src="https://avatars3.githubusercontent.com/u/16348023?s=460&v=4" />
      <div>
        <div class="card-title">Food App</div>
        <div class="card-subtitle">By alexander.kastil@integrations.at</div>
      </div>
    </div>
    <div class="card-content">
      <div>
        A .NET Core Api and Angular UI implemented a Cloud Native App with step by
        step Installation Scripts used for ng-dev, ng-adv, az-native, az-400,
        az-204
      </div>
      <div>
        <span>Using config:</span>
        <pre>
        <p>{{ config }}</p>
      </pre>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 16px;
  padding: 20px 24px;
  background-color: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-card);
  box-shadow: var(--shadow-card);
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

.card-subtitle {
  color: var(--color-text-muted);
}

.card-content > div {
  margin: 10px 0;
}
</style>
