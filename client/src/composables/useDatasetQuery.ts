import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { DatasetsApi } from '@/services/apis/DatasetsApi'
import useApi from './useApi'
import { toValue, type MaybeRefOrGetter } from 'vue'

export const useDatasetQuery = (id?: MaybeRefOrGetter<number | undefined>) => {
  const { apiConfig } = useApi()
  const datasetsApi = new DatasetsApi(apiConfig)
  const queryClient = useQueryClient()

  const { data: datasets, isFetching: isFetchingDatasets } = useQuery({
    queryKey: ['datasets'],
    queryFn: () => datasetsApi.listDatasets(),
  })

  const { data: dataset, isFetching: isFetchingDataset } = useQuery({
    queryKey: ['datasets', () => toValue(id)],
    queryFn: () => {
      const idValue = toValue(id)
      datasetsApi.retrieveDatasets({ id: idValue! })
    },
    enabled: () => !!toValue(id),
  })

  const {
    mutate: mutateOnCreateDataset,
    isPending: isCreatingDataset,
    isSuccess: isCreateDatasetSuccess,
  } = useMutation({
    mutationFn: async ({ name, file }: { name: string; file: File }) => {
      return await datasetsApi.createDatasets({ name, geojsonFile: file })
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
    },
  })

  const { mutate: mutateOnDeleteDataset, isPending: isDeletingDataset } = useMutation({
    mutationFn: (id: number) => datasetsApi.destroyDatasets({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
    },
  })

  return {
    datasets,
    isFetchingDatasets,
    dataset,
    isFetchingDataset,
    mutateOnCreateDataset,
    isCreatingDataset,
    isCreateDatasetSuccess,
    mutateOnDeleteDataset,
    isDeletingDataset,
  }
}

export default useDatasetQuery
