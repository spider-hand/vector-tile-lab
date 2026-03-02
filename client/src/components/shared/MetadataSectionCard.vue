<template>
  <Card class="bg-muted/50 py-4 shadow-none gap-2">
    <CardHeader class="px-4">
      <CardTitle class="text-sm">{{ title }}</CardTitle>
    </CardHeader>
    <CardContent class="px-4">
      <slot />
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

defineProps<{
  title: string
}>()
</script>