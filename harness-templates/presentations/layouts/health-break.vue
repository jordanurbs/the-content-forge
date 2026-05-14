<template>
  <div class="slidev-layout health-break-layout">
    <h2 class="title">Health Break</h2>
    <slot />
  </div>
</template>

<style scoped>
.health-break-layout {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  background: linear-gradient(135deg, #0A1628 0%, #1A2744 100%);
  padding: 4rem 2rem 3.5rem;  /* top padding for HUD, bottom for terminal */
}

.title {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #00FF88;
  font-size: 2em;
  margin-bottom: 1.5rem;
}
</style>
