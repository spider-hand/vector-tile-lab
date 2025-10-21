<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)" title="Style Tileset"
    description="Manage and configure tileset styles">
    <div class="flex flex-col gap-4">
      <div v-if="!tileset" class="text-center py-4 text-sm text-muted-foreground">
        No tileset selected. Please select a tileset.
      </div>
      <div v-else class="flex flex-col gap-3">
        <h3 class="text-sm font-medium">Layer Visibility</h3>
        <div v-if="tileset.metadata?.metadata?.vector_layers && tileset.metadata.metadata.vector_layers.length > 0">
          <div v-for="layer in tileset.metadata.metadata.vector_layers" :key="layer.id"
            class="flex flex-col gap-4 p-4 border rounded-lg">
            <h4 class="text-sm font-medium">{{ layer.id }}</h4>
            <div v-for="type in LAYER_TYPES" :key="type" class="flex items-center justify-between">
              <label class="text-xs font-medium">{{ type.charAt(0).toUpperCase() + type.slice(1) }}</label>
              <Switch :model-value="getLayerVisibility(layer.id, type)"
                @update:model-value="toggleLayerType(layer.id, type, $event)" />
            </div>
          </div>
        </div>
        <div v-else class="text-center py-4 text-sm text-muted-foreground">
          No vector layers found in this tileset.
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import BaseSidebar from './BaseSidebar.vue'
import { Switch } from '@/components/ui/switch'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useLayerStyles } from '@/composables/useLayerStyles'
import { watch } from 'vue'
import type { LayerType } from '@/types'

defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

defineEmits<{
  'update:open': [value: boolean]
}>()

const LAYER_TYPES: LayerType[] = ['fill', 'line', 'circle']

const { selectedDatasetId, selectedTilesetId } = useSelectedData()
const { tileset } = useTilesetQuery(selectedDatasetId, selectedTilesetId)
const { setLayersFromMetadata, toggleLayerType, getLayerVisibility, clearLayers } = useLayerStyles()

// Initialize layer visibility when tileset changes
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
