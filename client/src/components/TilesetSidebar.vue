<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)" title="Tilesets"
    description="Manage and configure your vector tilesets">
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-3">
        <h3 class="text-sm font-medium">Generate New Tileset</h3>
        <div v-if="dataset" class="text-xs text-muted-foreground bg-muted px-4 py-2 rounded">
          Dataset: {{ dataset.name }}
        </div>
        <div class="flex flex-col gap-3 p-4 border rounded-lg">
          <div class="flex flex-col gap-1">
            <label class="text-xs font-medium">Maximum Zoom</label>
            <Select v-model="maxZoom">
              <SelectTrigger class="h-8">
                <SelectValue placeholder="Select maximum zoom" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="g">g (guess)</SelectItem>
                <SelectItem v-for="zoom in Array.from({ length: 23 }, (_, i) => i)" :key="zoom"
                  :value="zoom.toString()">
                  {{ zoom }}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div class="flex items-center justify-between">
            <label class="text-xs font-medium">Drop densest as needed</label>
            <Switch :model-value="dropDensest" @update:model-value="dropDensest = $event" />
          </div>
          <Button @click="handleGenerate" :disabled="!dataset || isCreatingTileset || showProgress" class="h-8">
            <LoaderCircle v-if="isCreatingTileset" class="h-3 w-3 animate-spin mr-2" />
            {{ isCreatingTileset ? 'Generating...' : 'Generate' }}
          </Button>
        </div>
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
      <div class="flex flex-col gap-2">
        <h3 class="text-sm font-medium">Tilesets</h3>
        <div v-if="isFetchingTilesets" class="flex items-center justify-center py-4">
          <LoaderCircle class="h-4 w-4 animate-spin text-muted-foreground" />
          <span class="text-sm text-muted-foreground ml-2">Loading tilesets...</span>
        </div>
        <div v-else-if="tilesets && tilesets.length > 0" class="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="text-xs">ID</TableHead>
                <TableHead class="text-xs">Name</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="tileset in tilesets" :key="tileset.id"
                :data-state="selectedTilesetId === tileset.id && 'selected'" @click="setSelectedTileset(tileset.id)"
                class="cursor-pointer">
                <TableCell class="text-xs font-medium">{{ tileset.id }}</TableCell>
                <TableCell class="text-xs truncate" :title="tileset.name">
                  {{ tileset.name }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <div v-else class="text-center py-4 text-sm text-muted-foreground">
          No tilesets available
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseSidebar from './BaseSidebar.vue'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Switch } from '@/components/ui/switch'
import { Button } from '@/components/ui/button'
import { LoaderCircle, CheckCircle, AlertCircle } from 'lucide-vue-next'
import { useSelectedData } from '@/composables/useSelectedData'
import { useDatasetQuery } from '@/composables/useDatasetQuery'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useProgress } from '@/composables/useProgress'
import { toast } from 'vue-sonner'

defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

defineEmits<{
  'update:open': [value: boolean]
}>()

const { selectedDatasetId, selectedTilesetId, setSelectedTileset } = useSelectedData()
const { dataset } = useDatasetQuery(selectedDatasetId)

const createdTilesetId = ref<number | null>(null)
const showProgress = ref(false)

const {
  tilesets,
  isFetchingTilesets,
  progress,
  isProgressError,
  mutateOnCreateTileset,
  isCreatingTileset,
  isCreateTilesetSuccess,
  refetchTilesets
} = useTilesetQuery(selectedDatasetId, selectedTilesetId, createdTilesetId)

const maxZoom = ref<string>('g')
const dropDensest = ref<boolean>(true)

const { status, progressColors, progressTitle, progressDescription, progressPercentage } = useProgress(
  progress,
  isProgressError,
  {
    processing: 'Generating Tileset...',
    completed: 'Generation Complete!',
    failed: 'Generation Failed',
    processingDescription: 'Converting your dataset to vector tiles with custom options. This may take a few moments.',
    completedDescription: 'Your tileset is ready and available.',
    failedDescription: 'An error occurred while generating your tileset.'
  }
)

const handleGenerate = () => {
  if (!selectedDatasetId.value || !dataset.value) {
    console.error('No dataset selected')
    return
  }

  const tilesetName = `tileset_${Date.now()}`

  mutateOnCreateTileset(
    {
      name: tilesetName,
      maxZoom: maxZoom.value,
      dropDensest: dropDensest.value
    },
    {
      onSuccess: (data) => {
        createdTilesetId.value = data.id
        showProgress.value = true
      },
      onError: (error) => {
        console.error('Error generating tileset:', error)
      }
    }
  )
}

watch(isCreatingTileset, (newVal, oldVal) => {
  if (oldVal && !newVal && isCreateTilesetSuccess.value) {
    toast('Tileset generation started. Processing...', { position: 'top-center' })
  }
})

watch(() => progress.value?.status, (newVal, oldVal) => {
  if (oldVal === 'in_progress' && newVal === 'completed') {
    // Refetch tilesets to show the newly generated tileset
    refetchTilesets()

    setTimeout(() => {
      showProgress.value = false
      createdTilesetId.value = null
      toast('Tileset generation complete! Your tileset is now available.', { position: 'top-center' })
    }, 3000)
  } else if (oldVal === 'in_progress' && newVal === 'failed') {
    toast.error('Failed to generate tileset', { position: 'top-center' })
    setTimeout(() => {
      showProgress.value = false
      createdTilesetId.value = null
    }, 3000)
  }
})

// Watch for tilesets changes after refetch and select the newly created tileset
watch(tilesets, (newVal) => {
  if (createdTilesetId.value && newVal && newVal.length > 0) {
    const newTileset = newVal.find(t => t.id === createdTilesetId.value)
    if (newTileset) {
      setSelectedTileset(createdTilesetId.value)
    }
  }
})
</script>
