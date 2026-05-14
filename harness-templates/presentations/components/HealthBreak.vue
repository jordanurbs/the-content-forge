<script setup lang="ts">
defineProps<{
  title: string
  image?: string
  imageAlt?: string
}>()
</script>

<template>
  <div class="health-break">
    <div v-if="image" class="health-break-image">
      <img :src="image" :alt="imageAlt || 'Health Break'" />
    </div>
    <div class="health-instruction">
      <h3>{{ title }}</h3>
      <slot />
    </div>
  </div>
</template>

<style scoped>
.health-break {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.5rem;
}

.health-break-image {
  max-width: 500px;
}

.health-break-image img {
  width: 100%;
  height: auto;
  border-radius: 12px;
  border: 2px solid var(--success-green, #00FF88);
  box-shadow: 0 0 30px rgba(0, 255, 136, 0.3);
}

.health-instruction {
  background: rgba(0, 255, 136, 0.1);
  border: 1px solid var(--success-green, #00FF88);
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 600px;
  text-align: center;
}

.health-instruction h3 {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--success-green, #00FF88);
  margin-bottom: 0.5rem;
}

.health-instruction :deep(p) {
  color: var(--text-secondary, #B0C4DE);
  font-size: 1rem;
  margin: 0;
}
</style>
