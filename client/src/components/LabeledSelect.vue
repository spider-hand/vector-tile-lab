<template>
  <div class="flex flex-col gap-2">
    <label v-if="label" class="text-xs font-medium text-muted-foreground">{{ label }}</label>
    <Select :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event as string)">
      <SelectTrigger>
        <SelectValue :placeholder="placeholder">
          <div v-if="selectedOption?.colors" class="flex gap-0.5">
            <span
              v-for="(color, index) in selectedOption.colors"
              :key="index"
              class="w-3 h-3 rounded-sm"
              :style="{ backgroundColor: color }"
            />
          </div>
        </SelectValue>
      </SelectTrigger>
      <SelectContent class="z-[9999]">
        <SelectItem v-for="option in options" :key="option.value" :value="option.value">
          <div class="flex items-center gap-2">
            <div v-if="option.colors" class="flex gap-0.5">
              <span
                v-for="(color, index) in option.colors"
                :key="index"
                class="w-3 h-3 rounded-sm"
                :style="{ backgroundColor: color }"
              />
            </div>
            <span v-else>{{ option.label }}</span>
          </div>
        </SelectItem>
      </SelectContent>
    </Select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
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
  colors?: string[]
}

const props = defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  options: SelectOption[]
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()

const selectedOption = computed(() => {
  return props.options.find(opt => opt.value === props.modelValue)
})
</script>
