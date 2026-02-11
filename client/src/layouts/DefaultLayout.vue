<template>
  <div class="fixed top-4 left-4 z-[999] w-[200px]">
    <Card class="p-2">
      <div class="flex flex-col gap-1">
        <Button
          v-for="item in items"
          :key="item.title"
          :variant="activeItem === item.title ? 'secondary' : 'ghost'"
          class="justify-start gap-2"
          @click="handleMenuClick(item.title)"
        >
          <component :is="item.icon" class="h-4 w-4" />
          <span>{{ item.title }}</span>
        </Button>
      </div>
    </Card>
  </div>
  <main>
    <router-view />
  </main>

  <UploadSidebar v-show="uploadSidebarOpen" @close="activeItem = null" />
  <TilesetSidebar v-show="tilesetSidebarOpen" @close="activeItem = null" />
  <MetadataSidebar v-show="metadataSidebarOpen" @close="activeItem = null" />
  <StyleSidebar v-show="styleSidebarOpen" @close="activeItem = null" />
</template>

<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import UploadSidebar from '@/components/UploadSidebar.vue'
import MetadataSidebar from '@/components/MetadataSidebar.vue'
import TilesetSidebar from '@/components/TilesetSidebar.vue'
import StyleSidebar from '@/components/StyleSidebar.vue'
import { FileText, Layers, Upload, WandSparkles } from 'lucide-vue-next'

type MenuItem = 'Upload' | 'Tilesets' | 'Metadata' | 'Style';
const items: Array<{ title: MenuItem; icon: Component }> = [
  { title: 'Upload', icon: Upload },
  { title: 'Tilesets', icon: Layers },
  { title: 'Metadata', icon: FileText },
  { title: 'Style', icon: WandSparkles }
]

const activeItem = ref<MenuItem | null>(null)
const uploadSidebarOpen = computed(() => activeItem.value === 'Upload')
const tilesetSidebarOpen = computed(() => activeItem.value === 'Tilesets')
const metadataSidebarOpen = computed(() => activeItem.value === 'Metadata')
const styleSidebarOpen = computed(() => activeItem.value === 'Style')

const handleMenuClick = (title: MenuItem) => {
  if (activeItem.value === title) {
    activeItem.value = null;
  } else {
    activeItem.value = title;
  }
}
</script>