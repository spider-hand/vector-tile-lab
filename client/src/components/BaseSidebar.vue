<template>
  <div class="fixed top-4 left-[224px] bottom-4 z-[998]" :class="width">
    <Card class="flex flex-col h-full py-4">
      <CardHeader class="flex flex-row items-center justify-between space-y-0 px-4">
        <CardTitle>{{ title }}</CardTitle>
        <Button variant="ghost" size="icon" class="h-6 w-6" @click="$emit('close')">
          <X class="h-4 w-4" />
        </Button>
      </CardHeader>
      <CardContent class="flex-1 min-h-0 overflow-y-auto sidebar-scrollbar px-4">
        <slot />
      </CardContent>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { X } from 'lucide-vue-next'

withDefaults(defineProps<{
  title: string
  width?: string
}>(), {
  width: 'w-80'
})

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