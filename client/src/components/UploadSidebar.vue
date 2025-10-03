<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)"
               title="Upload GeoJSON" description="Select a file from your device to display on the map.">
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <div v-if="!selectedFile"
          class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
          @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
          <CloudUpload class="mx-auto h-8 w-8 text-gray-400 mb-4" />
          <p class="text-sm text-muted-foreground">
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
              {{ progressTitle }}
            </span>
          </div>
          <div class="w-full">
            <div :class="`flex justify-end text-sm mb-1 ${progressColors.text}`">
              <span>{{ progressPercentage }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2">
              <div :class="progressColors.bar" class="h-2 rounded-full transition-all duration-300 ease-out"
                :style="{ width: `${progressPercentage}%` }">
              </div>
            </div>
          </div>
          <p :class="`text-xs ${progressColors.description}`">
            {{ progressDescription }}
          </p>
        </div>
      </div>

      <Separator />

      <div class="flex flex-col gap-2">
        <h3 class="text-sm font-medium">Datasets</h3>
        <div v-if="isFetchingDatasets" class="flex items-center justify-center py-4">
          <LoaderCircle class="h-4 w-4 animate-spin text-muted-foreground" />
          <span class="text-sm text-muted-foreground ml-2">Loading datasets...</span>
        </div>
        <div v-else-if="datasets && datasets.length > 0" class="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="text-xs">ID</TableHead>
                <TableHead class="text-xs">Filename</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="dataset in datasets" :key="dataset.id"
                :data-state="selectedDatasetId === dataset.id && 'selected'" @click="setSelectedDataset(dataset.id)"
                class="cursor-pointer">
                <TableCell class="text-xs font-medium">{{ dataset.id }}</TableCell>
                <TableCell class="text-xs truncate" :title="dataset.geojsonFile">
                  {{ getFileName(dataset.geojsonFile) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <div v-else class="text-center py-4 text-sm text-muted-foreground">
          No datasets available
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseSidebar from './BaseSidebar.vue'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { CloudUpload, LoaderCircle, X, CheckCircle, AlertCircle } from 'lucide-vue-next'
import { useDatasetQuery } from '@/composables/useDatasetQuery'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useProgress } from '@/composables/useProgress'
import { toast } from 'vue-sonner'

import Separator from './ui/separator/Separator.vue'

defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

const emits = defineEmits<{
  'update:open': [value: boolean]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const createdDatasetId = ref<number | null>(null)
const showProgress = ref(false)

const { selectedDatasetId, selectedTilesetId, setSelectedDataset, setSelectedTileset } = useSelectedData()
const { mutateOnCreateDataset, isCreatingDataset, isCreateDatasetSuccess, progress, isProgressError, datasets, isFetchingDatasets, refetchDatasets } = useDatasetQuery(selectedDatasetId, createdDatasetId)
const { tilesets } = useTilesetQuery(selectedDatasetId, selectedTilesetId)

const { status, progressColors, progressTitle, progressDescription, progressPercentage } = useProgress(
  progress,
  isProgressError,
  {
    processing: 'Processing Dataset...',
    completed: 'Processing Complete!',
    failed: 'Processing Failed',
    processingDescription: 'Converting your GeoJSON file to vector tiles. This may take a few moments.',
    completedDescription: 'Your vector tiles are ready and available on the map.',
    failedDescription: 'An error occurred while processing your file.'
  }
)

function triggerFileInput() {
  fileInput.value?.click()
}

function clearSelectedFile() {
  selectedFile.value = null
  showProgress.value = false
  createdDatasetId.value = null
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

function getFileName(filePath: string): string {
  return filePath.split('/').pop()?.replace(/\.(geojson|json)$/i, '') || filePath
}

watch(isFetchingDatasets, (newVal, oldVal) => {
  if (oldVal && !newVal && !selectedDatasetId.value && datasets.value && datasets.value.length > 0) {
    setSelectedDataset(datasets.value[0].id)
  }
})

watch(isCreatingDataset, (newVal, oldVal) => {
  if (oldVal && !newVal && isCreateDatasetSuccess.value) {
    toast('File uploaded successfully. Processing started...', { position: 'top-center' })
  }
})

watch(() => progress.value?.status, (newVal, oldVal) => {
  if (oldVal === 'in_progress' && newVal === 'completed') {
    refetchDatasets()

    if (createdDatasetId.value) {
      setSelectedDataset(createdDatasetId.value)
    }

    setTimeout(() => {
      clearSelectedFile()
      toast('Processing complete! Your dataset is now available.', { position: 'top-center' })
      emits('update:open', false)
    }, 3000)
  } else if (oldVal === 'in_progress' && newVal === 'failed') {
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

watch(tilesets, (newTilesets) => {
  if (newTilesets && newTilesets.length > 0 && !selectedTilesetId.value) {
    setSelectedTileset(newTilesets[0].id)
  }
})
</script>
