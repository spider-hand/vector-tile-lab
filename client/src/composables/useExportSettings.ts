import { ref, computed } from 'vue'
import type { LegendSettings, ExportSettings } from '@/types'

const isPreviewMode = ref(false)
const isExporting = ref(false)
const exportHandler = ref<(() => Promise<void>) | null>(null)

const legendSettings = ref<LegendSettings>({
  title: 'Legend',
  fontFamily: 'Inter',
  fontSize: 12,
  titleFontWeight: '600',
  itemFontWeight: '400',
  position: 'bottom-right',
  padding: 16,
  visible: true,
})

const exportSettings = ref<ExportSettings>({
  aspectRatio: '16:9',
})

export const useExportSettings = () => {
  const aspectRatioValue = computed(() => {
    const [w, h] = exportSettings.value.aspectRatio.split(':').map(Number)
    return w / h
  })

  const setPreviewMode = (enabled: boolean) => {
    isPreviewMode.value = enabled
  }

  const updateLegendSettings = (settings: Partial<LegendSettings>) => {
    legendSettings.value = { ...legendSettings.value, ...settings }
  }

  const updateExportSettings = (settings: Partial<ExportSettings>) => {
    exportSettings.value = { ...exportSettings.value, ...settings }
  }

  const registerExportHandler = (handler: () => Promise<void>) => {
    exportHandler.value = handler
  }

  const triggerExport = async () => {
    if (!exportHandler.value || isExporting.value) return
    isExporting.value = true
    try {
      await exportHandler.value()
    } finally {
      isExporting.value = false
    }
  }

  const resetSettings = () => {
    legendSettings.value = {
      title: 'Legend',
      fontFamily: 'Inter',
      fontSize: 12,
      titleFontWeight: '600',
      itemFontWeight: '400',
      position: 'bottom-right',
      padding: 16,
      visible: true,
    }
    exportSettings.value = {
      aspectRatio: '16:9',
    }
  }

  return {
    isPreviewMode,
    isExporting,
    legendSettings,
    exportSettings,
    aspectRatioValue,
    setPreviewMode,
    updateLegendSettings,
    updateExportSettings,
    registerExportHandler,
    triggerExport,
    resetSettings,
  }
}
