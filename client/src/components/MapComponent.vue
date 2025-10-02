<template>
  <div ref="mapRef" class="absolute! top-0 left-0 w-full h-full">
  </div>
</template>

<script setup lang="ts">
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { onMounted, ref, watch } from 'vue';
import { mapTileMonitor } from '@/utils';
import * as pmtiles from 'pmtiles';
import useTilesetQuery from '@/composables/useTilesetQuery';
import { useSelectedData } from '@/composables/useSelectedData';

const mapRef = ref<HTMLElement | null>(null);
const map = ref<maplibregl.Map | null>(null);

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

const { selectedDatasetId, selectedTilesetId } = useSelectedData();
const { presignedUrl, isFetchingPresignedUrl } = useTilesetQuery(selectedDatasetId, selectedTilesetId);

const initializeMap = () => {
  if (!mapRef.value || map.value) return;

  map.value = new maplibregl.Map({
    container: mapRef.value as HTMLElement,
    style: {
      version: 8,
      sources: {
        'raster-tiles': {
          type: 'raster',
          tiles: [
            'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          ],
          tileSize: 256,
          attribution: '©<a href="https://www.openstreetmap.org/copyright/ja">OpenStreetMap</a> contributors',
        }
      },
      layers: [{
        id: 'raster-tiles',
        type: 'raster',
        source: 'raster-tiles',
        minzoom: 0,
        maxzoom: 19,
      }]
    },
    center: [6.82, 50.06],
    zoom: 3,
  });
};

const addPmtilesLayer = (pmtilesUrl: string) => {
  if (!map.value) return;

  if (map.value.getLayer('lau-population-fill')) {
    map.value.removeLayer('lau-population-fill');
  }
  if (map.value.getSource('pmtiles-source')) {
    map.value.removeSource('pmtiles-source');
  }

  map.value.addSource('pmtiles-source', {
    type: 'vector',
    url: `pmtiles://${pmtilesUrl}`,
  });

  map.value.addLayer({
    id: 'lau-population-fill',
    type: 'fill',
    source: 'pmtiles-source',
    'source-layer': 'LAU_RG_01M_2024_4326',
    paint: {
      'fill-color': [
        'case',
        ['has', 'POP_2024'],
        [
          'interpolate',
          ['linear'],
          ['get', 'POP_2024'],
          0, '#ffffcc',
          1000, '#c7e9b4',
          5000, '#7fcdbb',
          10000, '#41b6c4',
          25000, '#2c7fb8',
          50000, '#253494',
          100000, '#081d58'
        ],
        '#dddddd'
      ],
      'fill-opacity': 0.7
    }
  });

  // @ts-expect-error Type instantiation is excessively deep and possibly infinite.ts-plugin(2589)
  mapTileMonitor.setup(map.value, "pmtiles-source");
};

const removePmtilesLayer = () => {
  if (!map.value) return;

  if (map.value.getLayer('lau-population-fill')) {
    map.value.removeLayer('lau-population-fill');
  }
  if (map.value.getSource('pmtiles-source')) {
    map.value.removeSource('pmtiles-source');
  }
};

watch(
  () => presignedUrl.value,
  (newPresignedUrl) => {
    if (!map.value) {
      initializeMap();
    }

    if (newPresignedUrl?.presignedUrl && !isFetchingPresignedUrl.value) {
      addPmtilesLayer(newPresignedUrl.presignedUrl);
    } else {
      removePmtilesLayer();
    }
  }
);


watch(
  [selectedDatasetId, selectedTilesetId],
  ([newDatasetId, newTilesetId]) => {
    if (!map.value) {
      initializeMap();
    }

    if (!newDatasetId || !newTilesetId) {
      removePmtilesLayer();
    }
  }
);

onMounted(() => {
  initializeMap();

  if (presignedUrl.value?.presignedUrl && !isFetchingPresignedUrl.value) {
    addPmtilesLayer(presignedUrl.value.presignedUrl);
  }
})
</script>