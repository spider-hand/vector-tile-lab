<template>
  <div ref="mapRef" class="absolute! top-0 left-0 w-full h-full">
  </div>
</template>

<script setup lang="ts">
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { onMounted, ref } from 'vue';
import { mapTileMonitor } from '@/utils';
import * as pmtiles from 'pmtiles';
import { TilesetsApi } from '@/services/apis/TilesetsApi';
import useApi from '@/composables/useApi';

const mapRef = ref<HTMLElement | null>(null);
const map = ref<maplibregl.Map | null>(null);

const protocol = new pmtiles.Protocol();
maplibregl.addProtocol('pmtiles', protocol.tile);

const { apiConfig } = useApi();
const tilesetsApi = new TilesetsApi(apiConfig);

onMounted(async () => {
  try {
    const response = await tilesetsApi.retrieveTilesetsPresignedUrl({ id: 1 });
    const pmtilesUrl = response.presignedUrl;

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
          },
          'pmtiles-source': {
            type: 'vector',
            url: `pmtiles://${pmtilesUrl}`,
          }
        },
        layers: [{
          id: 'raster-tiles',
          type: 'raster',
          source: 'raster-tiles',
          minzoom: 0,
          maxzoom: 19,
        }, {
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
        }]
      },
      center: [6.82, 50.06],
      zoom: 3,
    });

    // @ts-expect-error Type instantiation is excessively deep and possibly infinite.ts-plugin(2589)
    mapTileMonitor.setup(map.value, "pmtiles-source");
  } catch (error) {
    console.error('Failed to load PMTiles:', error);
  }
})
</script>