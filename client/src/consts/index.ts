import type { LayerType } from '@/types'

export const LAYER_TYPES: LayerType[] = ['fill', 'line', 'circle']

// chart.js color palette
export const COLOR_PALETTE = {
  GRAY: 'rgb(201, 203, 207)',
  BLUE: 'rgb(54, 162, 235)',
  GREEN: 'rgb(75, 192, 192)',
  ORANGE: 'rgb(255, 159, 64)',
  RED: 'rgb(255, 99, 132)',
}

export const TIER_COLORS = [
  COLOR_PALETTE.GRAY,
  COLOR_PALETTE.BLUE,
  COLOR_PALETTE.GREEN,
  COLOR_PALETTE.ORANGE,
  COLOR_PALETTE.RED,
]
