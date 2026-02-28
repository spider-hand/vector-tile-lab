<template>
  <div
    class="absolute inset-0 flex flex-col bg-background border-r transition-transform duration-300 ease-in-out"
    :class="open ? 'translate-x-0' : '-translate-x-full'"
  >
    <div class="flex items-center justify-between px-4 py-3">
      <h2 class="text-sm font-semibold">{{ title }}</h2>
      <Button variant="ghost" size="icon" class="h-6 w-6" @click="$emit('close')">
        <X class="h-4 w-4" />
      </Button>
    </div>
    <div class="flex-1 min-h-0 overflow-y-auto px-4 py-3 sidebar-scrollbar">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { X } from 'lucide-vue-next'

defineProps<{
  title: string
  open: boolean
}>()

defineEmits<{
  close: []
}>()
</script>

<style scoped>
.sidebar-scrollbar::-webkit-scrollbar {
  width: 4px;
}

.sidebar-scrollbar::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.sidebar-scrollbar::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.sidebar-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>