import { ref } from 'vue'
import type { LayerType, LayerVisibilityState, VectorLayer } from '@/types'

const layersVisibility = ref<LayerVisibilityState>({})

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

  return {
    layersVisibility,
    setLayersFromMetadata,
    toggleLayerType,
    getLayerVisibility,
    clearLayers,
  }
}
