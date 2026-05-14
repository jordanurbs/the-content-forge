<template>
  <div class="slidev-layout two-col">
    <div class="header">
      <slot name="header" />
    </div>
    <div class="grid">
      <slot />
    </div>
  </div>
</template>

<style scoped>
.two-col {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 4rem 3.5rem 3.5rem;  /* top padding for HUD, bottom for terminal */
  background-color: #0A1628;
}

.header {
  margin-bottom: 1.5rem;
}

.header :deep(h2) {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #FFD700;
  font-size: 2em;
}

.header :deep(p) {
  font-family: 'Courier Prime Code', monospace;
  color: #B0C4DE;
  font-size: 1.1rem;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
  flex: 1;
  align-content: start;
}
</style>
