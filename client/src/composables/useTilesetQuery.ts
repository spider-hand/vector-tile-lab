import { useQuery } from '@tanstack/vue-query'
import { TilesetsApi } from '@/services/apis/TilesetsApi'
import useApi from './useApi'
import { toValue, type MaybeRefOrGetter } from 'vue'

export const useTilesetQuery = (id?: MaybeRefOrGetter<number | undefined>) => {
  const { apiConfig } = useApi()
  const tilesetsApi = new TilesetsApi(apiConfig)

  const { data: tilesets, isFetching: isFetchingTilesets } = useQuery({
    queryKey: ['tilesets'],
    queryFn: () => tilesetsApi.listTilesets(),
  })

  const { data: tileset, isFetching: isFetchingTileset } = useQuery({
    queryKey: ['tilesets', () => toValue(id)],
    queryFn: () => {
      const idValue = toValue(id)
      return tilesetsApi.retrieveTilesets({ id: idValue! })
    },
    enabled: () => !!toValue(id),
  })

  const { data: presignedUrl, isFetching: isFetchingPresignedUrl } = useQuery({
    queryKey: ['tilesets', () => toValue(id), 'presigned-url'],
    queryFn: () => {
      const idValue = toValue(id)
      return tilesetsApi.retrieveTilesetsPresignedUrl({ id: idValue! })
    },
    enabled: () => !!toValue(id),
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