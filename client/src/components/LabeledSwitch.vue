<template>
  <div class="flex items-center justify-between">
    <InfoTooltipLabel :tooltip-text="tooltipText" :label-text="labelText" />
    <Switch :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event)" />
  </div>
</template>

<script setup lang="ts">
import InfoTooltipLabel from './InfoTooltipLabel.vue'
import { Switch } from '@/components/ui/switch'

defineProps<{
  modelValue: boolean
  tooltipText: string
  labelText: string
}>()

defineEmits<{
  'update:modelValue': [value: boolean]
}>()
</script>
