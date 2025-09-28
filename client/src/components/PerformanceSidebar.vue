<template>
  <Sheet :open="open" @update:open="(value: boolean) => $emit('update:open', value)" :modal="false">
    <SheetContent side="left" class="w-80 flex flex-col" :style="{ marginLeft: sidebarMargin }"
      @interact-outside="(e) => e.preventDefault()">
      <SheetHeader>
        <SheetTitle>Performance Metrics</SheetTitle>
        <SheetDescription>
          Tile loading performance statistics
        </SheetDescription>
      </SheetHeader>
      <div class="flex flex-col flex-1 min-h-0 rounded-lg px-4 pb-4 overflow-y-auto">
        <div class="flex-1">
          <div class="bg-blue-50 rounded-lg p-4">
            <h3 class="font-medium mb-3">Loading Times</h3>
            <div class="flex flex-col gap-3">
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
          <div class="mt-4 bg-gray-50 rounded-lg p-4">
            <div class="flex justify-between items-center">
              <span class="text-muted-foreground text-sm">Total Requests:</span>
              <span class="font-medium">{{ totalRequests }}</span>
            </div>
          </div>
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useSidebar } from '@/components/ui/sidebar/utils';
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet';
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

const { open: sidebarOpen, isMobile } = useSidebar();

const sidebarMargin = computed(() => {
  if (isMobile.value) {
    return '0';
  }
  return sidebarOpen.value ? '10rem' : '0';
});

const stats = ref<TileLoadStats>({
  avgLoadTime: 0,
  maxLoadTime: 0,
  minLoadTime: 0,
  totalRequests: 0
});
const latestMetric = ref<TileLoadMetrics | null>(null);

const latestLoadTime = computed(() => {
  return latestMetric.value ? latestMetric.value.loadTime.toFixed(1) : '0.0';
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
