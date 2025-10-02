<template>
  <BaseSidebar :open="open" @update:open="$emit('update:open', $event)" title="Tilesets"
    description="Manage and configure your vector tilesets">
    <div class="flex flex-col gap-2">
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
  </BaseSidebar>
</template>

<script setup lang="ts">
import BaseSidebar from './BaseSidebar.vue'
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

const { selectedDatasetId, selectedTilesetId, setSelectedTileset } = useSelectedData()
const { tilesets, isFetchingTilesets } = useTilesetQuery(selectedDatasetId, selectedTilesetId)
</script>
