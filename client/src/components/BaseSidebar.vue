<template>
  <Sheet :open="open" @update:open="(value: boolean) => $emit('update:open', value)" :modal="false">
    <SheetContent side="left" class="flex flex-col" :class="width" :style="{ marginLeft: sidebarMargin }"
      @interact-outside="(e) => e.preventDefault()">
      <SheetHeader>
        <SheetTitle>{{ title }}</SheetTitle>
        <SheetDescription>{{ description }}</SheetDescription>
      </SheetHeader>

      <div class="flex flex-col flex-1 min-h-0 rounded-lg px-4 pb-4 overflow-y-auto sidebar-scrollbar">
        <slot />
      </div>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSidebar } from '@/components/ui/sidebar/utils'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'

defineProps({
  open: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  width: {
    type: String,
    default: 'w-80'
  }
})

defineEmits<{
  'update:open': [value: boolean]
}>()

const { open: sidebarOpen, isMobile } = useSidebar()

const sidebarMargin = computed(() => {
  if (isMobile.value) {
    return '0'
  }
  return sidebarOpen.value ? '10rem' : '0'
})
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