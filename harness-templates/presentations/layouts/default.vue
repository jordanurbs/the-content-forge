<template>
  <div class="slidev-layout default">
    <slot />
  </div>
</template>

<style scoped>
.default {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 4rem 3.5rem 3.5rem;  /* top padding for HUD, bottom for terminal */
  background-color: #0A1628;
  color: #FFFFFF;
  font-family: 'Courier Prime Code', monospace;
}

.default :deep(h1) {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 2.5em;
  color: #FFFFFF;
}

.default :deep(h2) {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #FFD700;
  font-size: 2em;
  margin-bottom: 0.5rem;
}

.default :deep(h3) {
  font-family: 'SHPinscher', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 1.5em;
}

.default :deep(p) {
  color: #B0C4DE;
  line-height: 1.6;
}

.default :deep(ul) {
  list-style-type: none;
  padding: 0;
}

.default :deep(ul li::before) {
  content: ">";
  color: #FFD700;
  margin-right: 10px;
  font-weight: bold;
}

.default :deep(strong) {
  color: #FFFFFF;
}

.default :deep(em) {
  color: #00FFFF;
  font-style: normal;
}
</style>
