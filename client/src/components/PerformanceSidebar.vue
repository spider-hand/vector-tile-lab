<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)"
               title="Performance Metrics" description="Tile loading performance statistics">
    <div class="flex-1">
      <div v-if="!selectedTilesetId" class="text-center py-8 text-sm text-muted-foreground">
        <div class="flex flex-col items-center gap-2">
          <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
            <PackageSearch />
          </div>
          <p>No tileset available</p>
        </div>
      </div>
      <div v-else class="flex flex-col gap-4">
        <div class="bg-blue-50 rounded-lg p-4">
          <h3 class="font-medium mb-3">Loading Times</h3>
          <div class="flex flex-col gap-3">
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground text-sm">Initial:</span>
              <span class="font-medium">{{ initialLoadTime }}ms</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground text-sm">Latest:</span>
              <span class="font-medium">{{ latestLoadTime }}ms</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground text-sm">Average:</span>
              <span class="font-medium">{{ averageLoadTime }}ms</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground text-sm">Minimum:</span>
              <span class="font-medium text-green-600">{{ minimumLoadTime }}ms</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground text-sm">Maximum:</span>
              <span class="font-medium text-red-600">{{ maximumLoadTime }}ms</span>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 rounded-lg p-4">
          <div class="flex justify-between items-center">
            <span class="text-muted-foreground text-sm">Total Requests:</span>
            <span class="font-medium">{{ totalRequests }}</span>
          </div>
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import BaseSidebar from './BaseSidebar.vue';
import { PackageSearch } from 'lucide-vue-next';
import { useSelectedData } from '@/composables/useSelectedData';
import { mapTileMonitor, type TileLoadMetrics, type TileLoadStats } from '@/utils/metrics';

defineProps({
  open: {
    type: Boolean,
    required: true
  }
});

defineEmits<{
  'update:open': [value: boolean]
}>();

const { selectedTilesetId } = useSelectedData();

const stats = ref<TileLoadStats>({
  initialLoadTime: 0,
  avgLoadTime: 0,
  maxLoadTime: 0,
  minLoadTime: 0,
  totalRequests: 0
});
const latestMetric = ref<TileLoadMetrics | null>(null);

const latestLoadTime = computed(() => {
  return latestMetric.value ? latestMetric.value.loadTime.toFixed(1) : '0.0';
});

const initialLoadTime = computed(() => {
  return stats.value?.initialLoadTime.toFixed(1);
});

const averageLoadTime = computed(() => {
  return stats.value?.avgLoadTime.toFixed(1);
});

const minimumLoadTime = computed(() => {
  return stats.value.totalRequests > 0 ? stats.value.minLoadTime.toFixed(1) : '0.0';
});

const maximumLoadTime = computed(() => {
  return stats.value.totalRequests > 0 ? stats.value.maxLoadTime.toFixed(1) : '0.0';
});

const totalRequests = computed(() => {
  return stats.value.totalRequests;
});

const updateStats = () => {
  stats.value = mapTileMonitor.stats;
  latestMetric.value = mapTileMonitor.latestMetric;
};

let refreshInterval: NodeJS.Timeout;

onMounted(() => {
  refreshInterval = setInterval(updateStats, 1000);
});

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval);
  }
});
</script>
