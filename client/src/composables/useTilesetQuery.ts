import { useQuery, useMutation, useQueryClient } from '@tanstack/vue-query'
import { DatasetsApi } from '@/services/apis/DatasetsApi'
import useApi from './useApi'
import { toValue, type MaybeRefOrGetter } from 'vue'

export const useTilesetQuery = (
  datasetId: MaybeRefOrGetter<number | null>,
  id?: MaybeRefOrGetter<number | null | undefined>,
  progressTilesetId?: MaybeRefOrGetter<number | null | undefined>,
) => {
  const { apiConfig } = useApi()
  const datasetsApi = new DatasetsApi(apiConfig)

  const { data: tilesets, isFetching: isFetchingTilesets } = useQuery({
    queryKey: ['datasets', () => toValue(datasetId), 'tilesets'],
    queryFn: () => {
      const datasetIdValue = toValue(datasetId)
      if (!datasetIdValue) throw new Error('Dataset ID is required')
      return datasetsApi.listDatasetsTilesets({ datasetId: datasetIdValue, status: 'completed' })
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
        id: idValue,
      })
    },
    enabled: () => !!toValue(datasetId) && !!toValue(id),
  })

  const { data: presignedUrl, isFetching: isFetchingPresignedUrl } = useQuery({
    queryKey: [
      'datasets',
      () => toValue(datasetId),
      'tilesets',
      () => toValue(id),
      'presigned-url',
    ],
    queryFn: () => {
      const datasetIdValue = toValue(datasetId)
      const idValue = toValue(id)
      if (!datasetIdValue || !idValue) throw new Error('Dataset ID and Tileset ID are required')
      return datasetsApi.retrieveDatasetsTilesetsPresignedUrl({
        datasetId: datasetIdValue,
        id: idValue,
      })
    },
    enabled: () => !!toValue(datasetId) && !!toValue(id),
  })

  const queryClient = useQueryClient()

  // Progress query for tileset generation - only enabled when progressTilesetId is provided
  const { data: progress, isError: isProgressError } = useQuery({
    queryKey: [
      'datasets',
      () => toValue(datasetId),
      'tilesets',
      () => toValue(progressTilesetId),
      'progress',
    ],
    queryFn: () => {
      const datasetIdValue = toValue(datasetId)
      const progressIdValue = toValue(progressTilesetId)
      if (!datasetIdValue || !progressIdValue)
        throw new Error('Dataset ID and Progress Tileset ID are required')

      return datasetsApi.retrieveDatasetsTilesetsProgress({
        datasetId: datasetIdValue,
        id: progressIdValue,
      })
    },
    enabled: () => !!toValue(datasetId) && !!toValue(progressTilesetId),
    refetchInterval: (query) => {
      // Stop polling when processing is complete or if there's an error
      if (
        !query.state.data ||
        query.state.data.status === 'completed' ||
        query.state.data.status === 'failed'
      ) {
        return false
      }
      // Poll every 2 seconds while processing
      return 2000
    },
    staleTime: 0, // Always refetch to get latest progress
  })

  // Mutation for creating tilesets
  const {
    mutate: mutateOnCreateTileset,
    isPending: isCreatingTileset,
    isSuccess: isCreateTilesetSuccess,
  } = useMutation({
    mutationFn: async ({
      name,
      maximumZoom,
      dropDensestAsNeeded,
      coalesceDensestAsNeeded,
      extendZoomsIfStillDropping,
    }: {
      name: string
      maximumZoom: string
      dropDensestAsNeeded: boolean
      coalesceDensestAsNeeded: boolean
      extendZoomsIfStillDropping: boolean
    }) => {
      const datasetIdValue = toValue(datasetId)
      if (!datasetIdValue) throw new Error('Dataset ID is required')

      return await datasetsApi.createDatasetsTilesets({
        datasetId: datasetIdValue,
        createDatasetsTilesetsRequest: {
          name,
          maximumZoom,
          dropDensestAsNeeded,
          coalesceDensestAsNeeded,
          extendZoomsIfStillDropping,
        },
      })
    },
    // Don't invalidate immediately - wait for generation to complete
  })

  // Function to refetch tilesets (called after generation completes)
  const refetchTilesets = () => {
    queryClient.invalidateQueries({
      queryKey: ['datasets', toValue(datasetId), 'tilesets'],
    })
  }

  return {
    tilesets,
    isFetchingTilesets,
    tileset,
    isFetchingTileset,
    presignedUrl,
    isFetchingPresignedUrl,
    progress,
    isProgressError,
    mutateOnCreateTileset,
    isCreatingTileset,
    isCreateTilesetSuccess,
    refetchTilesets,
  }
}

export default useTilesetQuery
