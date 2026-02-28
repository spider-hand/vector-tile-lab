<template>
  <BaseSidebar :open="open" @close="emits('close')" title="Upload">
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
          <FileDropzone v-if="!selectedFile" accept=".geojson,.json"
            description="Click to upload or drag and drop your GeoJSON file"
            @files-selected="(files) => selectedFile = files[0]" />
          <div v-if="selectedFile"
            class="border-2 border-solid border-green-600 bg-green-50 dark:bg-green-950 rounded-lg p-4 flex items-center justify-between">
            <div class="flex items-center gap-2 min-w-0 flex-1">
              <CircleCheck class="h-5 w-5 text-green-900 dark:text-green-100 flex-shrink-0" />
              <span class="text-sm text-green-900 dark:text-green-100 font-medium truncate">{{ selectedFile.name }}</span>
            </div>
            <Button variant="ghost" size="sm" @click="clearSelectedFile"
              class="h-6 w-6 p-0 text-green-900 dark:text-green-100 hover:bg-green-100 dark:hover:bg-green-900">
              <X class="h-4 w-4" />
            </Button>
          </div>
        </div>
        <div v-if="selectedFormat === 'shapefile'" class="flex flex-col gap-3">
          <FileDropzone accept=".shp,.shx,.dbf,.prj,.cpg"
            description="Click to upload or drag and drop Shapefile components" multiple
            @files-selected="handleShapefilesSelected" />
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
            <LoaderCircle v-if="status === 'in_progress'" :class="`h-4 w-4 ${progressColors.icon} animate-spin`" />
            <CircleCheck v-else-if="status === 'completed'" :class="`h-4 w-4 ${progressColors.icon}`" />
            <AlertCircle v-else-if="status === 'failed'" :class="`h-4 w-4 ${progressColors.icon}`" />
            <span :class="`text-sm font-medium ${progressColors.text}`">
              {{ progressTitle }}
            </span>
          </div>
          <div class="w-full">
            <div :class="`flex justify-end text-sm mb-1 ${progressColors.text}`">
              <span>{{ progressPercentage }}%</span>
            </div>
            <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
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
        <EmptyState v-else message="No dataset available" />
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import BaseSidebar from './BaseSidebar.vue'
import FileDropzone from './FileDropzone.vue'
import FileUploadItem from './FileUploadItem.vue'
import { Button } from '@/components/ui/button'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { LoaderCircle, X, AlertCircle, File, Files, CircleCheck } from 'lucide-vue-next'
import { useDatasetQuery } from '@/composables/useDatasetQuery'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useProgress } from '@/composables/useProgress'
import { toast } from 'vue-sonner'
import Separator from './ui/separator/Separator.vue'
import EmptyState from './EmptyState.vue'

defineProps<{
  open: boolean
}>()

const emits = defineEmits<{
  close: []
}>()

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

const clearSelectedFile = () => {
  selectedFile.value = null
  selectedFiles.value = {}
  showProgress.value = false
  createdDatasetId.value = null
}

const handleShapefilesSelected = (files: File[]) => {
  for (const file of files) {
    const fileName = file.name.toLowerCase()
    const extension = fileName.split('.').pop() as keyof typeof selectedFiles.value
    if (['shp', 'shx', 'dbf', 'prj', 'cpg'].includes(extension)) {
      selectedFiles.value[extension] = file
    }
  }
}

const removeShapefile = (extension: keyof typeof selectedFiles.value) => {
  selectedFiles.value[extension] = undefined
}

const handleUpload = () => {
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

const getFileName = (filePath: string): string => {
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