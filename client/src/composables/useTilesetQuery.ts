import { useQuery } from '@tanstack/vue-query'
import { DatasetsApi } from '@/services/apis/DatasetsApi'
import useApi from './useApi'
import { toValue, type MaybeRefOrGetter } from 'vue'

export const useTilesetQuery = (
  datasetId: MaybeRefOrGetter<number | null>, 
  id?: MaybeRefOrGetter<number | null | undefined>
) => {
  const { apiConfig } = useApi()
  const datasetsApi = new DatasetsApi(apiConfig)

  const { data: tilesets, isFetching: isFetchingTilesets } = useQuery({
    queryKey: ['datasets', () => toValue(datasetId), 'tilesets'],
    queryFn: () => {
      const datasetIdValue = toValue(datasetId)
      if (!datasetIdValue) throw new Error('Dataset ID is required')
      return datasetsApi.listDatasetsTilesets({ datasetId: datasetIdValue })
    },
    enabled: () => !!toValue(datasetId),
  })

  const { data: tileset, isFetching: isFetchingTileset } = useQuery({
    queryKey: ['datasets', () => toValue(datasetId), 'tilesets', () => toValue(id)],
    queryFn: () => {
      const datasetIdValue = toValue(datasetId)
      const idValue = toValue(id)
      if (!datasetIdValue || !idValue) throw new Error('Dataset ID and Tileset ID are required')
      return datasetsApi.retrieveDatasetsTilesets({ 
        datasetId: datasetIdValue, 
        id: idValue 
      })
    },
    enabled: () => !!toValue(datasetId) && !!toValue(id),
  })

  const { data: presignedUrl, isFetching: isFetchingPresignedUrl } = useQuery({
    queryKey: ['datasets', () => toValue(datasetId), 'tilesets', () => toValue(id), 'presigned-url'],
    queryFn: () => {
      const datasetIdValue = toValue(datasetId)
      const idValue = toValue(id)
      if (!datasetIdValue || !idValue) throw new Error('Dataset ID and Tileset ID are required')
      return datasetsApi.retrieveDatasetsTilesetsPresignedUrl({ 
        datasetId: datasetIdValue, 
        id: idValue 
      })
    },
    enabled: () => !!toValue(datasetId) && !!toValue(id),
  })

  return {
    tilesets,
    isFetchingTilesets,
    tileset,
    isFetchingTileset,
    presignedUrl,
    isFetchingPresignedUrl,
  }
}

export default useTilesetQuery