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
        <Button @click="handleUpload" :disabled="!selectedFile || isCreatingDataset || showProgress" class="w-full">
          <LoaderCircle v-if="isCreatingDataset" class="animate-spin" />
          {{ isCreatingDataset ? 'Uploading...' : 'Upload' }}
        </Button>
        <div v-if="showProgress"
          :class="`space-y-3 p-4 rounded-lg border-2 ${progressColors.background} ${progressColors.border}`">
          <div class="flex items-center gap-2">
            <LoaderCircle v-if="status === 'in_progress'" class="h-4 w-4 text-blue-600 animate-spin" />
            <CheckCircle v-else-if="status === 'completed'" class="h-4 w-4 text-green-600" />
            <AlertCircle v-else-if="status === 'failed'" class="h-4 w-4 text-red-600" />
            <span :class="`text-sm font-medium ${progressColors.text}`">
              {{ getProgressTitle() }}
            </span>
          </div>
          <div class="w-full">
            <div :class="`flex justify-end text-sm mb-1 ${progressColors.text}`">
              <span>{{ progress?.progress }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div :class="progressColors.bar" class="h-2 rounded-full transition-all duration-300 ease-out"
                :style="{ width: `${progress?.progress ?? 0}%` }">
              </div>
            </div>
          </div>
          <p :class="`text-xs ${progressColors.description}`">
            {{ getProgressDescription() }}
          </p>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useSidebar } from '@/components/ui/sidebar/utils'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { CloudUpload, LoaderCircle, X, CheckCircle, AlertCircle } from 'lucide-vue-next'
import { useDatasetQuery } from '@/composables/useDatasetQuery'
import { toast } from 'vue-sonner'
import type { RetrieveDatasetsProgress200ResponseStatusEnum } from '@/services'


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
const createdDatasetId = ref<number | undefined>(undefined)
const showProgress = ref(false)

const { mutateOnCreateDataset, isCreatingDataset, isCreateDatasetSuccess, progress, isProgressError } = useDatasetQuery(createdDatasetId)

const status = computed<RetrieveDatasetsProgress200ResponseStatusEnum>(() => {
  if (isProgressError.value) return 'failed'
  return progress.value?.status || 'in_progress'
})

const progressColors = computed(() => {
  switch (status.value) {
    case 'completed':
      return {
        background: 'bg-green-50',
        border: 'border-green-200',
        text: 'text-green-900',
        description: 'text-green-700',
        bar: 'bg-green-600'
      }
    case 'failed':
      return {
        background: 'bg-red-50',
        border: 'border-red-200',
        text: 'text-red-900',
        description: 'text-red-700',
        bar: 'bg-red-600'
      }
    case 'in_progress':
    default:
      return {
        background: 'bg-blue-50',
        border: 'border-blue-200',
        text: 'text-blue-900',
        description: 'text-blue-700',
        bar: 'bg-blue-600'
      }
  }
})

function triggerFileInput() {
  fileInput.value?.click()
}

function clearSelectedFile() {
  selectedFile.value = null
  showProgress.value = false
  createdDatasetId.value = undefined
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

    mutateOnCreateDataset({ name: fileName, file: selectedFile.value }, {
      onSuccess: (data) => {
        createdDatasetId.value = data.id
        showProgress.value = true
      }
    })
  }
}

function getProgressTitle() {
  if (isProgressError.value || progress.value?.status === 'failed') return 'Processing Failed'
  if (progress?.value?.status === 'completed') return 'Processing Complete!'
  return 'Processing Dataset...'
}

function getProgressDescription() {
  if (isProgressError.value) return 'An error occurred while processing your file.'
  if (progress.value?.status === 'completed') return 'Your vector tiles are ready and available on the map.'
  return 'Converting your GeoJSON file to vector tiles. This may take a few moments.'
}

watch(isCreatingDataset, (newVal, oldVal) => {
  if (oldVal && !newVal && isCreateDatasetSuccess.value) {
    toast('File uploaded successfully. Processing started...', { position: 'top-center' })
  }
})

watch(() => progress.value?.status, (status) => {
  if (status === 'completed') {
    setTimeout(() => {
      clearSelectedFile()
      toast('Processing complete! Your dataset is now available.', { position: 'top-center' })
      emits('update:open', false)
    }, 3000)
  } else if (status === 'failed') {
    toast.error('Failed to process dataset', { position: 'top-center' })
    showProgress.value = false
  }
})

watch(() => isProgressError.value, (isError) => {
  if (isError) {
    toast.error('Failed to process dataset', { position: 'top-center' })
    showProgress.value = false
  }
})
</script>
