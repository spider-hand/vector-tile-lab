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
import { useLayerStyles } from '@/composables/useLayerStyles';
import type { LayerType, TileHeader, TileMetadataResponse, VectorLayer } from '@/types';

const mapRef = ref<HTMLElement | null>(null);
const map = ref<maplibregl.Map | null>(null);

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

const { selectedDatasetId, selectedTilesetId } = useSelectedData();
const { presignedUrl, isFetchingPresignedUrl, tileset, isFetchingTileset } = useTilesetQuery(selectedDatasetId, selectedTilesetId);
const { layersVisibility, getLayerVisibility } = useLayerStyles();

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

const flyToTilesetBounds = (header: TileHeader) => {
  if (!map.value) return;

  const [centerLng, centerLat] = header.center;

  map.value.flyTo({
    center: [centerLng, centerLat],
    zoom: 3,
    duration: 1500,
    essential: true
  });
};

const addPmtilesLayer = (pmtilesUrl: string, tilesetMetadata: TileMetadataResponse) => {
  if (!map.value) return;

  removePmtilesLayer();

  mapTileMonitor.clear();

  map.value.addSource('pmtiles-source', {
    type: 'vector',
    url: `pmtiles://${pmtilesUrl}`,
  });

  if (tilesetMetadata.metadata.vector_layers) {
    tilesetMetadata.metadata.vector_layers.forEach((layer: VectorLayer) => {
      addGenericLayer(layer.id);
    });
  }

  // @ts-expect-error Type instantiation is excessively deep and possibly infinite.ts-plugin(2589)
  mapTileMonitor.setup(map.value, "pmtiles-source");

  flyToTilesetBounds(tilesetMetadata.header);
};

const addGenericLayer = (sourceLayer: string) => {
  if (!map.value) return;

  const color = "#3b82f6"; // blue-500

  map.value.addLayer({
    id: `${sourceLayer}-fill`,
    type: 'fill',
    source: 'pmtiles-source',
    'source-layer': sourceLayer,
    paint: {
      'fill-color': color,
      'fill-opacity': 0.6
    },
    layout: {
      visibility: getLayerVisibility(sourceLayer, 'fill') ? 'visible' : 'none'
    }
  });

  map.value.addLayer({
    id: `${sourceLayer}-stroke`,
    type: 'line',
    source: 'pmtiles-source',
    'source-layer': sourceLayer,
    paint: {
      'line-color': color,
      'line-width': 1,
      'line-opacity': 0.8
    },
    layout: {
      visibility: getLayerVisibility(sourceLayer, 'line') ? 'visible' : 'none'
    }
  });

  map.value.addLayer({
    id: `${sourceLayer}-point`,
    type: 'circle',
    source: 'pmtiles-source',
    'source-layer': sourceLayer,
    paint: {
      'circle-color': color,
      'circle-radius': 4,
      'circle-opacity': 0.8,
      'circle-stroke-color': '#ffffff',
      'circle-stroke-width': 1
    },
    layout: {
      visibility: getLayerVisibility(sourceLayer, 'circle') ? 'visible' : 'none'
    }
  });
};

const updateLayerVisibility = (sourceLayer: string, layerType: LayerType, visible: boolean) => {
  if (!map.value) return;

  const layerIdMap = {
    fill: `${sourceLayer}-fill`,
    line: `${sourceLayer}-stroke`,
    circle: `${sourceLayer}-point`
  };

  const layerId = layerIdMap[layerType];

  if (map.value.getLayer(layerId)) {
    map.value.setLayoutProperty(layerId, 'visibility', visible ? 'visible' : 'none');
  }
};

const removePmtilesLayer = () => {
  if (!map.value) return;

  const layers = map.value.getStyle().layers || [];
  layers.forEach((layer) => {
    if ('source' in layer && layer.source === 'pmtiles-source') {
      if (map.value?.getLayer(layer.id)) {
        map.value.removeLayer(layer.id);
      }
    }
  });

  if (map.value.getSource('pmtiles-source')) {
    map.value.removeSource('pmtiles-source');
  }
};

watch(
  [() => presignedUrl.value, () => tileset.value],
  ([newPresignedUrl, newTileset]) => {
    if (!map.value) {
      initializeMap();
    }

    if (newPresignedUrl?.presignedUrl && !isFetchingPresignedUrl.value && newTileset && !isFetchingTileset.value) {
      addPmtilesLayer(newPresignedUrl.presignedUrl, newTileset.metadata);
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

// Watch for layer visibility changes and update map layers accordingly
watch(
  () => layersVisibility.value,
  (newVisibility) => {
    Object.keys(newVisibility).forEach(sourceLayer => {
      const layerVisibility = newVisibility[sourceLayer];
      updateLayerVisibility(sourceLayer, 'fill', layerVisibility.fill);
      updateLayerVisibility(sourceLayer, 'line', layerVisibility.line);
      updateLayerVisibility(sourceLayer, 'circle', layerVisibility.circle);
    });
  },
  { deep: true }
);

onMounted(() => {
  initializeMap();

  if (presignedUrl.value?.presignedUrl && !isFetchingPresignedUrl.value && tileset.value && !isFetchingTileset.value) {
    addPmtilesLayer(presignedUrl.value.presignedUrl, tileset.value.metadata);
  }
})
</script>