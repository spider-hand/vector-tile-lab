import type { LayerType } from '@/types'

export const LAYER_TYPES: LayerType[] = ['fill', 'line', 'circle']

export const COLOR_PALETTE_CHARTJS = [
  'rgb(201, 203, 207)',
  'rgb(54, 162, 235)',
  'rgb(75, 192, 192)',
  'rgb(255, 159, 64)',
  'rgb(255, 99, 132)',
]

export const COLOR_PALETTE_APEXCHARTS = ['#775DD0', '#008FFB', '#00E396', '#FEB019', '#FF4560']

export const COLOR_PALETTE_RED = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']

export const COLOR_PALETTE_BLUE = ['#ffffcc', '#a1dab4', '#41b6c4', '#2c7fb8', '#253494']

export const COLOR_PALETTE_GREEN = ['#ffffcc', '#c2e699', '#78c679', '#31a354', '#006837']

export type ColorPaletteType = 'chartjs' | 'apexcharts' | 'red' | 'blue' | 'green'

export const TIER_COLORS: Record<ColorPaletteType, string[]> = {
  chartjs: COLOR_PALETTE_CHARTJS,
  apexcharts: COLOR_PALETTE_APEXCHARTS,
  red: COLOR_PALETTE_RED,
  blue: COLOR_PALETTE_BLUE,
  green: COLOR_PALETTE_GREEN,
}

export const COLOR_THEME_LIST = [
  { label: 'Chart.js', value: 'chartjs' },
  { label: 'ApexCharts', value: 'apexcharts' },
  { label: 'Red', value: 'red' },
  { label: 'Blue', value: 'blue' },
  { label: 'Green', value: 'green' },
]

export const DEFFAULT_COLOR = COLOR_PALETTE_CHARTJS[1] // Blue
