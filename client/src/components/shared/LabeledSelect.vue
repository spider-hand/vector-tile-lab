<template>
  <div class="flex flex-col gap-2">
    <label v-if="label" class="text-xs font-medium text-muted-foreground">{{ label }}</label>
    <Select :model-value="modelValue" @update:model-value="$emit('update:modelValue', $event as string)">
      <SelectTrigger>
        <SelectValue :placeholder="placeholder">
          <div v-if="selectedOption" class="flex items-center gap-2">
            <div v-if="selectedOption.colors" class="flex gap-0.5">
              <span
                v-for="(color, index) in selectedOption.colors"
                :key="index"
                class="w-3 h-3 rounded-sm"
                :style="{ backgroundColor: color }"
              />
            </div>
            <span class="text-xs">{{ selectedOption.label }}</span>
          </div>
        </SelectValue>
      </SelectTrigger>
      <SelectContent class="z-[9999]">
        <template v-if="groups && groups.length > 0">
          <SelectGroup v-for="group in groups" :key="group.category">
            <SelectLabel class="text-xs font-semibold text-muted-foreground">
              {{ group.label }}
            </SelectLabel>
            <SelectItem v-for="option in group.options" :key="option.value" :value="option.value">
              <div class="flex items-center gap-2">
                <div v-if="option.colors" class="flex gap-0.5">
                  <span
                    v-for="(color, index) in option.colors"
                    :key="index"
                    class="w-3 h-3 rounded-sm"
                    :style="{ backgroundColor: color }"
                  />
                </div>
                <span class="text-xs">{{ option.label }}</span>
              </div>
            </SelectItem>
          </SelectGroup>
        </template>
        <template v-else>
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
              <span>{{ option.label }}</span>
            </div>
          </SelectItem>
        </template>
      </SelectContent>
    </Select>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectTrigger,
  SelectValue
} from '@/components/ui/select'

export interface SelectOption {
  value: string
  label: string
  colors?: string[]
}

export interface SelectGroup {
  category: string
  label: string
  options: SelectOption[]
}

const props = defineProps<{
  modelValue: string
  label?: string
  placeholder?: string
  options: SelectOption[]
  groups?: SelectGroup[]
}>()

defineEmits<{
  'update:modelValue': [value: string]
}>()

const selectedOption = computed(() => {
  if (props.groups && props.groups.length > 0) {
    for (const group of props.groups) {
      const found = group.options.find(opt => opt.value === props.modelValue)
      if (found) return found
    }
    return undefined
  }
  return props.options.find(opt => opt.value === props.modelValue)
})
</script>
