<template>
  <div class="border-2 border-solid rounded-lg p-4 flex items-center justify-between"
    :class="file ? 'border-green-300 bg-green-50' : 'border-gray-200 bg-gray-50'">
    <div v-if="!file" class="flex items-center gap-2">
      <span class="text-xs font-mono px-2 py-1 rounded"
        :class="file ? 'bg-transparent text-green-700' : 'bg-gray-100'">{{ extension }}</span>
    </div>
    <div v-else class="flex items-center gap-2 min-w-0 flex-1">
      <CloudUpload class="h-5 w-5 text-green-600 flex-shrink-0" />
      <span class="text-sm text-green-700 font-medium truncate">{{ file.name }}</span>
    </div>
    <Button v-if="file" variant="ghost" size="sm" @click="$emit('remove')"
      class="h-6 w-6 p-0 text-green-600 hover:text-green-800 hover:bg-green-100">
      <X class="h-4 w-4" />
    </Button>
  </div>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { CloudUpload, X } from 'lucide-vue-next'

defineProps<{
  extension: string
  file?: File
}>()

defineEmits<{
  remove: []
}>()
</script>