<template>
  <BaseSidebar :open="open" @close="handleClose" title="Capture">
    <div class="flex flex-col gap-6">
      <div class="flex flex-col gap-3">
        <h3 class="text-sm font-medium">Preview</h3>
        <div class="flex flex-col gap-3 p-4 border rounded-lg">
          <LabeledSelect :model-value="exportSettings.aspectRatio"
            @update:model-value="updateExportSettings({ aspectRatio: $event as AspectRatio })" label="Aspect Ratio"
            placeholder="Select aspect ratio" :options="ASPECT_RATIO_OPTIONS" />
        </div>
      </div>

      <div class="flex flex-col gap-3">
        <div class="flex items-center justify-between">
          <h3 class="text-sm font-medium">Legend</h3>
          <Switch :model-value="legendSettings.visible"
            @update:model-value="updateLegendSettings({ visible: $event })" />
        </div>
        <div v-if="legendSettings.visible" class="flex flex-col gap-3 p-4 border rounded-lg">
          <LabeledSelect :model-value="legendSettings.position"
            @update:model-value="updateLegendSettings({ position: $event as LegendPosition })" label="Position"
            placeholder="Select position" :options="LEGEND_POSITION_OPTIONS" />

          <LabeledSlider :model-value="legendSettings.padding"
            @update:model-value="updateLegendSettings({ padding: $event })" label="Padding" :min="8" :max="48"
            :step="4" />

          <LabeledSelect :model-value="legendSettings.fontFamily"
            @update:model-value="updateLegendSettings({ fontFamily: $event as FontFamily })" label="Font Family"
            placeholder="Select font" :options="FONT_FAMILY_OPTIONS" />

          <LabeledSlider :model-value="legendSettings.fontSize"
            @update:model-value="updateLegendSettings({ fontSize: $event })" label="Font Size" :min="10" :max="20"
            :step="1" />

          <div class="flex flex-col gap-2">
            <label class="text-xs font-medium text-muted-foreground">Title</label>
            <Input :model-value="legendSettings.title"
              @update:model-value="updateLegendSettings({ title: $event as string })" placeholder="Legend title"
              class="h-8" />
          </div>

          <LabeledSelect :model-value="legendSettings.titleFontWeight"
            @update:model-value="updateLegendSettings({ titleFontWeight: $event as FontWeight })" label="Title Weight"
            placeholder="Select weight" :options="FONT_WEIGHT_OPTIONS" />

          <LabeledSelect :model-value="legendSettings.itemFontWeight"
            @update:model-value="updateLegendSettings({ itemFontWeight: $event as FontWeight })" label="Item Weight"
            placeholder="Select weight" :options="FONT_WEIGHT_OPTIONS" />
        </div>
      </div>

      <Button @click="triggerExport" :disabled="isExporting" class="h-8">
        <LoaderCircle v-if="isExporting" class="h-3 w-3 animate-spin mr-2" />
        {{ isExporting ? 'Exporting...' : 'Export' }}
      </Button>
    </div>
  </BaseSidebar>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import BaseSidebar from './BaseSidebar.vue'
import LabeledSelect from './LabeledSelect.vue'
import LabeledSlider from './LabeledSlider.vue'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Switch } from '@/components/ui/switch'
import { LoaderCircle } from 'lucide-vue-next'
import { useExportSettings } from '@/composables/useExportSettings'
import { ASPECT_RATIO_OPTIONS, FONT_FAMILY_OPTIONS, FONT_WEIGHT_OPTIONS, LEGEND_POSITION_OPTIONS } from '@/consts'
import type { AspectRatio, FontFamily, FontWeight, LegendPosition } from '@/types'

const props = defineProps<{
  open: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const {
  isExporting,
  legendSettings,
  exportSettings,
  setPreviewMode,
  updateLegendSettings,
  updateExportSettings,
  triggerExport,
} = useExportSettings()

watch(
  () => props.open,
  (isOpen) => {
    setPreviewMode(isOpen)
  },
  { immediate: true }
)

const handleClose = () => {
  setPreviewMode(false)
  emit('close')
}
</script>
