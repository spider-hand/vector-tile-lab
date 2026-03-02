<template>
  <div class="flex flex-col gap-2">
    <label class="text-xs font-medium text-muted-foreground">{{ label }}</label>
    <div class="flex items-center gap-3">
      <Slider :model-value="[modelValue]" :min="min" :max="max" :step="step" class="flex-1"
        @update:model-value="$emit('update:modelValue', $event![0])" />
      <span class="text-xs w-8 text-right">{{ modelValue }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { Slider } from '@/components/ui/slider'

defineProps<{
  modelValue: number
  label: string
  min: number
  max: number
  step: number
}>()

defineEmits<{
  'update:modelValue': [value: number]
}>()
</script>
