<script setup lang="ts">
defineProps<{
  variant?: 'default' | 'warning' | 'success'
}>()
</script>

<template>
  <div class="info-card" :class="variant">
    <slot />
  </div>
</template>

<style scoped>
.info-card {
  background: rgba(26, 39, 68, 0.8);
  border: 1px solid var(--navy-light, #2A3F5F);
  border-left: 4px solid var(--neon-cyan, #00FFFF);
  border-radius: 8px;
  padding: 1.5rem;
  margin: 1rem 0;
  text-align: left;
}

.info-card.warning {
  border-left-color: var(--warning-red, #FF4444);
}

.info-card.success {
  border-left-color: var(--success-green, #00FF88);
}

.info-card :deep(h3) {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.info-card :deep(p) {
  color: var(--text-secondary, #B0C4DE);
  font-size: 0.9em;
  line-height: 1.5;
  margin: 0;
}

.info-card :deep(ul) {
  color: var(--text-secondary, #B0C4DE);
  font-size: 0.9em;
  padding-left: 0;
  list-style: none;
}

.info-card :deep(ul li::before) {
  content: ">";
  color: var(--neon-yellow, #FFD700);
  margin-right: 10px;
  font-weight: bold;
}
</style>
