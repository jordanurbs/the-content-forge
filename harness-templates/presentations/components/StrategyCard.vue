<script setup lang="ts">
defineProps<{
  title?: string
  titleColor?: string
}>()
</script>

<template>
  <div class="strategy-card">
    <h3 v-if="title" class="card-title" :style="{ color: titleColor || 'var(--neon-cyan)' }">
      {{ title }}
    </h3>
    <div class="card-content">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.strategy-card {
  background: rgba(26, 39, 68, 0.8);
  border: 1px solid var(--navy-light, #2A3F5F);
  border-radius: 12px;
  padding: 1.5rem;
  margin: 0.5rem;
  transition: all 0.3s ease;
  text-align: left;
}

.strategy-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0, 255, 255, 0.2);
  border-color: var(--neon-cyan, #00FFFF);
}

.card-title {
  font-family: 'SHPinscher', sans-serif;
  font-size: 1.1rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.card-content {
  color: var(--text-secondary, #B0C4DE);
  font-size: 0.85em;
  line-height: 1.5;
}

.card-content :deep(p) {
  margin: 0;
}
</style>
