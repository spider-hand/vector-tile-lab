<template>
  <Sheet :open="open" @update:open="(value: boolean) => $emit('update:open', value)" :modal="false">
    <SheetContent side="left" class="w-80 flex flex-col" :style="{ marginLeft: sidebarMargin }"
      @interact-outside="(e) => e.preventDefault()">
      <SheetHeader>
        <SheetTitle>Metadata</SheetTitle>
        <SheetDescription>
          Analysis of PMTiles
        </SheetDescription>
      </SheetHeader>
      <div class="flex flex-col flex-1 min-h-0 rounded-lg px-4 pb-4 overflow-y-auto">
        <div class="flex-1 overflow-y-auto">
          <div v-if="data" class="flex flex-col gap-4">
            <div class="bg-gray-50 rounded-lg p-4">
              <h3 class="font-medium mb-3">Basic Information</h3>
              <div class="flex flex-col gap-2 text-xs">
                <div>
                  <span class="text-muted-foreground">File Name:</span>
                  <p class="font-medium truncate">{{ filename }}</p>
                </div>
                <div>
                  <span class="text-muted-foreground">Format:</span>
                  <p class="font-medium">{{ data.metadata.format?.toUpperCase() ?? 'PMTiles' }}</p>
                </div>
                <div>
                  <span class="text-muted-foreground">Version:</span>
                  <p class="font-medium">{{ data.metadata.version ?? 'N/A' }}</p>
                </div>
                <div>
                  <span class="text-muted-foreground">Generator:</span>
                  <p class="font-medium">{{ data.metadata.generator ?? 'N/A' }}</p>
                </div>
              </div>
            </div>
            <div class="bg-blue-50 rounded-lg p-4">
              <h3 class="font-medium mb-3">Zoom Levels & Tile Estimates</h3>
              <div class="flex flex-col gap-2">
                <div class="grid grid-cols-2 text-xs">
                  <div>
                    <span class="text-muted-foreground">Min Zoom:</span>
                    <p class="font-medium">{{ data.header.min_zoom }}</p>
                  </div>
                  <div>
                    <span class="text-muted-foreground">Max Zoom:</span>
                    <p class="font-medium">{{ data.header.max_zoom }}</p>
                  </div>
                </div>
                <div>
                  <span class="text-muted-foreground text-xs">Estimated Total Tiles:</span>
                  <p class="text-lg font-bold text-blue-700">{{ estimatedTotalTiles.toLocaleString() }}</p>
                </div>
                <div class="flex flex-col gap-1">
                  <span class="text-muted-foreground text-xs">Tiles per Zoom Level:</span>
                  <div class="flex flex-col gap-1">
                    <div v-for="zoomData in tilesPerZoom" :key="zoomData.zoom" class="flex justify-between text-xs">
                      <span>Zoom {{ zoomData.zoom }}:</span>
                      <span class="font-medium">{{ zoomData.tiles.toLocaleString() }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-purple-50 rounded-lg p-4">
              <h3 class="font-medium mb-3">Vector Layers</h3>
              <div v-for="layer in data.metadata.vector_layers" :key="layer.id" class="flex flex-col gap-3">
                <div class="flex flex-col gap-2 text-xs">
                  <div>
                    <span class="text-muted-foreground">ID:</span>
                    <p class="font-medium truncate">{{ layer.id }}</p>
                  </div>
                  <div>
                    <span class="text-muted-foreground">Geometry:</span>
                    <p class="font-medium">{{ getLayerGeometry(layer.id) }}</p>
                  </div>
                  <div>
                    <span class="text-muted-foreground">Features:</span>
                    <p class="font-medium">{{ getLayerFeatureCount(layer.id).toLocaleString() }}</p>
                  </div>
                </div>
                <div class="flex flex-col">
                  <span class="text-muted-foreground text-xs">Fields ({{ Object.keys(layer.fields ?? {}).length
                  }}):</span>
                  <div class="flex flex-wrap gap-1">
                    <span v-for="(type, field) in layer.fields" :key="field"
                      class="inline-block bg-purple-100 text-purple-900 rounded text-xs p-1">
                      {{ field }} <span class="text-purple-700">({{ type }})</span>
                    </span>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="data.metadata.generator_options || data.metadata.strategies" class="bg-yellow-50 rounded-lg p-4">
              <h3 class="font-medium mb-3">Generation Details</h3>
              <div class="flex flex-col gap-3">
                <div v-if="data.metadata.generator_options" class="flex flex-col">
                  <span class="text-muted-foreground text-xs">Generator Options:</span>
                  <p class="text-xs font-mono bg-white rounded border break-all p-1">
                    {{ data.metadata.generator_options }}
                  </p>
                </div>
                <div v-if="data.metadata.strategies && data.metadata.strategies.length > 0" class="flex flex-col">
                  <span class="text-xs text-muted-foreground">Optimization Strategies:</span>
                  <div class="max-h-32 overflow-y-auto">
                    <div v-for="(strategy, index) in data.metadata.strategies" :key="index"
                      class="text-xs bg-white rounded border p-1 flex flex-col gap-1">
                      <span class="font-medium">Zoom {{ index }}:</span>
                      <span v-if="strategy.detail_reduced">
                        Detail reduced: {{ strategy.detail_reduced }}x
                      </span>
                      <span v-if="strategy.tiny_polygons">
                        Tiny polygons: {{ strategy.tiny_polygons.toLocaleString() }}
                      </span>
                      <span v-if="strategy.tile_size_desired">
                        Target size: {{ (strategy.tile_size_desired / 1024).toFixed(1) }}KB
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="dataStats.length > 0" class="bg-orange-50 rounded-lg p-4">
              <h3 class="font-medium mb-3">Data Statistics</h3>
              <div class="flex flex-col">
                <div v-for="stat in dataStats" :key="stat.field" class="border-b border-orange-200 py-2 last:border-0">
                  <h4 class="text-sm font-medium text-orange-900 mb-1">{{ stat.field }}</h4>
                  <div class="grid grid-cols-2 gap-1 text-xs">
                    <div>
                      <span class="text-muted-foreground">Type:</span>
                      <span class="font-medium">{{ stat.type }}</span>
                    </div>
                    <div>
                      <span class="text-muted-foreground">Count:</span>
                      <span class="font-medium">{{ stat.count.toLocaleString() }}</span>
                    </div>
                    <div v-if="stat.min !== undefined">
                      <span class="text-muted-foreground">Min:</span>
                      <span class="font-medium">{{ stat.min }}</span>
                    </div>
                    <div v-if="stat.max !== undefined">
                      <span class="text-muted-foreground">Max:</span>
                      <span class="font-medium">{{ stat.max }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useSidebar } from '@/components/ui/sidebar/utils';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet';
import useApi from '@/composables/useApi';
import { TilesetsApi } from '@/services';

interface TileMetadataResponse {
  header: TileHeader;
  metadata: TileMetadata;
}

interface TileHeader {
  min_zoom: number;
  max_zoom: number;
  bounds: [number, number, number, number];
  center: [number, number, number];
}

interface TileMetadata {
  vector_layers: VectorLayer[];
  description: string;
  name: string;
  version: string;
  format: string;
  generator: string;
  generator_options: string;
  strategies: Strategy[];
  tilestats: TileStats;
  [key: string]: unknown;
}

interface VectorLayer {
  id: string;
  fields: { [key: string]: string };
  description: string;
  maxzoom: number;
  minzoom: number;
}

interface Strategy {
  detail_reduced?: number;
  tile_size_desired?: number;
  tiny_polygons?: number;
}

interface TileStats {
  layerCount: number;
  layers: LayerStat[];
}

interface LayerStat {
  attributeCount: number;
  attributes: AttributeStats[];
  count: number;
  geometry: string;
  layer: string;
}

interface AttributeStats {
  attribute: string;
  count: number;
  max?: number;
  min?: number;
  type: string;
  values: (string | number | boolean)[];
}

interface DataStat {
  field: string;
  type: string;
  count: number;
  min?: number;
  max?: number;
}

defineProps({
  open: {
    type: Boolean,
    required: true
  }
});

defineEmits<{
  'update:open': [value: boolean]
}>()

const { open: sidebarOpen, isMobile } = useSidebar()

const sidebarMargin = computed(() => {
  if (isMobile.value) {
    return '0'
  }
  return sidebarOpen.value ? '10rem' : '0'
})

const { apiConfig } = useApi();
const tilesetsApi = new TilesetsApi(apiConfig);

const data = ref<TileMetadataResponse | null>(null);

const filename = computed(() => {
  if (!data.value?.metadata.name) return 'Unknown';
  return data.value.metadata.name.replace('/tmp/', '').replace('.pmtiles', '');
});

const tilesPerZoom = computed(() => {
  if (!data.value) return [];

  const result = [];
  const [west, south, east, north] = data.value.header.bounds;

  for (let zoom = data.value.header.min_zoom; zoom <= data.value.header.max_zoom; zoom++) {
    const tiles = calculateTilesAtZoom(west, south, east, north, zoom);
    result.push({ zoom, tiles });
  }

  return result;
});

const estimatedTotalTiles = computed(() => {
  return tilesPerZoom.value.reduce((total, zoomData) => total + zoomData.tiles, 0);
});

const dataStats = computed(() => {
  if (!data.value?.metadata?.tilestats?.layers) return [];

  const stats: DataStat[] = [];
  data.value.metadata.tilestats.layers.forEach(layer => {
    if (layer.attributes) {
      layer.attributes.forEach(attr => {
        stats.push({
          field: attr.attribute,
          type: attr.type,
          count: attr.count,
          min: attr.min,
          max: attr.max
        });
      });
    }
  });

  return stats;
});

const deg2num = (lat: number, lon: number, zoom: number) => {
  const latRad = lat * Math.PI / 180;
  const n = Math.pow(2, zoom);
  const x = Math.floor((lon + 180) / 360 * n);
  const y = Math.floor((1 - Math.asinh(Math.tan(latRad)) / Math.PI) / 2 * n);
  return { x, y };
};

const calculateTilesAtZoom = (west: number, south: number, east: number, north: number, zoom: number) => {
  const minTile = deg2num(south, west, zoom);
  const maxTile = deg2num(north, east, zoom);

  const tilesX = Math.abs(maxTile.x - minTile.x) + 1;
  const tilesY = Math.abs(maxTile.y - minTile.y) + 1;

  return tilesX * tilesY;
};

const getLayerGeometry = (layerId: string) => {
  const layer = data.value?.metadata?.tilestats?.layers?.find(l => l.layer === layerId);
  return layer?.geometry ?? 'Unknown';
};

const getLayerFeatureCount = (layerId: string) => {
  const layer = data.value?.metadata?.tilestats?.layers?.find(l => l.layer === layerId);
  return layer?.count ?? 0;
};

const fetchMetadata = async () => {
  try {
    const response = await tilesetsApi.retrieveTilesets({ id: 1 })
    data.value = response.metadata as TileMetadataResponse;
  } catch (error) {
    console.error('Error fetching metadata:', error);
  }
};

onMounted(() => {
  fetchMetadata();
});
</script>

<style scoped>
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
