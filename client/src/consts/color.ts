import { MethodEnum } from '@/services'
import type { ColorSchema, ColorThemeGroup, ColorThemeOption } from '@/types'

export type ColorPaletteType = (typeof COLOR_SCHEMAS)[number]['name']

// @see: https://carto.com/carto-colors
export const COLOR_SCHEMAS: ColorSchema[] = [
  {
    name: 'Burg',
    category: 'sequential',
    colors: ['#ffc6c4', '#f4a3a8', '#e38191', '#cc607d', '#ad466c', '#8b3058', '#672044'],
  },
  {
    name: 'BurgYl',
    category: 'sequential',
    colors: ['#fbe6c5', '#f5ba98', '#ee8a82', '#dc7176', '#c8586c', '#9c3f5d', '#70284a'],
  },
  {
    name: 'RedOr',
    category: 'sequential',
    colors: ['#f6d2a9', '#f5b78e', '#f19c7c', '#ea8171', '#dd686c', '#ca5268', '#b13f64'],
  },
  {
    name: 'OrYel',
    category: 'sequential',
    colors: ['#ecda9a', '#efc47e', '#f3ad6a', '#f7945d', '#f97b57', '#f66356', '#ee4d5a'],
  },
  {
    name: 'Peach',
    category: 'sequential',
    colors: ['#fde0c5', '#facba6', '#f8b58b', '#f59e72', '#f2855d', '#ef6a4c', '#eb4a40'],
  },
  {
    name: 'PinkYl',
    category: 'sequential',
    colors: ['#fef6b5', '#ffdd9a', '#ffc285', '#ffa679', '#fa8a76', '#f16d7a', '#e15383'],
  },
  {
    name: 'Mint',
    category: 'sequential',
    colors: ['#e4f1e1', '#b4d9cc', '#89c0b6', '#63a6a0', '#448c8a', '#287274', '#0d585f'],
  },
  {
    name: 'BlueGrn',
    category: 'sequential',
    colors: ['#c4e6c3', '#96d2a4', '#6dbc90', '#4da284', '#36877a', '#266b6e', '#1d4f60'],
  },
  {
    name: 'DarkMint',
    category: 'sequential',
    colors: ['#d2fbd4', '#a5dbc2', '#7bbcb0', '#559c9e', '#3a7c89', '#235d72', '#123f5a'],
  },
  {
    name: 'Emrld',
    category: 'sequential',
    colors: ['#d3f2a3', '#97e196', '#6cc08b', '#4c9b82', '#217a79', '#105965', '#074050'],
  },
  {
    name: 'BluYl',
    category: 'sequential',
    colors: ['#f7feae', '#b7e6a5', '#7ccba2', '#46aea0', '#089099', '#00718b', '#045275'],
  },
  {
    name: 'Teal',
    category: 'sequential',
    colors: ['#d1eeea', '#a8dbd9', '#85c4c9', '#68abb8', '#4f90a6', '#3b738f', '#2a5674'],
  },
  {
    name: 'TealGrn',
    category: 'sequential',
    colors: ['#b0f2bc', '#89e8ac', '#67dba5', '#4cc8a3', '#38b2a3', '#2c98a0', '#257d98'],
  },
  {
    name: 'Purp',
    category: 'sequential',
    colors: ['#f3e0f7', '#e4c7f1', '#d1afe8', '#b998dd', '#9f82ce', '#826dba', '#63589f'],
  },
  {
    name: 'PurpOr',
    category: 'sequential',
    colors: ['#f9ddda', '#f2b9c4', '#e597b9', '#ce78b3', '#ad5fad', '#834ba0', '#573b88'],
  },
  {
    name: 'Sunset',
    category: 'sequential',
    colors: ['#f3e79b', '#fac484', '#f8a07e', '#eb7f86', '#ce6693', '#a059a0', '#5c53a5'],
  },
  {
    name: 'Magenta',
    category: 'sequential',
    colors: ['#f3cbd3', '#eaa9bd', '#dd88ac', '#ca699d', '#b14d8e', '#91357d', '#6c2167'],
  },
  {
    name: 'SunsetDark',
    category: 'sequential',
    colors: ['#fcde9c', '#faa476', '#f0746e', '#e34f6f', '#dc3977', '#b9257a', '#7c1d6f'],
  },
  {
    name: 'BrwnYl',
    category: 'sequential',
    colors: ['#ede5cf', '#e0c2a2', '#d39c83', '#c1766f', '#a65461', '#813753', '#541f3f'],
  },
  {
    name: 'ArmyRose',
    category: 'diverging',
    colors: ['#798234', '#a3ad62', '#d0d3a2', '#fdfbe4', '#f0c6c3', '#df91a3', '#d46780'],
  },
  {
    name: 'Fall',
    category: 'diverging',
    colors: ['#3d5941', '#778868', '#b5b991', '#f6edbd', '#edbb8a', '#de8a5a', '#ca562c'],
  },
  {
    name: 'Geyser',
    category: 'diverging',
    colors: ['#008080', '#70a494', '#b4c8a8', '#f6edbd', '#edbb8a', '#de8a5a', '#ca562c'],
  },
  {
    name: 'Temps',
    category: 'diverging',
    colors: ['#009392', '#39b185', '#9ccb86', '#e9e29c', '#eeb479', '#e88471', '#cf597e'],
  },
  {
    name: 'TealRose',
    category: 'diverging',
    colors: ['#009392', '#72aaa1', '#b1c7b3', '#f1eac8', '#e5b9ad', '#d98994', '#d0587e'],
  },
  {
    name: 'Tropic',
    category: 'diverging',
    colors: ['#009B9E', '#42B7B9', '#A7D3D4', '#F1F1F1', '#E4C1D9', '#D691C1', '#C75DAB'],
  },
  {
    name: 'Earth',
    category: 'diverging',
    colors: ['#A16928', '#bd925a', '#d6bd8d', '#edeac2', '#b5c8b8', '#79a7ac', '#2887a1'],
  },
]

export const COLOR_THEME_GROUPS: ColorThemeGroup[] = [
  {
    category: 'sequential',
    label: 'Sequential',
    options: COLOR_SCHEMAS.filter((s) => s.category === 'sequential').map((s) => ({
      label: s.name,
      value: s.name,
      colors: s.colors,
      category: s.category,
    })),
  },
  {
    category: 'diverging',
    label: 'Diverging',
    options: COLOR_SCHEMAS.filter((s) => s.category === 'diverging').map((s) => ({
      label: s.name,
      value: s.name,
      colors: s.colors,
      category: s.category,
    })),
  },
]

export const COLOR_THEME_LIST: ColorThemeOption[] = COLOR_SCHEMAS.map((s) => ({
  label: s.name,
  value: s.name,
  colors: s.colors,
  category: s.category,
}))

export const CLASSIFICATION_METHOD_LIST: { label: string; value: MethodEnum }[] = [
  { label: 'Quantile', value: MethodEnum.Quantile },
  { label: 'Natural Breaks', value: MethodEnum.NaturalBreaks },
  { label: 'Percentile', value: MethodEnum.Percentile },
]

export const DEFFAULT_COLOR = '#3B82F6' // Tailwind CSS Blue-500
