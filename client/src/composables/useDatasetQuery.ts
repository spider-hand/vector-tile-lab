import { useMutation, useQuery, useQueryClient } from '@tanstack/vue-query'
import { DatasetsApi } from '@/services/apis/DatasetsApi'
import useApi from './useApi'
import { toValue, type MaybeRefOrGetter } from 'vue'
import { RetrieveDatasetsProgress200ResponseStatusEnum } from '@/services'

export const useDatasetQuery = (
  id?: MaybeRefOrGetter<number | null>,
  progressId?: MaybeRefOrGetter<number | null>,
) => {
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
      return datasetsApi.retrieveDatasets({ id: idValue! })
    },
    enabled: () => !!toValue(id),
  })

  const { data: progress, isError: isProgressError } = useQuery({
    queryKey: ['datasets', () => toValue(progressId), 'progress'],
    queryFn: () => {
      const idValue = toValue(progressId)
      return datasetsApi.retrieveDatasetsProgress({ id: idValue! })
    },
    enabled: () => !!toValue(progressId),
    refetchInterval: (query) => {
      // Stop polling when processing is complete or if there's an error
      if (
        !query.state.data ||
        query.state.data.status === RetrieveDatasetsProgress200ResponseStatusEnum.Completed ||
        query.state.data.status === RetrieveDatasetsProgress200ResponseStatusEnum.Failed
      ) {
        return false
      }
      // Poll every 2 seconds while processing
      return 2000
    },
    staleTime: 0, // Always refetch to get latest progress
  })

  const {
    mutate: mutateOnCreateDataset,
    isPending: isCreatingDataset,
    isSuccess: isCreateDatasetSuccess,
  } = useMutation({
    mutationFn: async (params: { 
      name: string
      geojsonFile?: File
      shpFile?: File
      shxFile?: File
      dbfFile?: File
      prjFile?: File
      cpgFile?: File
    }) => {
      return await datasetsApi.createDatasets({
        name: params.name,
        geojsonFile: params.geojsonFile,
        shpFile: params.shpFile,
        shxFile: params.shxFile,
        dbfFile: params.dbfFile,
        prjFile: params.prjFile,
        cpgFile: params.cpgFile,
      })
    },
  })

  const { mutate: mutateOnDeleteDataset, isPending: isDeletingDataset } = useMutation({
    mutationFn: (id: number) => datasetsApi.destroyDatasets({ id }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
    },
  })

  const refetchDatasets = () => {
    queryClient.invalidateQueries({ queryKey: ['datasets'] })
  }

  return {
    datasets,
    isFetchingDatasets,
    dataset,
    isFetchingDataset,
    progress,
    isProgressError,
    mutateOnCreateDataset,
    isCreatingDataset,
    isCreateDatasetSuccess,
    mutateOnDeleteDataset,
    isDeletingDataset,
    refetchDatasets,
  }
}

export default useDatasetQuery
