<script setup lang="ts">
defineProps<{
  logoSrc?: string
  lessonNumber?: string
  duration?: string
}>()
</script>

<template>
  <div class="slidev-layout cover">
    <div class="logo-container" v-if="logoSrc">
      <img :src="logoSrc" alt="{{PROJECT_NAME}} Logo" class="logo" />
    </div>
    <div class="content">
      <slot />
    </div>
    <p v-if="lessonNumber || duration" class="meta">
      {{ lessonNumber }}{{ duration ? ` // ${duration}` : '' }}
    </p>
  </div>
</template>

<style scoped>
.cover {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: linear-gradient(135deg, #0A1628 0%, #1A2744 100%);
  height: 100%;
  padding: 4rem 2rem 3.5rem;  /* top padding for HUD, bottom for terminal */
}

.logo-container {
  margin-bottom: 1.5rem;
}

.logo {
  width: 350px;
  height: auto;
}

.content :deep(h1) {
  font-family: 'SHPinscher', sans-serif;
  font-size: 2.5rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  background: linear-gradient(135deg, #FFD700 0%, #FFFFFF 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.5rem;
}

.content :deep(h3) {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #00FFFF;
  font-size: 1.3rem;
  margin-bottom: 0.5rem;
}

.content :deep(p) {
  font-family: 'Courier Prime Code', monospace;
  color: #B0C4DE;
  font-size: 1.1rem;
}

.meta {
  font-family: 'Courier Prime Code', monospace;
  color: #708090;
  font-size: 0.8em;
  margin-top: 1rem;
}
</style>
