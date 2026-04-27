<template>
  <Dialog v-model:visible="visible" :header="title" modal :closable="!loading" class="confirm-dialog" :draggable="false">
    <div class="confirm-body">
      <i v-if="icon" :class="icon" class="confirm-icon" :style="{ color: iconColor }"></i>
      <p v-if="message" class="confirm-message">{{ message }}</p>
      <slot />
    </div>
    <template #footer>
      <div class="confirm-actions">
        <Button :label="cancelLabel" severity="secondary" @click="cancel" :disabled="loading" />
        <Button v-if="!hideConfirm" :label="confirmLabel" :severity="severity" :loading="loading" @click="confirm" autofocus />
      </div>
    </template>
  </Dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'

const props = withDefaults(defineProps<{
  visible: boolean
  title?: string
  message?: string
  confirmLabel?: string
  cancelLabel?: string
  severity?: 'danger' | 'info' | 'warn' | 'success'
  loading?: boolean
  icon?: string | null
  hideConfirm?: boolean
}>(), {
  title: 'Confirmar',
  message: '',
  confirmLabel: 'Confirmar',
  cancelLabel: 'Cancelar',
  severity: 'danger',
  loading: false,
  icon: 'pi pi-exclamation-triangle',
  hideConfirm: false,
})

const emit = defineEmits<{
  confirm: []
  cancel: []
  'update:visible': [value: boolean]
}>()

const visible = ref(props.visible)
watch(() => props.visible, (v) => visible.value = v)
watch(visible, (v) => emit('update:visible', v))

const iconColor = computed(() => ({
  danger: '#e74c3c',
  warn: '#f39c12',
  info: '#3498db',
  success: '#27ae60',
  '': '#667eea',
}[props.severity] || '#667eea'))

function confirm() { emit('confirm') }
function cancel() { visible.value = false; emit('cancel') }
</script>

<style scoped>
.confirm-body { text-align: center; padding: 0.5rem 0; }
.confirm-icon { font-size: 2.5rem; margin-bottom: 0.75rem; display: block; }
.confirm-message { font-size: 1rem; color: #2c3e50; line-height: 1.5; }
.confirm-actions { display: flex; gap: 0.75rem; justify-content: center; }
</style>
