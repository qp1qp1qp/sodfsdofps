<template>
  <a href="#main-content" class="skip-to-content">Перейти к основному содержанию</a>
</template>

<style scoped>
.skip-to-content {
  position: absolute;
  left: -9999px;
  top: auto;
  width: 1px;
  height: 1px;
  overflow: hidden;
}

.skip-to-content:focus {
  position: static;
  width: auto;
  height: auto;
  padding: 10px;
  background: #fff;
  color: #000;
  z-index: 1000;
}
</style>
