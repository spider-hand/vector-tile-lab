<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)" title="Upload Data"
    description="Select a file from your device to display on the map.">
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-2">
        <h3 class="text-sm font-medium">File Format</h3>
        <Tabs v-model="selectedFormat" class="w-full">
          <TabsList class="grid w-full grid-cols-2">
            <TabsTrigger value="geojson">
              <File />
              GeoJSON
            </TabsTrigger>
            <TabsTrigger value="shapefile">
              <Files />
              Shapefile
            </TabsTrigger>
          </TabsList>
        </Tabs>
      </div>
      <div class="flex flex-col gap-2">
        <div v-if="selectedFormat === 'geojson'">
          <div v-if="!selectedFile"
            class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
            @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
            <CloudUpload class="mx-auto h-8 w-8 text-gray-400 mb-4" />
            <p class="text-sm text-muted-foreground">
              Click to upload or drag and drop your GeoJSON file
            </p>
            <input ref="fileInput" type="file" :accept="acceptedFileTypes" class="hidden" @change="handleFileSelect" />
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
        </div>
        <div v-if="selectedFormat === 'shapefile'" class="flex flex-col gap-3">
          <div
            class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-gray-400 transition-colors cursor-pointer"
            @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
            <CloudUpload class="mx-auto h-8 w-8 text-gray-400 mb-4" />
            <p class="text-sm text-muted-foreground mb-2">
              Click to upload or drag and drop Shapefile components
            </p>
            <input ref="fileInput" type="file" :accept="acceptedFileTypes" class="hidden" @change="handleFileSelect"
              multiple />
          </div>
          <div class="space-y-2">
            <h4 class="text-xs font-medium text-muted-foreground">Required Files</h4>
            <div class="grid grid-cols-1 gap-2">
              <FileUploadItem extension=".shp" :file="selectedFiles.shp" @remove="() => removeShapefile('shp')" />
              <FileUploadItem extension=".shx" :file="selectedFiles.shx" @remove="() => removeShapefile('shx')" />
              <FileUploadItem extension=".dbf" :file="selectedFiles.dbf" @remove="() => removeShapefile('dbf')" />
            </div>
            <h4 class="text-xs font-medium text-muted-foreground mt-3">Optional Files</h4>
            <div class="grid grid-cols-1 gap-2">
              <FileUploadItem extension=".prj" :file="selectedFiles.prj" @remove="() => removeShapefile('prj')" />
              <FileUploadItem extension=".cpg" :file="selectedFiles.cpg" @remove="() => removeShapefile('cpg')" />
            </div>
          </div>
        </div>
        <Button @click="handleUpload" :disabled="!canUpload || isCreatingDataset || showProgress" class="w-full">
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
                <TableCell v-if="dataset.geojsonFile" class="text-xs truncate" :title="dataset.geojsonFile">
                  {{ getFileName(dataset.geojsonFile) }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <div v-else class="text-center py-8 text-sm text-muted-foreground">
          <div class="flex flex-col items-center gap-2">
            <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
              <PackageSearch />
            </div>
            <p>No dataset available</p>
          </div>
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import BaseSidebar from './BaseSidebar.vue'
import FileUploadItem from './FileUploadItem.vue'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { CloudUpload, LoaderCircle, X, CheckCircle, AlertCircle, File, Files, PackageSearch } from 'lucide-vue-next'
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
const selectedFiles = ref<{
  shp?: File
  shx?: File
  dbf?: File
  prj?: File
  cpg?: File
}>({})
const createdDatasetId = ref<number | null>(null)
const showProgress = ref(false)
const selectedFormat = ref<'geojson' | 'shapefile'>('geojson')

const { selectedDatasetId, selectedTilesetId, setSelectedDataset, setSelectedTileset } = useSelectedData()
const { mutateOnCreateDataset, isCreatingDataset, isCreateDatasetSuccess, progress, isProgressError, datasets, isFetchingDatasets, refetchDatasets } = useDatasetQuery(selectedDatasetId, createdDatasetId)
const { tilesets } = useTilesetQuery(selectedDatasetId, selectedTilesetId)

const acceptedFileTypes = computed(() => {
  return selectedFormat.value === 'geojson' ? '.geojson,.json' : '.shp,.shx,.dbf,.prj,.cpg'
})

const canUpload = computed(() => {
  if (selectedFormat.value === 'geojson') {
    return !!selectedFile.value
  } else {
    return !!(selectedFiles.value.shp && selectedFiles.value.shx && selectedFiles.value.dbf)
  }
})

const progressMessages = computed(() => {
  return {
    processing: 'Processing Dataset...',
    completed: 'Processing Complete!',
    failed: 'Processing Failed',
    processingDescription: 'Converting your GeoJSON file to vector tiles. This may take a few moments.',
    completedDescription: 'Your vector tiles are ready and available on the map.',
    failedDescription: 'An error occurred while processing your file.'
  }
})

const { status, progressColors, progressTitle, progressDescription, progressPercentage } = useProgress(
  progress,
  isProgressError,
  progressMessages.value
)

function triggerFileInput() {
  fileInput.value?.click()
}

function clearSelectedFile() {
  selectedFile.value = null
  selectedFiles.value = {}
  showProgress.value = false
  createdDatasetId.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function handleFileSelect(event: Event) {
  const target = event.target as HTMLInputElement
  const files = target.files

  if (selectedFormat.value === 'geojson') {
    const file = files?.[0]
    if (file && isValidFileType(file)) {
      selectedFile.value = file
    }
  } else {
    if (files) {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        if (isValidFileType(file)) {
          addShapefile(file)
        }
      }
    }
  }
}

function isValidFileType(file: File): boolean {
  const fileName = file.name.toLowerCase()
  if (selectedFormat.value === 'geojson') {
    return fileName.endsWith('.geojson') || fileName.endsWith('.json')
  } else {
    return fileName.endsWith('.shp') || fileName.endsWith('.shx') ||
      fileName.endsWith('.dbf') || fileName.endsWith('.prj') ||
      fileName.endsWith('.cpg')
  }
}

function addShapefile(file: File) {
  const fileName = file.name.toLowerCase()
  const extension = fileName.split('.').pop() as keyof typeof selectedFiles.value

  if (['shp', 'shx', 'dbf', 'prj', 'cpg'].includes(extension)) {
    selectedFiles.value[extension] = file
  }
}

function removeShapefile(extension: keyof typeof selectedFiles.value) {
  selectedFiles.value[extension] = undefined
}

function handleDrop(event: DragEvent) {
  const files = event.dataTransfer?.files
  if (files && files.length > 0) {
    if (selectedFormat.value === 'geojson') {
      const file = files[0]
      if (isValidFileType(file)) {
        selectedFile.value = file
      }
    } else {
      for (let i = 0; i < files.length; i++) {
        const file = files[i]
        if (isValidFileType(file)) {
          addShapefile(file)
        }
      }
    }
  }
}

function handleUpload() {
  if (selectedFormat.value === 'geojson' && selectedFile.value) {
    const fileName = selectedFile.value.name.replace(/\.(geojson|json)$/, '')

    mutateOnCreateDataset({
      name: fileName,
      geojsonFile: selectedFile.value
    }, {
      onSuccess: (data) => {
        createdDatasetId.value = data.id
        showProgress.value = true
      }
    })
  } else if (selectedFormat.value === 'shapefile' && canUpload.value) {
    const fileName = selectedFiles.value.shp!.name.replace(/\.shp$/, '')

    mutateOnCreateDataset({
      name: fileName,
      shpFile: selectedFiles.value.shp,
      shxFile: selectedFiles.value.shx,
      dbfFile: selectedFiles.value.dbf,
      prjFile: selectedFiles.value.prj,
      cpgFile: selectedFiles.value.cpg,
    }, {
      onSuccess: (data) => {
        createdDatasetId.value = data.id
        showProgress.value = true
      }
    })
  }
}

function getFileName(filePath: string): string {
  return filePath.split('/').pop()?.replace(/\.(geojson|json|shp)$/i, '') || filePath
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

watch(selectedFormat, () => {
  clearSelectedFile()
})
</script>