<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)" title="Style Tileset"
    description="Manage and configure tileset styles">
    <div class="flex flex-col gap-4">
      <div v-if="!tileset" class="text-center py-8 text-sm text-muted-foreground">
        <div class="flex flex-col items-center gap-2">
          <div class="w-12 h-12 bg-gray-100 rounded-full flex items-center justify-center">
            <PackageSearch />
          </div>
          <p>No tileset available</p>
        </div>
      </div>
      <div v-else class="flex flex-col gap-6">
        <div class="flex flex-col gap-3">
          <h3 class="text-sm font-medium">Style by Attribute</h3>
          <div v-if="tierLists && tierLists.length > 0" class="flex flex-col gap-3">
            <div class="flex flex-col gap-2">
              <Select v-model="selectedAttributeField" @update:model-value="onAttributeFieldChange">
                <SelectTrigger>
                  <SelectValue placeholder="Choose an attribute..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="field in uniqueFields" :key="field" :value="field">
                    {{ field }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div v-if="selectedAttributeField" class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Classification Method</label>
              <Select v-model="selectedMethod" @update:model-value="applySelectedAttribute">
                <SelectTrigger>
                  <SelectValue placeholder="Choose a method..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem v-for="method in availableMethods" :key="method.value" :value="method.value">
                    {{ method.label }}
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div v-if="selectedAttributeField && selectedMethod" class="flex flex-col gap-2">
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
            <div v-if="selectedTierList" class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Legend</label>
              <div class="grid grid-cols-1 gap-2">
                <div v-for="(breakValue, index) in selectedTierList.breaks" :key="index"
                  class="flex items-center justify-between px-3 py-2 border rounded text-xs">
                  <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded" :style="{ backgroundColor: getTierColor(Number(index)) }"></div>
                    <span class="font-medium">Tier {{ Number(index) + 1 }}</span>
                  </div>
                  <span class="text-muted-foreground">
                    {{ getTierRange(Number(index)) }}
                  </span>
                </div>
              </div>
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
import { PackageSearch } from 'lucide-vue-next'
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
import { LAYER_TYPES, COLOR_THEME_LIST, CLASSIFICATION_METHOD_LIST, getTierColors } from '@/consts'

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
const selectedMethod = ref<string>('')

const uniqueFields = computed(() => {
  if (!tierLists.value) return []
  return Array.from(new Set(tierLists.value.map(tl => tl.field)))
})

const availableMethods = computed(() => {
  if (!selectedAttributeField.value || !tierLists.value) return []
  const methods = tierLists.value
    .filter(tl => tl.field === selectedAttributeField.value)
    .map(tl => tl.method)
  return CLASSIFICATION_METHOD_LIST.filter(m => methods.includes(m.value))
})

const selectedTierList = computed((): TierList | undefined => {
  if (selectedAttributeField.value === '' || selectedMethod.value === '' || !tierLists.value) return undefined
  return tierLists.value.find(tl => tl.field === selectedAttributeField.value && tl.method === selectedMethod.value)
})

const onAttributeFieldChange = () => {
  if (availableMethods.value.length > 0) {
    const defaultMethod = availableMethods.value.find(m => m.value === 'quantile')
    selectedMethod.value = defaultMethod ? defaultMethod.value : availableMethods.value[0].value
    applySelectedAttribute()
  } else {
    selectedMethod.value = ''
    clearTier()
  }
}

const applySelectedAttribute = () => {
  if (selectedTierList.value) {
    const classCount = selectedTierList.value.breaks.length
    const colors = getTierColors(selectedColorTheme.value, classCount)
    applyTier(
      selectedTierList.value.field,
      selectedTierList.value.breaks,
      colors
    )
  } else {
    clearTier()
  }
}

const getTierColor = (index: number): string => {
  if (!selectedTierList.value) return '#cccccc'
  const classCount = selectedTierList.value.breaks.length
  const themeColors = getTierColors(selectedColorTheme.value, classCount)
  return themeColors[index]
}

const getTierRange = (index: number): string => {
  if (!selectedTierList.value) return ''
  const breaks = selectedTierList.value.breaks

  if (index === 0) {
    // First tier: ≤ breaks[0]
    return `≤ ${breaks[0]}`
  } else {
    // Subsequent tiers: breaks[i-1] < value ≤ breaks[i]
    return `${breaks[index - 1]} - ${breaks[index]}`
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
    selectedMethod.value = ''
    clearTier()
  }
)
</script>
