<script setup lang="ts">
const props = defineProps<{
  type: 'critical' | 'action' | 'caution' | 'protip'
  icon?: string
  label?: string
}>()

const typeConfig = {
  critical: { color: '#FF4444', bg: 'rgba(255, 68, 68, 0.1)', defaultLabel: 'CRITICAL' },
  action: { color: '#00FF88', bg: 'rgba(0, 255, 136, 0.1)', defaultLabel: 'ACTION' },
  caution: { color: '#FFA500', bg: 'rgba(255, 165, 0, 0.1)', defaultLabel: 'CAUTION' },
  protip: { color: '#00FFFF', bg: 'rgba(0, 255, 255, 0.1)', defaultLabel: 'PRO TIP' },
}

const config = typeConfig[props.type]
</script>

<template>
  <div
    class="callout-card"
    :style="{
      borderLeftColor: config.color,
      background: config.bg
    }"
  >
    <div v-if="icon" class="callout-icon">{{ icon }}</div>
    <div class="callout-label" :style="{ color: config.color }">
      {{ label || config.defaultLabel }}
    </div>
    <div class="callout-text">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.callout-card {
  border-radius: 8px;
  padding: 1rem;
  text-align: left;
  border-left: 4px solid;
}

.callout-icon {
  font-size: 1.5rem;
  margin-bottom: 0.5rem;
}

.callout-label {
  font-family: 'SHPinscher', sans-serif;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 0.5rem;
}

.callout-text {
  font-size: 0.85rem;
  color: var(--text-secondary, #B0C4DE);
  line-height: 1.5;
}

.callout-text :deep(p) {
  margin: 0;
}
</style>
