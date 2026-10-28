<script setup lang="ts">
const entryPic = '/assets/images/food.png';
</script>

<template>
  <div class="mainDiv">
    <img :src="entryPic" alt="login-screen" class="entryImg" />
  </div>
</template>

<style scoped>
.mainDiv {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 80vh;
}

.entryImg {
  width: 250px;
}

.webfont {
  font-family: 'MuseoModerno', cursive;
  font-size: 2rem;
}
</style>
