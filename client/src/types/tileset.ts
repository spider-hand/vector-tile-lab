export interface TileMetadataResponse {
  header: TileHeader
  metadata: TileMetadata
}

export interface TileHeader {
  min_zoom: number
  max_zoom: number
  bounds: [number, number, number, number]
  center: [number, number, number]
}

export interface TileMetadata {
  vector_layers: VectorLayer[]
  description: string
  name: string
  version: string
  format: string
  generator: string
  generator_options: string
  strategies: Strategy[]
  tilestats: TileStats
  [key: string]: unknown
}

export interface VectorLayer {
  id: string
  fields: { [key: string]: string }
  description: string
  maxzoom: number
  minzoom: number
}

export interface Strategy {
  detail_reduced?: number
  tile_size_desired?: number
  tiny_polygons?: number
}

export interface TileStats {
  layerCount: number
  layers: LayerStat[]
}

export interface LayerStat {
  attributeCount: number
  attributes: AttributeStats[]
  count: number
  geometry: string
  layer: string
}

export interface AttributeStats {
  attribute: string
  count: number
  max?: number
  min?: number
  type: string
  values: (string | number | boolean)[]
}

export interface DataStat {
  field: string
  type: string
  count: number
  min?: number
  max?: number
}

export type LayerType = 'fill' | 'line' | 'circle'

export interface LayerVisibilityState {
  [layerId: string]: Record<LayerType, boolean>
}
