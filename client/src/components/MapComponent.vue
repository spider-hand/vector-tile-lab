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
import { DEFFAULT_COLOR } from '@/consts';

const mapRef = ref<HTMLElement | null>(null);
const map = ref<maplibregl.Map | null>(null);

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

const { selectedDatasetId, selectedTilesetId } = useSelectedData();
const { presignedUrl, isFetchingPresignedUrl, tileset, isFetchingTileset } = useTilesetQuery(selectedDatasetId, selectedTilesetId);
const { layersVisibility, getLayerVisibility, tierStyleConfig, layerStyle } = useLayerStyles();

const initializeMap = () => {
  if (!mapRef.value || map.value) return;

  const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN;
  const tile = mapboxToken ? `https://api.mapbox.com/styles/v1/mapbox/light-v11/tiles/{z}/{x}/{y}?access_token=${mapboxToken}` : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
  const attribution = mapboxToken ? '© <a href="https://www.mapbox.com/about/maps/">Mapbox</a> © <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> <strong><a href="https://www.mapbox.com/map-feedback/" target="_blank">Improve this map</a></strong>' : '©<a href="https://www.openstreetmap.org/copyright/ja">OpenStreetMap</a> contributors';

  map.value = new maplibregl.Map({
    container: mapRef.value as HTMLElement,
    style: {
      version: 8,
      sources: {
        'raster-tiles': {
          type: 'raster',
          tiles: [
            tile,
          ],
          tileSize: 256,
          attribution: attribution,
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

  const [minLng, minLat, maxLng, maxLat] = header.bounds;

  map.value.fitBounds(
    [[minLng, minLat], [maxLng, maxLat]],
    {
      padding: 50,
      duration: 1500
    }
  );
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

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const createTierColorExpression = (field: string, breaks: number[], colors: string[]): any => {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const expression: any[] = ['case'];

  for (let i = 0; i < breaks.length; i++) {
    if (i === 0) {
      // First class: value <= breaks[0]
      expression.push(['<=', ['get', field], breaks[i]], colors[i]);
    } else {
      // Subsequent classes: breaks[i-1] < value <= breaks[i]
      expression.push(
        ['all', ['>', ['get', field], breaks[i - 1]], ['<=', ['get', field], breaks[i]]],
        colors[i]
      );
    }
  }

  // Add fallback color for values that don't match any condition (required for 'case' expression)
  expression.push(DEFFAULT_COLOR);

  return expression;
};

const addGenericLayer = (sourceLayer: string) => {
  if (!map.value) return;

  const styleConfig = tierStyleConfig.value;

  // Determine paint properties based on whether tier styling is active
  const getFillColor = () => {
    if (styleConfig) {
      return createTierColorExpression(styleConfig.field, styleConfig.breaks, styleConfig.colors);
    }
    return DEFFAULT_COLOR;
  };

  const getLineColor = () => {
    if (styleConfig) {
      return createTierColorExpression(styleConfig.field, styleConfig.breaks, styleConfig.colors);
    }
    return DEFFAULT_COLOR;
  };

  const getCircleColor = () => {
    if (styleConfig) {
      return createTierColorExpression(styleConfig.field, styleConfig.breaks, styleConfig.colors);
    }
    return DEFFAULT_COLOR;
  };

  map.value.addLayer({
    id: `${sourceLayer}-fill`,
    type: 'fill',
    source: 'pmtiles-source',
    'source-layer': sourceLayer,
    paint: {
      'fill-color': getFillColor(),
      'fill-opacity': layerStyle.value.fillOpacity
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
      'line-color': getLineColor(),
      'line-width': layerStyle.value.lineWidth,
      'line-opacity': layerStyle.value.lineOpacity
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
      'circle-color': getCircleColor(),
      'circle-radius': layerStyle.value.circleRadius,
      'circle-opacity': layerStyle.value.circleOpacity,
      'circle-stroke-color': layerStyle.value.circleStrokeColor === 'black' ? '#000000' : '#ffffff',
      'circle-stroke-width': layerStyle.value.circleStrokeWidth,
      'circle-stroke-opacity': layerStyle.value.circleStrokeOpacity,
    },
    layout: {
      visibility: getLayerVisibility(sourceLayer, 'circle') ? 'visible' : 'none'
    }
  });
};

const updateLayerStyles = () => {
  if (!map.value || !tileset.value?.metadata?.metadata?.vector_layers) return;

  const mapInstance = map.value;
  const styleConfig = tierStyleConfig.value;

  tileset.value.metadata.metadata.vector_layers.forEach((layer: VectorLayer) => {
    const sourceLayer = layer.id;

    const fillLayerId = `${sourceLayer}-fill`;
    const strokeLayerId = `${sourceLayer}-stroke`;
    const pointLayerId = `${sourceLayer}-point`;

    const colorExpression = styleConfig
      ? createTierColorExpression(styleConfig.field, styleConfig.breaks, styleConfig.colors)
      : DEFFAULT_COLOR;

    // Update fill layer
    if (mapInstance.getLayer(fillLayerId)) {
      mapInstance.setPaintProperty(fillLayerId, 'fill-color', colorExpression);
    }

    // Update stroke layer
    if (mapInstance.getLayer(strokeLayerId)) {
      mapInstance.setPaintProperty(strokeLayerId, 'line-color', colorExpression);
    }

    // Update point layer
    if (mapInstance.getLayer(pointLayerId)) {
      mapInstance.setPaintProperty(pointLayerId, 'circle-color', colorExpression);
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

const updateLayerPaintProperties = () => {
  if (!map.value || !tileset.value?.metadata?.metadata?.vector_layers) return;

  const mapInstance = map.value;

  tileset.value.metadata.metadata.vector_layers.forEach((layer: VectorLayer) => {
    const sourceLayer = layer.id;

    const fillLayerId = `${sourceLayer}-fill`;
    const strokeLayerId = `${sourceLayer}-stroke`;
    const pointLayerId = `${sourceLayer}-point`;

    if (mapInstance.getLayer(fillLayerId)) {
      mapInstance.setPaintProperty(fillLayerId, 'fill-opacity', layerStyle.value.fillOpacity);
    }

    if (mapInstance.getLayer(strokeLayerId)) {
      mapInstance.setPaintProperty(strokeLayerId, 'line-opacity', layerStyle.value.lineOpacity);
      mapInstance.setPaintProperty(strokeLayerId, 'line-width', layerStyle.value.lineWidth);
    }

    if (mapInstance.getLayer(pointLayerId)) {
      mapInstance.setPaintProperty(pointLayerId, 'circle-opacity', layerStyle.value.circleOpacity);
      mapInstance.setPaintProperty(pointLayerId, 'circle-radius', layerStyle.value.circleRadius);
      mapInstance.setPaintProperty(pointLayerId, 'circle-stroke-width', layerStyle.value.circleStrokeWidth);
      mapInstance.setPaintProperty(pointLayerId, 'circle-stroke-opacity', layerStyle.value.circleStrokeOpacity);
      mapInstance.setPaintProperty(pointLayerId, 'circle-stroke-color', layerStyle.value.circleStrokeColor === 'black' ? '#000000' : '#ffffff');
    }
  });
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

// Watch for tier style changes and update map layers accordingly
watch(
  () => tierStyleConfig.value,
  () => {
    updateLayerStyles();
  },
  { deep: true }
);

// Watch for layer style changes and update map layers accordingly
watch(
  () => layerStyle.value,
  () => {
    updateLayerPaintProperties();
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