import { ref } from 'vue'

const selectedDatasetId = ref<number | null>(null)
const selectedDatasetName = ref<string | null>(null)
const selectedTilesetId = ref<number | null>(null)

export const useSelectedData = () => {
  const setSelectedDataset = (id: number | null, name?: string | null) => {
    selectedDatasetId.value = id
    selectedDatasetName.value = name ?? null
    selectedTilesetId.value = null
  }

  const setSelectedTileset = (id: number | null) => {
    selectedTilesetId.value = id
  }

  return {
    selectedDatasetId,
    selectedDatasetName,
    selectedTilesetId,
    setSelectedDataset,
    setSelectedTileset,
  }
}
