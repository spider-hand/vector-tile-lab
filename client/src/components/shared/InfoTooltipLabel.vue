<template>
  <div class="flex items-center gap-1">
    <Tooltip>
      <TooltipTrigger as-child>
        <Button size="icon" variant="ghost" tabindex="-1">
          <Info class="h-4 w-4 text-muted-foreground" />
        </Button>
      </TooltipTrigger>
      <TooltipContent class="z-[9999] max-w-[10rem]">
        <p>{{ tooltipText }}</p>
      </TooltipContent>
    </Tooltip>
    <label class="text-xs font-medium">{{ labelText }}</label>
  </div>
</template>

<script setup lang="ts">
import { Tooltip, TooltipContent, TooltipTrigger } from '@/components/ui/tooltip'
import { Button } from '@/components/ui/button'
import { Info } from 'lucide-vue-next'

defineProps<{
  tooltipText: string
  labelText: string
}>()
</script>