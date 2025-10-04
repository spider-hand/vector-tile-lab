<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)" title="Comparison"
    description="Compare tile distribution across tilesets" :width="'w-160'">
    <div class="flex flex-col gap-4">
      <div class="flex flex-col gap-3">
        <h3 class="text-sm font-medium">Select Tilesets for Comparison</h3>
        <div v-if="availableTilesets.length === 0" class="text-sm text-muted-foreground text-center py-4">
          No tilesets available for comparison
        </div>
        <div v-else>
          <DropdownMenu>
            <DropdownMenuTrigger as-child>
              <Button variant="outline" class="w-full justify-between">
                <span class="text-muted-foreground">
                  Select tilesets...
                </span>
                <ChevronDown class="h-4 w-4 opacity-50" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent class="w-full">
              <DropdownMenuCheckboxItem v-for="tileset in availableTilesets" :key="tileset.id"
                :model-value="selectedTilesetIds.includes(tileset.id)"
                @update:model-value="toggleTilesetSelection(tileset.id)">
                {{ tileset.name }}
              </DropdownMenuCheckboxItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      <div v-if="chartData && selectedTilesetIds.length > 0" class="flex flex-col gap-3">
        <h3 class="text-sm font-medium">Tiles by Zoom Level</h3>
        <div class="bg-gray-50 rounded-lg p-4">
          <canvas ref="chartRef" class="w-full" style="height: 300px;"></canvas>
        </div>
        <div class="grid grid-cols-1 gap-2">
          <div v-for="(tileset, index) in comparisonData" :key="tileset.id"
            class="flex items-center justify-between px-4 py-2 border rounded text-xs">
            <div class="flex items-center gap-2">
              <div class="w-3 h-3 rounded" :style="{ backgroundColor: chartColors[index % chartColors.length] }"></div>
              <span class="font-medium">{{ tileset.name }}</span>
            </div>
            <span class="text-muted-foreground">
              {{ tileset.totalTiles.toLocaleString() }} tiles
            </span>
          </div>
        </div>
      </div>
      <div v-else-if="selectedTilesetIds.length === 0" class="text-center py-8 text-sm text-muted-foreground">
        <div class="flex flex-col items-center gap-2">
          <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
            📊
          </div>
          <p>Select tilesets to compare their tile distribution</p>
        </div>
      </div>
      <div v-else class="text-center py-8 text-sm text-muted-foreground">
        <div class="flex flex-col items-center gap-2">
          <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
            📊
          </div>
          <p>No data available</p>
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import BaseSidebar from './BaseSidebar.vue'
import { Button } from '@/components/ui/button'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
  DropdownMenuCheckboxItem
} from '@/components/ui/dropdown-menu'
import { ChevronDown } from 'lucide-vue-next'
import { useSelectedData } from '@/composables/useSelectedData'
import { useDatasetQuery } from '@/composables/useDatasetQuery'
import useTilesetQuery from '@/composables/useTilesetQuery'
import type { TileMetadataResponse } from '@/types'
import {
  Chart,
  CategoryScale,
  LinearScale,
  BarElement,
  BarController,
  Title,
  Tooltip,
  Legend,
  type ChartConfiguration
} from 'chart.js'
import { calculateTilesAtZoom } from '@/utils'
import type { Tileset } from '@/services'

Chart.register(CategoryScale, LinearScale, BarElement, BarController, Title, Tooltip, Legend)

const props = defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

defineEmits<{
  'update:open': [value: boolean]
}>()

const { selectedDatasetId } = useSelectedData()
const { datasets } = useDatasetQuery(selectedDatasetId)
const { tilesets } = useTilesetQuery(selectedDatasetId)

const chartRef = ref<HTMLCanvasElement | null>(null)
let chartInstance: Chart | null = null

const selectedTilesetIds = ref<number[]>([])

const toggleTilesetSelection = (tilesetId: number) => {
  const index = selectedTilesetIds.value.indexOf(tilesetId)
  if (index > -1) {
    selectedTilesetIds.value.splice(index, 1)
  } else {
    selectedTilesetIds.value.push(tilesetId)
  }
}

