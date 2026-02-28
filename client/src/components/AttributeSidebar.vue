<template>
  <BaseSidebar :open="open" @close="$emit('close')" title="Attribute">
    <div class="flex flex-col gap-4">
      <EmptyState v-if="!tileset" message="No tileset available" />
      <div v-else class="flex flex-col gap-6">
        <div class="flex flex-col gap-3">
          <div v-if="tierLists && tierLists.length > 0" class="flex flex-col gap-3">
            <LabeledSelect v-model="selectedAttributeField" label="Attribute" placeholder="Choose an attribute..."
              :options="attributeFieldOptions" @update:model-value="onAttributeFieldChange" />
            <LabeledSelect v-if="selectedAttributeField" v-model="selectedMethod" label="Classification Method"
              placeholder="Choose a method..." :options="availableMethods"
              @update:model-value="applySelectedAttribute" />
            <LabeledSelect v-if="selectedAttributeField && selectedMethod" v-model="selectedColorTheme"
              label="Color Theme" placeholder="Choose a color theme..." :options="COLOR_THEME_LIST" />
            <div v-if="selectedTierList" class="flex flex-col gap-2">
              <label class="text-xs font-medium text-muted-foreground">Legend</label>
              <div class="grid grid-cols-1 gap-2">
                <div v-for="(breakValue, index) in selectedTierList.breaks" :key="index"
                  class="flex items-center justify-between px-3 py-2 border rounded text-xs">
                  <div class="flex items-center gap-2">
                    <div class="w-3 h-3 rounded" :style="{ backgroundColor: getTierColor(Number(index)) }"></div>
                  </div>
                  <span class="text-muted-foreground">
                    {{ getTierRange(Number(index)) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import BaseSidebar from './BaseSidebar.vue'
import LabeledSelect from './LabeledSelect.vue'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'
import { useTierListQuery } from '@/composables/useTierListQuery'
import { useLayerStyles } from '@/composables/useLayerStyles'
import { watch, ref, computed } from 'vue'
import type { TierList } from '@/services/models'
import { COLOR_THEME_LIST, CLASSIFICATION_METHOD_LIST, getTierColors } from '@/consts'
import EmptyState from './EmptyState.vue'

defineProps<{
  open: boolean
}>()

defineEmits<{
  close: []
}>()

const { selectedDatasetId, selectedTilesetId } = useSelectedData()
const { tileset } = useTilesetQuery(selectedDatasetId, selectedTilesetId)
const { tierLists } = useTierListQuery(selectedDatasetId, selectedTilesetId)
const { selectedColorTheme, applyTier, clearTier } = useLayerStyles()

const selectedAttributeField = ref<string>('')
const selectedMethod = ref<string>('')

const uniqueFields = computed(() => {
  if (!tierLists.value) return []
  return Array.from(new Set(tierLists.value.map(tl => tl.field)))
})

const attributeFieldOptions = computed(() => {
  return uniqueFields.value.map(field => ({ value: field, label: field }))
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
