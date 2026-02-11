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
  <TweakSidebar v-show="tweakSidebarOpen" @close="activeItem = null" />
  <MetadataSidebar v-show="metadataSidebarOpen" @close="activeItem = null" />
  <TilesetSidebar v-show="tilesetSidebarOpen" @close="activeItem = null" />
</template>

<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import UploadSidebar from '@/components/UploadSidebar.vue'
import MetadataSidebar from '@/components/MetadataSidebar.vue'
import TweakSidebar from '@/components/TweakSidebar.vue'
import TilesetSidebar from '@/components/TilesetSidebar.vue'
import { FileText, SlidersHorizontal, Upload, Layers } from 'lucide-vue-next'

type MenuItem = 'Upload' | 'Tweak' | 'Metadata' | 'Tileset';
const items: Array<{ title: MenuItem; icon: Component }> = [
  { title: 'Upload', icon: Upload },
  { title: 'Tweak', icon: SlidersHorizontal },
  { title: 'Metadata', icon: FileText },
  { title: 'Tileset', icon: Layers }
]

const activeItem = ref<MenuItem | null>(null)
const uploadSidebarOpen = computed(() => activeItem.value === 'Upload')
const tweakSidebarOpen = computed(() => activeItem.value === 'Tweak')
const metadataSidebarOpen = computed(() => activeItem.value === 'Metadata')
const tilesetSidebarOpen = computed(() => activeItem.value === 'Tileset')

const handleMenuClick = (title: MenuItem) => {
  if (activeItem.value === title) {
    activeItem.value = null;
  } else {
    activeItem.value = title;
  }
}
</script>