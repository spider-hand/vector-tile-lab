<template>
  <Sheet :open="open" @update:open="(value) => $emit('update:open', value)" :modal="false">
    <SheetContent side="left" class="w-80 flex flex-col gap-4" :style="{ marginLeft: sidebarMargin }">
      <SheetHeader>
        <SheetTitle>Upload GeoJSON</SheetTitle>
        <SheetDescription>
          Select a file from your device to display on the map.
        </SheetDescription>
      </SheetHeader>
      <div class="flex flex-col gap-2 px-4">
        <div v-if="!selectedFile"
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
          @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
          <CloudUpload class="mx-auto h-8 w-8 text-gray-400 mb-4" />
          <p class="text-sm text-gray-600">
            Click to upload or drag and drop
          </p>
          <input ref="fileInput" type="file" accept=".geojson,.json" class="hidden" @change="handleFileSelect" />
        </div>
        <div v-if="selectedFile"
          class="border-2 border-solid border-green-300 bg-green-50 rounded-lg p-4 flex items-center justify-between">
          <div class="flex items-center gap-2 min-w-0 flex-1">
            <CloudUpload class="h-5 w-5 text-green-600 flex-shrink-0" />
            <span class="text-sm text-green-700 font-medium truncate">{{ selectedFile.name }}</span>
          </div>
          <Button variant="ghost" size="sm" @click="clearSelectedFile"
            class="h-6 w-6 p-0 text-green-600 hover:text-green-800 hover:bg-green-100">
            <X class="h-4 w-4" />
          </Button>
        </div>
        <Button @click="handleUpload" :disabled="!selectedFile || isCreatingDataset" class="w-full">
          <LoaderCircle v-if="isCreatingDataset" class="animate-spin" />
          {{ isCreatingDataset ? 'Uploading...' : 'Upload' }}
        </Button>
      </div>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useSidebar } from '@/components/ui/sidebar/utils'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { CloudUpload, LoaderCircle, X } from 'lucide-vue-next'
import { useDatasetQuery } from '@/composables/useDatasetQuery'
import { toast } from 'vue-sonner'


defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

const emits = defineEmits<{
  'update:open': [value: boolean]
}>()

const { open: sidebarOpen, isMobile } = useSidebar()

const sidebarMargin = computed(() => {
  if (isMobile.value) {
    return '0'
  }
  return sidebarOpen.value ? '10rem' : '0'
})


const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)

const { mutateOnCreateDataset, isCreatingDataset, isCreateDatasetSuccess } = useDatasetQuery()

function triggerFileInput() {
  fileInput.value?.click()
}

function clearSelectedFile() {
  selectedFile.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    selectedFile.value = file
  }
}

function handleDrop(event: DragEvent) {
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    if (file.name.endsWith('.geojson') || file.name.endsWith('.json')) {
      selectedFile.value = file
    }
  }
}

function handleUpload() {
  if (selectedFile.value) {
    const fileName = selectedFile.value.name.replace(/\.(geojson|json)$/, '')

    mutateOnCreateDataset({ name: fileName, file: selectedFile.value })
  }
}

watch(isCreatingDataset, (newVal, oldVal) => {
  if (oldVal && !newVal && isCreateDatasetSuccess.value) {
    clearSelectedFile()
    toast('File uploaded successfully', { position: 'top-center' })
    emits('update:open', false)
  }
})
</script>
