import type { Map as MapLibreMap } from 'maplibre-gl'

export interface TileLoadMetrics {
  sourceId: string
  loadTime: number
  timestamp: number
}

export interface TileLoadStats {
  initialLoadTime: number
  avgLoadTime: number
  maxLoadTime: number
  minLoadTime: number
  totalRequests: number
}

class MapTileMonitor {
  private _metrics: TileLoadMetrics[] = []
  private _sourceLoadTimes = new Map<string, number>()

  setup(map: MapLibreMap, targetSourceId: string) {
    map.on('sourcedataloading', (e) => {
      const sourceId = e.sourceId
      if (sourceId !== targetSourceId) return

      this._sourceLoadTimes.set(sourceId, performance.now())
    })

    map.on('sourcedata', (e) => {
      if (e.isSourceLoaded) {
        const sourceId = e.sourceId
        if (sourceId !== targetSourceId) return

        const startTime = this._sourceLoadTimes.get(sourceId)

        if (startTime) {
          const endTime = performance.now()
          const loadTime = endTime - startTime

          const metric: TileLoadMetrics = {
            sourceId,
            loadTime,
            timestamp: Date.now(),
          }
          this._metrics.push(metric)
          this._sourceLoadTimes.delete(sourceId)
        }
      }
    })
  }

  get stats() {
    if (this._metrics.length === 0) {
      return {
        initialLoadTime: 0,
        avgLoadTime: 0,
        maxLoadTime: 0,
        minLoadTime: 0,
        totalRequests: 0,
      }
    }

    const loadTimes = this._metrics.map((m) => m.loadTime)

    return {
      initialLoadTime: this._metrics[0].loadTime,
      avgLoadTime: loadTimes.length > 0 ? loadTimes.reduce((a, b) => a + b) / loadTimes.length : 0,
      maxLoadTime: Math.max(...loadTimes, 0),
      minLoadTime: Math.min(...loadTimes, Infinity),
      totalRequests: loadTimes.length,
    }
  }

  get latestMetric(): TileLoadMetrics | null {
    return this._metrics.length > 0 ? this._metrics[this._metrics.length - 1] : null
  }

  clear() {
    this._metrics = []
    this._sourceLoadTimes.clear()
  }
}

export const mapTileMonitor = new MapTileMonitor()
