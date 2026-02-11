<template>
  <BaseSidebar @close="$emit('close')" title="Metadata">
    <div class="flex-1">
      <EmptyState v-if="!data" message="No tileset available" />
      <div v-else class="flex flex-col gap-4">
        <MetadataSectionCard title="Basic Information">
          <div class="flex flex-col gap-2 text-xs">
            <LabeledValue label="File Name" :value="filename" truncate />
            <LabeledValue label="Format" :value="data.metadata.format" />
            <LabeledValue label="Version" :value="data.metadata.version" />
            <LabeledValue label="Generator" :value="data.metadata.generator" />
            <LabeledValue v-if="data.metadata.generator_options" label="Generator Options"
              :value="data.metadata.generator_options" mono />
          </div>
        </MetadataSectionCard>

        <MetadataSectionCard title="Zoom & Tile Estimates">
          <div class="flex flex-col gap-2">
            <div class="grid grid-cols-2 text-xs">
              <LabeledValue label="Min Zoom" :value="data.header.min_zoom" />
              <LabeledValue label="Max Zoom" :value="data.header.max_zoom" />
            </div>
            <LabeledValue class="text-xs" label="Estimated Total Tiles" :value="estimatedTotalTiles.toLocaleString()" />
            <div class="flex flex-col gap-1 text-xs">
              <span class="text-muted-foreground">Tiles per Zoom Level:</span>
              <div class="flex flex-col gap-1">
                <div v-for="zoomData in tilesPerZoom" :key="zoomData.zoom" class="flex justify-between text-xs">
                  <span>Zoom {{ zoomData.zoom }}:</span>
                  <span class="font-medium">{{ zoomData.tiles.toLocaleString() }}</span>
                </div>
              </div>
            </div>
          </div>
        </MetadataSectionCard>

        <MetadataSectionCard title="Vector Layers">
          <div v-for="layer in data.metadata.vector_layers" :key="layer.id" class="flex flex-col gap-3">
            <div class="flex flex-col gap-2 text-xs">
              <LabeledValue label="ID" :value="layer.id" truncate />
              <LabeledValue label="Geometry" :value="getLayerGeometry(layer.id)" />
              <LabeledValue label="Features" :value="getLayerFeatureCount(layer.id).toLocaleString()" />
            </div>
            <div class="flex flex-col gap-1 text-xs">
              <span class="text-muted-foreground">Fields ({{ Object.keys(layer.fields ?? {}).length }}):</span>
              <div class="flex flex-wrap gap-2 rounded">
                <span v-for="(type, field) in layer.fields" :key="field" class="inline-block rounded text-xs">
                  {{ field }} <span>({{ type }})</span>
                </span>
              </div>
            </div>
          </div>
        </MetadataSectionCard>

        <MetadataSectionCard v-if="dataStats.length > 0" title="Data Statistics">
          <div class="flex flex-col">
            <div v-for="stat in dataStats" :key="stat.field" class="flex flex-col gap-1 border-b py-2 last:border-0">
              <h4 class="text-sm font-medium">{{ stat.field }}</h4>
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
        </MetadataSectionCard>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import BaseSidebar from './BaseSidebar.vue';
import MetadataSectionCard from './MetadataSectionCard.vue';
import LabeledValue from './LabeledValue.vue';
import EmptyState from './EmptyState.vue'
import useTilesetQuery from '@/composables/useTilesetQuery';
import { useSelectedData } from '@/composables/useSelectedData';
import type { DataStat, TileMetadataResponse } from '@/types';
import { calculateTilesAtZoom } from '@/utils';

defineEmits<{
  close: []
}>()

const { selectedDatasetId, selectedTilesetId } = useSelectedData();
const { tileset } = useTilesetQuery(selectedDatasetId, selectedTilesetId);
const data = computed(() => tileset.value?.metadata as TileMetadataResponse | null);

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

const getLayerGeometry = (layerId: string) => {
  const layer = data.value?.metadata?.tilestats?.layers?.find(l => l.layer === layerId);
  return layer?.geometry ?? 'Unknown';
};

const getLayerFeatureCount = (layerId: string) => {
  const layer = data.value?.metadata?.tilestats?.layers?.find(l => l.layer === layerId);
  return layer?.count ?? 0;
};


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
