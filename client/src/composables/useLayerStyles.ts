import { ref } from 'vue'
import type { LayerType, LayerVisibilityState, VectorLayer } from '@/types'
import { type ColorPaletteType } from '@/consts'

export interface TierStyleConfig {
  field: string
  breaks: number[]
  colors: string[]
}

export interface LayerStyleConfig {
  fillOpacity: number
  lineOpacity: number
  lineWidth: number
  circleOpacity: number
  circleRadius: number
  circleStrokeWidth: number
  circleStrokeOpacity: number
  circleStrokeColor: 'white' | 'black'
}

const layersVisibility = ref<LayerVisibilityState>({})
const selectedColorTheme = ref<ColorPaletteType>('chartjs')
const tierStyleConfig = ref<TierStyleConfig | null>(null)
const layerStyle = ref<LayerStyleConfig>({
  fillOpacity: 0.6,
  lineOpacity: 0.8,
  lineWidth: 1,
  circleOpacity: 0.8,
  circleRadius: 4,
  circleStrokeWidth: 0.2,
  circleStrokeOpacity: 0.4,
  circleStrokeColor: 'white',
})

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

  const applyTier = (field: string, breaks: number[], colors: string[]) => {
    tierStyleConfig.value = {
      field,
      breaks,
      colors: colors.slice(0, breaks.length),
    }
  }

  const clearTier = () => {
    tierStyleConfig.value = null
  }

  return {
    layersVisibility,
    tierStyleConfig,
    selectedColorTheme,
    layerStyle,
    setLayersFromMetadata,
    toggleLayerType,
    getLayerVisibility,
    clearLayers,
    applyTier,
    clearTier,
  }
}
