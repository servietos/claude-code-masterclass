<script setup lang="ts">
import { storeToRefs } from 'pinia';
import { useAuthStore } from '@/stores/auth';

const { user } = storeToRefs(useAuthStore());
</script>

<template>
  <h5>{{ user }}</h5>
</template>
