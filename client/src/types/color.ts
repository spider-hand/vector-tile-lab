export type ColorSchemaCategory = 'sequential' | 'diverging'

export interface ColorSchema {
  name: string
  category: ColorSchemaCategory
  colors: string[]
}

export interface ColorThemeOption {
  label: string
  value: string
  colors: string[]
  category: ColorSchemaCategory
}

export interface ColorThemeGroup {
  category: ColorSchemaCategory
  label: string
  options: ColorThemeOption[]
}
