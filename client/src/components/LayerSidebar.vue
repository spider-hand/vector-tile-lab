<template>
  <BaseSidebar :open="open" @close="$emit('close')" title="Layer">
    <div class="flex flex-col gap-4">
      <EmptyState v-if="!tileset" message="No tileset available" />
      <div v-else class="flex flex-col gap-6">
        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Visibility</h3>
          <div v-if="tileset.metadata?.metadata?.vector_layers && tileset.metadata.metadata.vector_layers.length > 0"
            class="flex flex-col gap-4">
            <div v-for="layer in tileset.metadata.metadata.vector_layers" :key="layer.id"
              class="flex flex-col gap-3 p-3 border rounded-lg">
              <h4 class="text-sm font-medium">{{ layer.id }}</h4>
              <div v-for="type in LAYER_TYPES" :key="type" class="flex items-center justify-between">
                <label class="text-xs font-medium">{{ type.charAt(0).toUpperCase() + type.slice(1) }}</label>
                <Switch :model-value="getLayerVisibility(layer.id, type)"
                  @update:model-value="toggleLayerType(layer.id, type, $event)" />
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Fill</h3>
          <div class="flex flex-col gap-4 p-4 border rounded-lg">
            <LabeledSlider v-model="layerStyle.fillOpacity" label="Opacity" :min="0" :max="1" :step="0.1" />
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Line</h3>
          <div class="flex flex-col gap-4 p-4 border rounded-lg">
            <LabeledSlider v-model="layerStyle.lineOpacity" label="Opacity" :min="0" :max="1" :step="0.1" />

            <LabeledSlider v-model="layerStyle.lineWidth" label="Width" :min="0.5" :max="10" :step="0.5" />
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Circle</h3>
          <div class="flex flex-col gap-4 p-4 border rounded-lg">
            <LabeledSlider v-model="layerStyle.circleOpacity" label="Opacity" :min="0" :max="1" :step="0.1" />

            <LabeledSlider v-model="layerStyle.circleRadius" label="Radius" :min="1" :max="20" :step="1" />

            <LabeledSlider v-model="layerStyle.circleStrokeWidth" label="Stroke Width" :min="0" :max="5" :step="0.5" />

            <LabeledSlider v-model="layerStyle.circleStrokeOpacity" label="Stroke Opacity" :min="0" :max="1"
              :step="0.1" />

            <div class="flex items-center justify-between">
              <label class="text-xs font-medium text-muted-foreground">Stroke Color (Black / White)</label>
              <Switch :model-value="layerStyle.circleStrokeColor === 'black'"
                @update:model-value="layerStyle.circleStrokeColor = $event ? 'black' : 'white'" />
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import BaseSidebar from './BaseSidebar.vue'
import EmptyState from './EmptyState.vue'
import LabeledSlider from './LabeledSlider.vue'
import { Switch } from '@/components/ui/switch'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useLayerStyles } from '@/composables/useLayerStyles'
import { watch } from 'vue'
import type { LayerType } from '@/types'

const LAYER_TYPES: LayerType[] = ['fill', 'line', 'circle']


defineProps<{
  open: boolean
}>()

defineEmits<{
  close: []
}>()

const { selectedDatasetId, selectedTilesetId } = useSelectedData()
const { tileset } = useTilesetQuery(selectedDatasetId, selectedTilesetId)
const { layerStyle, setLayersFromMetadata, toggleLayerType, getLayerVisibility, clearLayers } = useLayerStyles()

watch(
  () => tileset.value,
  (newTileset) => {
    if (newTileset?.metadata?.metadata?.vector_layers) {
      setLayersFromMetadata(newTileset.metadata.metadata.vector_layers)
    } else {
      clearLayers()
    }
  },
  { immediate: true }
)
</script>
