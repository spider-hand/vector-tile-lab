import { ref } from 'vue'
import { useLayerStyles } from './useLayerStyles'

const selectedDatasetId = ref<number | null>(null)
const selectedTilesetId = ref<number | null>(null)

export const useSelectedData = () => {
  const { clearTier } = useLayerStyles()

  const setSelectedDataset = (id: number | null) => {
    selectedDatasetId.value = id
    selectedTilesetId.value = null
    clearTier();
  }

  const setSelectedTileset = (id: number | null) => {
    selectedTilesetId.value = id
  }

  return {
    selectedDatasetId,
    selectedTilesetId,
    setSelectedDataset,
    setSelectedTileset,
  }
}
