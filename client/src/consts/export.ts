import type { LegendPosition, FontFamily, FontWeight, AspectRatio } from '@/types'

export const FONT_FAMILY_OPTIONS: { label: string; value: FontFamily }[] = [
  { label: 'Inter', value: 'Inter' },
  { label: 'IBM Plex Sans', value: 'IBM Plex Sans' },
  { label: 'Barlow', value: 'Barlow' },
  { label: 'Manrope', value: 'Manrope' },
  { label: 'Space Grotesk', value: 'Space Grotesk' },
]

export const FONT_WEIGHT_OPTIONS: { label: string; value: FontWeight }[] = [
  { label: 'Normal', value: '400' },
  { label: 'Medium', value: '500' },
  { label: 'Semibold', value: '600' },
  { label: 'Bold', value: '700' },
]

export const LEGEND_POSITION_OPTIONS: { label: string; value: LegendPosition }[] = [
  { label: 'Top Left', value: 'top-left' },
  { label: 'Top Right', value: 'top-right' },
  { label: 'Bottom Left', value: 'bottom-left' },
  { label: 'Bottom Right', value: 'bottom-right' },
]

export const ASPECT_RATIO_OPTIONS: { label: string; value: AspectRatio }[] = [
  { label: '16:9', value: '16:9' },
  { label: '4:3', value: '4:3' },
  { label: '3:2', value: '3:2' },
  { label: '1:1', value: '1:1' },
]
