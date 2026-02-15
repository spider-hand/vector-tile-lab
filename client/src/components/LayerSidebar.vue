<template>
  <BaseSidebar @close="$emit('close')" title="Layer">
    <div class="flex flex-col gap-4">
      <EmptyState v-if="!tileset" message="No tileset available" />
      <div v-else class="flex flex-col gap-6">
        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Visibility</h3>
          <div v-if="tileset.metadata?.metadata?.vector_layers && tileset.metadata.metadata.vector_layers.length > 0" class="flex flex-col gap-4">
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
            <div class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Opacity</label>
              <div class="flex items-center gap-3">
                <Slider
                  :model-value="[layerStyle.fillOpacity]"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  @update:model-value="(val) => layerStyle.fillOpacity = val?.[0] ?? 0.6"
                />
                <span class="text-xs w-8 text-right">{{ layerStyle.fillOpacity }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Line</h3>
          <div class="flex flex-col gap-4 p-4 border rounded-lg">
            <div class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Opacity</label>
              <div class="flex items-center gap-3">
                <Slider
                  :model-value="[layerStyle.lineOpacity]"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  @update:model-value="(val) => layerStyle.lineOpacity = val?.[0] ?? 0.8"
                />
                <span class="text-xs w-8 text-right">{{ layerStyle.lineOpacity }}</span>
              </div>
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Width</label>
              <div class="flex items-center gap-3">
                <Slider
                  :model-value="[layerStyle.lineWidth]"
                  :min="0.5"
                  :max="10"
                  :step="0.5"
                  @update:model-value="(val) => layerStyle.lineWidth = val?.[0] ?? 1"
                />
                <span class="text-xs w-8 text-right">{{ layerStyle.lineWidth }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Circle</h3>
          <div class="flex flex-col gap-4 p-4 border rounded-lg">
            <div class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Opacity</label>
              <div class="flex items-center gap-3">
                <Slider
                  :model-value="[layerStyle.circleOpacity]"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  @update:model-value="(val) => layerStyle.circleOpacity = val?.[0] ?? 0.8"
                />
                <span class="text-xs w-8 text-right">{{ layerStyle.circleOpacity }}</span>
              </div>
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Radius</label>
              <div class="flex items-center gap-3">
                <Slider
                  :model-value="[layerStyle.circleRadius]"
                  :min="1"
                  :max="20"
                  :step="1"
                  @update:model-value="(val) => layerStyle.circleRadius = val?.[0] ?? 4"
                />
                <span class="text-xs w-8 text-right">{{ layerStyle.circleRadius }}</span>
              </div>
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Stroke Width</label>
              <div class="flex items-center gap-3">
                <Slider
                  :model-value="[layerStyle.circleStrokeWidth]"
                  :min="0"
                  :max="5"
                  :step="0.5"
                  @update:model-value="(val) => layerStyle.circleStrokeWidth = val?.[0] ?? 1"
                />
                <span class="text-xs w-8 text-right">{{ layerStyle.circleStrokeWidth }}</span>
              </div>
            </div>

            <div class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Stroke Opacity</label>
              <div class="flex items-center gap-3">
                <Slider
                  :model-value="[layerStyle.circleStrokeOpacity]"
                  :min="0"
                  :max="1"
                  :step="0.1"
                  @update:model-value="(val) => layerStyle.circleStrokeOpacity = val?.[0] ?? 1"
                />
                <span class="text-xs w-8 text-right">{{ layerStyle.circleStrokeOpacity }}</span>
              </div>
            </div>

            <div class="flex items-center justify-between">
              <label class="text-xs font-medium text-muted-foreground">Stroke Color (Black / White)</label>
              <Switch
                :model-value="layerStyle.circleStrokeColor === 'black'"
                @update:model-value="layerStyle.circleStrokeColor = $event ? 'black' : 'white'"
              />
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
import { Switch } from '@/components/ui/switch'
import { Slider } from '@/components/ui/slider'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useLayerStyles } from '@/composables/useLayerStyles'
import { watch } from 'vue'
import { LAYER_TYPES } from '@/consts'

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
