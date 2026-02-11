<template>
  <div class="flex flex-col gap-2">
    <label v-if="label" class="text-xs font-medium text-muted-foreground">{{ label }}</label>
    <Select :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event as string)">
      <SelectTrigger>
        <SelectValue :placeholder="placeholder" />
      </SelectTrigger>
      <SelectContent class="z-[9999]">
        <SelectItem v-for="option in options" :key="option.value" :value="option.value">
          {{ option.label }}
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>

<script setup lang="ts">
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

export interface SelectOption {
  value: string
  label: string
}

defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  options: SelectOption[]
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()
</script>
