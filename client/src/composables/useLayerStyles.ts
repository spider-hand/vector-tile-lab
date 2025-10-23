import { ref } from 'vue'
import type { LayerType, LayerVisibilityState, VectorLayer } from '@/types'
import { TIER_COLORS } from '@/consts'

export interface TierStyleConfig {
  field: string
  breaks: number[]
  colors: string[]
}

const layersVisibility = ref<LayerVisibilityState>({})
const tierStyleConfig = ref<TierStyleConfig | null>(null)

export const useLayerStyles = () => {
  const setLayersFromMetadata = (layers: VectorLayer[]) => {
    const newVisibility: LayerVisibilityState = {}

    for (const layer of layers) {
      newVisibility[layer.id] = {
        fill: true,
        line: true,
        circle: true,
      }
    }

    layersVisibility.value = newVisibility
  }

  const toggleLayerType = (layerId: string, type: LayerType, visible: boolean) => {
    if (layersVisibility.value[layerId]) {
      layersVisibility.value[layerId][type] = visible
    }
  }

  const getLayerVisibility = (layerId: string, type: LayerType): boolean => {
    return layersVisibility.value[layerId]?.[type] ?? true
  }

  const clearLayers = () => {
    layersVisibility.value = {}
  }

  const applyTier = (field: string, breaks: number[]) => {
    tierStyleConfig.value = {
      field,
      breaks,
      colors: TIER_COLORS.slice(0, breaks.length + 1),
    }
  }

  const clearTier = () => {
    tierStyleConfig.value = null
  }

  return {
    layersVisibility,
    tierStyleConfig,
    setLayersFromMetadata,
    toggleLayerType,
    getLayerVisibility,
    clearLayers,
    applyTier,
    clearTier,
  }
}
