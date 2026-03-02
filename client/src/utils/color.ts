import { COLOR_SCHEMAS, DEFFAULT_COLOR } from '@/consts'
import type { ColorPaletteType } from '@/consts'
import type { ExpressionSpecification } from '@maplibre/maplibre-gl-style-spec'

/**
 * Samples colors evenly from an array to match the desired count.
 * Always includes the first and last colors (endpoints), then distributes
 * remaining picks evenly across the array to preserve the full color range.
 *
 * Example with 7 colors → 5:
 *   indices: 0, 2, 3, 5, 6 (endpoints + evenly spaced middle)
 */
const sampleColors = (colors: string[], count: number): string[] => {
  if (count >= colors.length) return [...colors]
  if (count <= 1) return [colors[0]]

  const result: string[] = []
  for (let i = 0; i < count; i++) {
    const index = Math.round((i * (colors.length - 1)) / (count - 1))
    result.push(colors[index])
  }
  return result
}

export const getTierColors = (schemaName: ColorPaletteType, classCount: number): string[] => {
  const schema = COLOR_SCHEMAS.find((s) => s.name === schemaName)
  if (!schema) return []
  return sampleColors(schema.colors, classCount)
}

export const getTierRange = (index: number, breaks: number[]): string => {
  if (!breaks || breaks.length === 0) return ''

  if (index === 0) {
    return `≤ ${breaks[0]}`
  } else {
    return `${breaks[index - 1]} - ${breaks[index]}`
  }
}

export const createTierColorExpression = (
  field: string,
  breaks: number[],
  colors: string[],
): ExpressionSpecification => {
  const expression: unknown[] = ['case']

  for (let i = 0; i < breaks.length; i++) {
    if (i === 0) {
      // First class: value <= breaks[0]
      expression.push(['<=', ['get', field], breaks[i]], colors[i])
    } else {
      // Subsequent classes: breaks[i-1] < value <= breaks[i]
      expression.push(
        ['all', ['>', ['get', field], breaks[i - 1]], ['<=', ['get', field], breaks[i]]],
        colors[i],
      )
    }
  }

  // Add fallback color for values that don't match any condition (required for 'case' expression)
  expression.push(DEFFAULT_COLOR)

  return expression as ExpressionSpecification
}
