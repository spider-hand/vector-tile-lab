<template>
  <div
    class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
    @click="triggerFileInput"
    @dragover.prevent
    @drop.prevent="handleDrop"
  >
    <CloudUpload class="mx-auto h-8 w-8 text-gray-400 mb-4" />
    <p class="text-sm text-muted-foreground">
      {{ description }}
    </p>
    <input
      ref="fileInput"
      type="file"
      :accept="accept"
      :multiple="multiple"
      class="hidden"
      @change="handleFileSelect"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { CloudUpload } from 'lucide-vue-next'

const props = defineProps<{
  accept: string
  multiple?: boolean
  description?: string
}>()

const emit = defineEmits<{
  'files-selected': [files: File[]]
}>()

const fileInput = ref<HTMLInputElement | null>(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const isValidFileType = (file: File): boolean => {
  const fileName = file.name.toLowerCase()
  const acceptedTypes = props.accept.split(',').map(t => t.trim().toLowerCase())
  return acceptedTypes.some(type => fileName.endsWith(type))
}

const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    const validFiles = Array.from(files).filter(file => isValidFileType(file))
    if (validFiles.length > 0) {
      emit('files-selected', validFiles)
    }
  }
  // Reset input so the same file can be selected again
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

const handleDrop = (event: DragEvent) => {
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const validFiles = Array.from(files).filter(file => isValidFileType(file))
    if (validFiles.length > 0) {
      emit('files-selected', validFiles)
    }
  }
}
</script>
