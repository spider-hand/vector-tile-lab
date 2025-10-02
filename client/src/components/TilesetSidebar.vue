<template>
  <Sheet :open="open" @update:open="(value: boolean) => $emit('update:open', value)" :modal="false">
    <SheetContent side="left" class="w-80 flex flex-col" :style="{ marginLeft: sidebarMargin }"
      @interact-outside="(e) => e.preventDefault()">
      <SheetHeader>
        <SheetTitle>Tilesets</SheetTitle>
        <SheetDescription>
          Manage and configure your vector tilesets
        </SheetDescription>
      </SheetHeader>

      <div class="flex flex-col gap-2 px-4">
        <h3 class="text-sm font-medium">Tilesets</h3>
        <div v-if="isFetchingTilesets" class="flex items-center justify-center py-4">
          <LoaderCircle class="h-4 w-4 animate-spin text-muted-foreground" />
          <span class="text-sm text-muted-foreground ml-2">Loading tilesets...</span>
        </div>
        <div v-else-if="tilesets && tilesets.length > 0" class="rounded-lg border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead class="text-xs">ID</TableHead>
                <TableHead class="text-xs">Name</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow v-for="tileset in tilesets" :key="tileset.id"
                :data-state="selectedTilesetId === tileset.id && 'selected'" @click="setSelectedTileset(tileset.id)"
                class="cursor-pointer">
                <TableCell class="text-xs font-medium">{{ tileset.id }}</TableCell>
                <TableCell class="text-xs truncate" :title="tileset.name">
                  {{ tileset.name }}
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </div>
        <div v-else class="text-center py-4 text-sm text-muted-foreground">
          No tilesets available
        </div>
      </div>
    </SheetContent>
  </Sheet>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useSidebar } from '@/components/ui/sidebar/utils'
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from '@/components/ui/sheet'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { LoaderCircle } from 'lucide-vue-next'
import { useSelectedData } from '@/composables/useSelectedData'
import useTilesetQuery from '@/composables/useTilesetQuery'

defineProps({
  open: {
    type: Boolean,
    required: true
  }
})

defineEmits<{
  'update:open': [value: boolean]
}>()

const { open: sidebarOpen, isMobile } = useSidebar()

const sidebarMargin = computed(() => {
  if (isMobile.value) {
    return '0'
  }
  return sidebarOpen.value ? '10rem' : '0'
})

const { selectedDatasetId, selectedTilesetId, setSelectedTileset } = useSelectedData()
const { tilesets, isFetchingTilesets } = useTilesetQuery(selectedDatasetId, selectedTilesetId)
</script>

<style scoped>
.overflow-y-auto::-webkit-scrollbar {
  width: 4px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f5f9;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
  background: #94a3b8;
}
</style>
