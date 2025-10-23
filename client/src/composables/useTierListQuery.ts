import { useQuery } from '@tanstack/vue-query'
import { DatasetsApi } from '@/services/apis/DatasetsApi'
import useApi from './useApi'
import { toValue, type MaybeRefOrGetter } from 'vue'

export const useTierListQuery = (
  datasetId: MaybeRefOrGetter<number | null>,
  tilesetId: MaybeRefOrGetter<number | null>,
) => {
  const { apiConfig } = useApi()
  const datasetsApi = new DatasetsApi(apiConfig)

  const {
    data: tierLists,
    isFetching: isFetchingTierLists,
    error: tierListsError,
  } = useQuery({
    queryKey: ['datasets', () => toValue(datasetId), 'tilesets', () => toValue(tilesetId), 'tiers'],
    queryFn: () => {
      const datasetIdValue = toValue(datasetId)
      const tilesetIdValue = toValue(tilesetId)
      if (!datasetIdValue || !tilesetIdValue) {
        throw new Error('Dataset ID and Tileset ID are required')
      }
      return datasetsApi.listDatasetsTiers({
        datasetId: datasetIdValue,
      })
    },
    enabled: () => !!toValue(datasetId) && !!toValue(tilesetId),
  })

  return {
    tierLists,
    isFetchingTierLists,
    tierListsError,
  }
}
