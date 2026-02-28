<template>
  <div
    class="fixed inset-y-0 left-0 z-[999] flex flex-col p-2 border-r bg-background transition-all duration-300 ease-in-out"
    :class="collapsed ? 'w-14' : 'w-[200px]'">
    <div class="flex flex-col gap-1 flex-1">
      <Button v-for="item in items" :key="item.title" :variant="activeItem === item.title ? 'secondary' : 'ghost'"
        class="gap-2 transition-all duration-300" :class="collapsed ? 'justify-center px-0' : 'justify-start'"
        @click="handleMenuClick(item.title)">
        <component :is="item.icon" class="h-4 w-4 shrink-0" />
        <span v-show="!collapsed">{{ item.title }}</span>
      </Button>
    </div>
    <Button variant="ghost" class="gap-2 transition-all duration-300"
      :class="collapsed ? 'justify-center px-0' : 'justify-start'" @click="collapsed = !collapsed">
      <component :is="collapsed ? ChevronRight : ChevronLeft" class="h-4 w-4 shrink-0" />
    </Button>
  </div>

  <div class="fixed inset-y-0 w-80 overflow-hidden z-[998] transition-all duration-300 ease-in-out"
    :class="collapsed ? 'left-14' : 'left-[200px]'">
    <UploadSidebar :open="uploadSidebarOpen" @close="activeItem = null" />
    <TweakSidebar :open="tweakSidebarOpen" @close="activeItem = null" />
    <MetadataSidebar :open="metadataSidebarOpen" @close="activeItem = null" />
    <LayerSidebar :open="layerSidebarOpen" @close="activeItem = null" />
    <AttributeSidebar :open="attributeSidebarOpen" @close="activeItem = null" />
  </div>

  <Button v-if="mapboxToken" variant="ghost" size="icon"
    class="fixed top-2 right-2 z-[999] bg-background" @click="toggleTheme">
    <Sun v-if="theme === 'dark'" class="h-4 w-4" />
    <Moon v-else class="h-4 w-4" />
  </Button>

  <main>
    <router-view />
  </main>
</template>

<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import { Button } from '@/components/ui/button'
import UploadSidebar from '@/components/UploadSidebar.vue'
import MetadataSidebar from '@/components/MetadataSidebar.vue'
import TweakSidebar from '@/components/TweakSidebar.vue'
import AttributeSidebar from '@/components/AttributeSidebar.vue'
import { FileText, SlidersHorizontal, Upload, Tags, Layers, ChevronLeft, ChevronRight, Sun, Moon } from 'lucide-vue-next'
import LayerSidebar from '@/components/LayerSidebar.vue'
import { useTheme } from '@/composables/useTheme'

const mapboxToken = import.meta.env.VITE_MAPBOX_TOKEN

const { theme, toggleTheme } = useTheme()

type MenuItem = 'Upload' | 'Tweak' | 'Metadata' | 'Layer' | 'Attribute';
const items: Array<{ title: MenuItem; icon: Component }> = [
  { title: 'Upload', icon: Upload },
  { title: 'Tweak', icon: SlidersHorizontal },
  { title: 'Metadata', icon: FileText },
  { title: 'Layer', icon: Layers },
  { title: 'Attribute', icon: Tags }
]

const activeItem = ref<MenuItem | null>(null)
const collapsed = ref(false)

const uploadSidebarOpen = computed(() => activeItem.value === 'Upload')
const tweakSidebarOpen = computed(() => activeItem.value === 'Tweak')
const metadataSidebarOpen = computed(() => activeItem.value === 'Metadata')
const layerSidebarOpen = computed(() => activeItem.value === 'Layer')
const attributeSidebarOpen = computed(() => activeItem.value === 'Attribute')

const handleMenuClick = (title: MenuItem) => {
  if (activeItem.value === title) {
    activeItem.value = null;
  } else {
    activeItem.value = title;
  }
}
</script>