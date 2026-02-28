<template>
  <BaseSidebar :open="open" @close="$emit('close')" title="Tweak">
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-3">
        <h3 class="text-sm font-medium">Generate New Tileset</h3>
        <div class="flex flex-col gap-3 p-4 border rounded-lg">
          <Tabs v-model="activeTab" class="w-full">
            <TabsList class="grid w-full grid-cols-2">
              <TabsTrigger value="basic">
                <Settings />
                Basic
              </TabsTrigger>
              <TabsTrigger value="advanced">
                <Sparkle />
                Advanced
              </TabsTrigger>
            </TabsList>
            <TabsContent value="basic" class="mt-3">
              <TooltipProvider>
                <div class="flex flex-col gap-3">
                  <div class="flex flex-col gap-1">
                    <InfoTooltipLabel tooltip-text="The highest zoom level for which tiles are generated (default 14)"
                      label-text="Maximum Zoom" />
                    <Select v-model="maximumZoom">
                      <SelectTrigger class="h-8">
                        <SelectValue placeholder="Select maximum zoom" />
                      </SelectTrigger>
                      <SelectContent class="z-[9999]">
                        <SelectItem value="g">g (guess)</SelectItem>
                        <SelectItem v-for="zoom in Array.from({ length: 23 }, (_, i) => i)" :key="zoom"
                          :value="zoom.toString()">
                          {{ zoom }}
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <LabeledSwitch v-model="dropDensestAsNeeded"
                    tooltip-text="If the tiles are too big at low zoom levels, drop the least-visible features to allow tiles to be created with those features that remain"
                    label-text="Drop densest as needed" />
                  <LabeledSwitch v-model="coalesceDensestAsNeeded"
                    tooltip-text="If the tiles are too big at low or medium zoom levels, merge as many features together as are necessary to allow tiles to be created with those features that are still distinguished"
                    label-text="Coalesce densest as needed" />
                  <LabeledSwitch v-model="extendZoomsIfStillDropping"
                    tooltip-text="If even the tiles at high zoom levels are too big, keep adding zoom levels until one is reached that can represent all the features"
                    label-text="Extend zooms if still dropping" />
                </div>
              </TooltipProvider>
            </TabsContent>
            <TabsContent value="advanced" class="mt-3">
              <div class="flex flex-col gap-2">
                <label class="text-xs text-muted-foreground">
                  Tippecanoe Options
                </label>
                <Input v-model="rawOptions" placeholder="-zg --drop-densest-as-needed" class="h-8 text-xs font-mono" />
              </div>
            </TabsContent>
          </Tabs>
          <Button @click="handleGenerate" :disabled="!dataset || isCreatingTileset || showProgress" class="h-8">
            <LoaderCircle v-if="isCreatingTileset" class="h-3 w-3 animate-spin mr-2" />
            {{ isCreatingTileset ? 'Generating...' : 'Generate' }}
          </Button>
        </div>
        <div v-if="showProgress"
          :class="`space-y-3 p-4 rounded-lg border-2 ${progressColors.background} ${progressColors.border}`">
          <div class="flex items-center gap-2">
            <LoaderCircle v-if="status === 'in_progress'" :class="`h-4 w-4 ${progressColors.icon} animate-spin`" />
            <CheckCircle v-else-if="status === 'completed'" :class="`h-4 w-4 ${progressColors.icon}`" />
            <AlertCircle v-else-if="status === 'failed'" :class="`h-4 w-4 ${progressColors.icon}`" />
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
        <div v-else-if="tilesets && tilesets.length > 0" class="flex flex-col gap-2">
          <div class="rounded-lg border">
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
          <Button @click="handleExport" :disabled="!selectedTilesetId" variant="outline" class="h-8">
            Export
          </Button>
        </div>
        <EmptyState v-else message="No tileset available" />
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import BaseSidebar from './BaseSidebar.vue'
import InfoTooltipLabel from './InfoTooltipLabel.vue'
import LabeledSwitch from './LabeledSwitch.vue'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { TooltipProvider } from '@/components/ui/tooltip'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Input } from '@/components/ui/input'
import { LoaderCircle, CheckCircle, AlertCircle, Settings, Sparkle } from 'lucide-vue-next'
import { useSelectedData } from '@/composables/useSelectedData'
import { useDatasetQuery } from '@/composables/useDatasetQuery'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useProgress } from '@/composables/useProgress'
import { toast } from 'vue-sonner'
import EmptyState from './EmptyState.vue'

defineProps<{
  open: boolean
}>()

defineEmits<{
  close: []
}>()

type TweakTabType = 'basic' | 'advanced'

const { selectedDatasetId, selectedTilesetId, setSelectedTileset } = useSelectedData()
const { dataset } = useDatasetQuery(selectedDatasetId)

const createdTilesetId = ref<number | null>(null)
const showProgress = ref(false)
const activeTab = ref<TweakTabType>('basic')
const rawOptions = ref<string>('')

const {
  tilesets,
  isFetchingTilesets,
  presignedUrl,
  progress,
  isProgressError,
  mutateOnCreateTileset,
  isCreatingTileset,
  isCreateTilesetSuccess,
  refetchTilesets
} = useTilesetQuery(selectedDatasetId, selectedTilesetId, createdTilesetId)

const maximumZoom = ref<string>('g')
const dropDensestAsNeeded = ref<boolean>(true)
const coalesceDensestAsNeeded = ref<boolean>(false)
const extendZoomsIfStillDropping = ref<boolean>(false)

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

  const options = activeTab.value === 'advanced'
    ? {
      name: tilesetName,
      rawOptions: rawOptions.value ?? undefined
    }
    : {
      name: tilesetName,
      maximumZoom: maximumZoom.value,
      dropDensestAsNeeded: dropDensestAsNeeded.value,
      coalesceDensestAsNeeded: coalesceDensestAsNeeded.value,
      extendZoomsIfStillDropping: extendZoomsIfStillDropping.value
    }

  mutateOnCreateTileset(
    options,
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
      rawOptions.value = ''
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

const handleExport = () => {
  if (!presignedUrl.value?.presignedUrl) {
    toast.error('Failed to export tileset', { position: 'top-center' })
    return
  }
  window.open(presignedUrl.value.presignedUrl, '_blank')
}
</script>
