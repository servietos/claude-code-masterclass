<script setup lang="ts">
import { environment } from '@/environments/environment';
import { useAuthStore } from '@/stores/auth';

const auth = useAuthStore();
const entryPic = '/assets/images/food.png';

function login() {
  if (environment.authEnabled) {
    auth.login();
  }
}
</script>

<template>
  <div class="card">
    <div class="title">Welcome to Food App</div>
    <img :src="entryPic" alt="login-screen" class="card-image" />
    <button class="btn btn-primary" @click="login()">Login</button>
  </div>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  box-sizing: content-box;
  width: 50vw;
  min-width: 360px;
  margin-bottom: 0;
  border: 1px dotted var(--color-border-strong);
  border-radius: 0;
  box-shadow: none;
  padding: 1rem;
  background-color: var(--color-surface-muted);
}

.title {
  display: flex;
  justify-content: center;
  align-items: center;
  font-family: 'MuseoModerno', cursive;
  font-size: 2rem;
  min-height: 3.5rem;
}

button {
  min-width: 140px;
}

@media screen and (max-width: 400px) {
  .card {
    width: 80vw;
    min-width: 250px;
  }

  .title {
    font-size: 1rem;
  }
}
</style>
