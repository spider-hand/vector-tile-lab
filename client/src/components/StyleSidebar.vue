<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)" title="Style Tileset"
    description="Manage and configure tileset styles">
    <div class="flex flex-col gap-4">
      <div v-if="!tileset" class="text-center py-4 text-sm text-muted-foreground">
        No tileset selected. Please select a tileset.
      </div>
      <div v-else class="flex flex-col gap-6">
        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Style by Attribute</h3>
          <div v-if="tierLists && tierLists.length > 0" class="flex flex-col gap-3">
            <div class="flex flex-col gap-2">
              <Select v-model="selectedAttributeField" @update:model-value="applySelectedAttribute">
                <SelectTrigger>
                  <SelectValue placeholder="Choose an attribute..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="tierList in tierLists" :key="tierList.id" :value="tierList.field">
                    {{ tierList.field }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div v-if="selectedAttributeField" class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Color Theme</label>
              <Select v-model="selectedColorTheme">
                <SelectTrigger>
                  <SelectValue placeholder="Choose a color theme..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="theme in COLOR_THEME_LIST" :key="theme.value" :value="theme.value">
                    {{ theme.label }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>
        <div class="flex flex-col gap-3">
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
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import BaseSidebar from './BaseSidebar.vue'
import { Switch } from '@/components/ui/switch'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useTierListQuery } from '@/composables/useTierListQuery'
import { useLayerStyles } from '@/composables/useLayerStyles'
import { watch, ref, computed } from 'vue'
import type { TierList } from '@/services/models'
import { LAYER_TYPES, COLOR_THEME_LIST } from '@/consts'

defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

defineEmits<{
  'update:open': [value: boolean]
}>()

const { selectedDatasetId, selectedTilesetId } = useSelectedData()
const { tileset } = useTilesetQuery(selectedDatasetId, selectedTilesetId)
const { tierLists } = useTierListQuery(selectedDatasetId, selectedTilesetId)
const { selectedColorTheme, setLayersFromMetadata, toggleLayerType, getLayerVisibility, clearLayers, applyTier, clearTier } = useLayerStyles()

const selectedAttributeField = ref<string>('')

const selectedTierList = computed((): TierList | undefined => {
  if (selectedAttributeField.value === '' || !tierLists.value) return undefined
  return tierLists.value.find(tl => tl.field === selectedAttributeField.value)
})

const applySelectedAttribute = () => {
  if (selectedTierList.value) {
    applyTier(
      selectedTierList.value.field,
      selectedTierList.value.breaks
    )
  } else {
    clearTier()
  }
}

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

// Apply the new color theme
watch(
  () => selectedColorTheme.value,
  () => {
    applySelectedAttribute()
  }
)

// Reset selected attribute and tier when dataset changes
watch(
  () => selectedDatasetId.value,
  () => {
    selectedAttributeField.value = ''
    clearTier()
  }
)
</script>
