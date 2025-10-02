import { ref } from 'vue'

const selectedDatasetId = ref<number | null>(null)
const selectedTilesetId = ref<number | null>(null)

export const useSelectedData = () => {
  const setSelectedDataset = (id: number | null) => {
    selectedDatasetId.value = id
    selectedTilesetId.value = null
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
