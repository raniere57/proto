<template>
  <div class="not-found">
    <i class="pi pi-compass"></i>
    <h1>404</h1>
    <p>Página não encontrada</p>
    <router-link to="/">
      <Button label="Voltar para Home" icon="pi pi-home" />
    </router-link>
  </div>
</template>

<style scoped>
.not-found {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 60vh; text-align: center;
}
.not-found i { font-size: 4rem; color: #667eea; margin-bottom: 1rem; }
.not-found h1 { font-size: 4rem; color: #1a1a2e; margin-bottom: 0.5rem; }
.not-found p { color: #6c757d; font-size: 1.2rem; margin-bottom: 2rem; }
</style>