const chartColors = [
  '#3b82f6',
  '#ef4444',
  '#10b981',
  '#f59e0b',
  '#8b5cf6',
  '#06b6d4',
  '#f97316',
  '#84cc16',
]

const availableTilesets = computed(() => {
  if (!datasets.value) return []

  const allTilesets: Array<Pick<Tileset, 'id' | 'name' | 'metadata'>> = []

  if (tilesets.value) {
    tilesets.value.forEach(tileset => {
      if (tileset.metadata) {
        allTilesets.push({
          id: tileset.id,
          name: tileset.name,
          metadata: tileset.metadata
        })
      }
    })
  }

  return allTilesets
})

const comparisonData = computed(() => {
  return selectedTilesetIds.value
    .map(id => availableTilesets.value.find(t => t.id === id))
    .filter((tileset): tileset is NonNullable<typeof tileset> => Boolean(tileset))
    .map(tileset => {
      const tilesPerZoom = calculateTilesPerZoom(tileset.metadata)
      const totalTiles = tilesPerZoom.reduce((sum, data) => sum + data.tiles, 0)

      return {
        id: tileset.id,
        name: tileset.name,
        tilesPerZoom,
        totalTiles
      }
    })
})

const chartData = computed(() => {
  if (comparisonData.value.length === 0) return null

  const allZoomLevels = new Set<number>()
  comparisonData.value.forEach(data => {
    if (data) {
      data.tilesPerZoom.forEach(zoom => allZoomLevels.add(zoom.zoom))
    }
  })

  const sortedZoomLevels = Array.from(allZoomLevels).sort((a, b) => a - b)

  const datasets = comparisonData.value
    .map((data, index) => {
      if (!data) return null

      const zoomData = sortedZoomLevels.map(zoom => {
        const found = data.tilesPerZoom.find(z => z.zoom === zoom)
        return found ? found.tiles : 0
      })

      return {
        label: data.name,
        data: zoomData,
        backgroundColor: chartColors[index % chartColors.length],
        borderColor: chartColors[index % chartColors.length],
        borderWidth: 1
      }
    })
    .filter((dataset): dataset is NonNullable<typeof dataset> => Boolean(dataset))

  return {
    labels: sortedZoomLevels.map(zoom => `Zoom ${zoom}`),
    datasets
  }
})

const chartConfig = computed<ChartConfiguration<'bar'>>(() => ({
  type: 'bar',
  data: chartData.value!,
  options: {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      title: {
        display: false,
      },
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const label = context.dataset.label || ''
            const value = context.parsed.y
            return `${label}: ${value.toLocaleString()} tiles`
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Zoom Level'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Number of Tiles'
        },
        ticks: {
          callback: (value) => {
            return typeof value === 'number' ? value.toLocaleString() : value
          }
        }
      }
    }
  }
}))

const calculateTilesPerZoom = (metadata: TileMetadataResponse) => {
  const result = []
  const [west, south, east, north] = metadata.header.bounds

  for (let zoom = metadata.header.min_zoom; zoom <= metadata.header.max_zoom; zoom++) {
    const tiles = calculateTilesAtZoom(west, south, east, north, zoom)
    result.push({ zoom, tiles })
  }

  return result
}

const createChart = () => {
  if (!chartRef.value || !chartData.value) return

  if (chartInstance) {
    chartInstance.destroy()
  }

  chartInstance = new Chart(chartRef.value, chartConfig.value)
}

const updateChart = () => {
  if (!chartInstance || !chartData.value) return

  chartInstance.data = chartData.value
  chartInstance.update()
}

watch(chartData, async () => {
  if (chartData.value) {
    await nextTick()
    if (chartInstance) {
      updateChart()
    } else {
      createChart()
    }
  } else if (!chartData.value && chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
}, { deep: true })


watch(() => props.open, async (newVal) => {
  if (newVal && chartData.value) {
    await nextTick()
    if (chartInstance) {
      updateChart()
    } else {
      createChart()
    }
  } else if (!newVal && chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

onMounted(() => {
  // Select first two tilesets by default for comparison
  if (availableTilesets.value.length > 0 && selectedTilesetIds.value.length === 0) {
    selectedTilesetIds.value = availableTilesets.value.slice(0, 2).map(t => t.id)
  }
})
</script>
