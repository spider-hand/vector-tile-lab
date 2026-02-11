<template>
  <div class="flex flex-col gap-1">
    <span class="text-muted-foreground">{{ label }}:</span>
    <p class="font-medium" :class="{
      'truncate': truncate,
      'text-xs font-mono bg-white rounded border break-all p-1': mono
    }">
      {{ value }}
    </p>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string
  value: string | number
  truncate?: boolean
  mono?: boolean
}>()
</script>
