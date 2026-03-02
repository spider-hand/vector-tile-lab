<template>
  <div
    v-if="visible && tierStyleConfig"
    class="absolute rounded-lg shadow-lg bg-card/95 border border-border"
    :style="positionStyles"
  >
    <div class="p-3">
      <h3
        class="mb-2 text-card-foreground"
        :style="{ fontFamily: fontFamily, fontSize: `${fontSize + 2}px`, fontWeight: titleFontWeight }"
      >
        {{ title }}
      </h3>
      <div class="flex flex-col gap-1.5">
        <div
          v-for="(breakValue, index) in tierStyleConfig.breaks"
          :key="index"
          class="flex items-center gap-2"
        >
          <div
            class="w-4 h-4 rounded-sm shrink-0"
            :style="{ backgroundColor: tierStyleConfig.colors[index] }"
          ></div>
          <span
            class="text-muted-foreground"
            :style="{ fontFamily: fontFamily, fontSize: `${fontSize}px`, fontWeight: itemFontWeight }"
          >
            {{ getTierRange(Number(index), tierStyleConfig.breaks) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useLayerStyles } from '@/composables/useLayerStyles'
import { getTierRange } from '@/utils/color'
import type { LegendPosition, FontFamily, FontWeight } from '@/types'

const props = defineProps<{
  title: string
  fontFamily: FontFamily
  fontSize: number
  titleFontWeight: FontWeight
  itemFontWeight: FontWeight
  position: LegendPosition
  padding: number
  visible: boolean
}>()

const { tierStyleConfig } = useLayerStyles()

const positionStyles = computed(() => {
  const styles: Record<string, string> = {}
  const padding = `${props.padding}px`

  switch (props.position) {
    case 'top-left':
      styles.top = padding
      styles.left = padding
      break
    case 'top-right':
      styles.top = padding
      styles.right = padding
      break
    case 'bottom-left':
      styles.bottom = padding
      styles.left = padding
      break
    case 'bottom-right':
      styles.bottom = padding
      styles.right = padding
      break
  }

  return styles
})
</script>
