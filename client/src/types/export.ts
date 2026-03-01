export type LegendPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
export type FontFamily = 'Inter' | 'IBM Plex Sans' | 'Barlow' | 'Manrope' | 'Space Grotesk'
export type FontWeight = '400' | '500' | '600' | '700'
export type AspectRatio = '16:9' | '4:3' | '1:1' | '3:2'

export interface LegendSettings {
  title: string
  fontFamily: FontFamily
  fontSize: number
  titleFontWeight: FontWeight
  itemFontWeight: FontWeight
  position: LegendPosition
  padding: number
  visible: boolean
}

export interface ExportSettings {
  aspectRatio: AspectRatio
}
