<template>
  <div class="text-center py-8 text-sm text-muted-foreground">
    <div class="flex flex-col items-center gap-2">
      <div class="w-12 h-12 bg-muted/50 rounded-full flex items-center justify-center">
        <PackageSearch />
      </div>
      <p>{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { PackageSearch } from 'lucide-vue-next';

defineProps<{
  message: string
}>()
</script>