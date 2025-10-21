<template>
  <SidebarProvider>
    <Sidebar style="

--sidebar-width: 10rem; --sidebar-width-mobile: 10rem;

 position: relative; z-index: 999;">
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem v-for="item in items" :key="item.title">
                <SidebarMenuButton @click="handleMenuClick(item.title)" :is-active="activeItem === item.title">
                  <component :is="item.icon" />
                  <span>{{ item.title }}</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
    <main>
      <router-view />
    </main>

    <UploadSidebar :open="uploadSidebarOpen" @update:open="handleMenuClick('Upload')" />
    <TilesetSidebar :open="tilesetSidebarOpen" @update:open="handleMenuClick('Tilesets')" />
    <MetadataSidebar :open="metadataSidebarOpen" @update:open="handleMenuClick('Metadata')" />
    <PerformanceSidebar :open="performanceSidebarOpen" @update:open="handleMenuClick('Performance')" />
    <ComparisonSidebar :open="comparisonSidebarOpen" @update:open="handleMenuClick('Comparison')" />
    <StyleSidebar :open="styleSidebarOpen" @update:open="handleMenuClick('Style')" />
  </SidebarProvider>
</template>

<script setup lang="ts">
import { computed, ref, type Component } from 'vue'
import Sidebar from '@/components/ui/sidebar/Sidebar.vue';
import SidebarContent from '@/components/ui/sidebar/SidebarContent.vue';
import SidebarGroup from '@/components/ui/sidebar/SidebarGroup.vue';
import SidebarGroupContent from '@/components/ui/sidebar/SidebarGroupContent.vue';
import SidebarMenu from '@/components/ui/sidebar/SidebarMenu.vue';
import SidebarMenuButton from '@/components/ui/sidebar/SidebarMenuButton.vue';
import SidebarMenuItem from '@/components/ui/sidebar/SidebarMenuItem.vue';
import SidebarProvider from '@/components/ui/sidebar/SidebarProvider.vue';
import UploadSidebar from '@/components/UploadSidebar.vue';
import MetadataSidebar from '@/components/MetadataSidebar.vue';
import PerformanceSidebar from '@/components/PerformanceSidebar.vue';
import { ChartNoAxesColumn, ChartSpline, FileText, Layers, Upload, WandSparkles } from 'lucide-vue-next';
import TilesetSidebar from '@/components/TilesetSidebar.vue';
import ComparisonSidebar from '@/components/ComparisonSidebar.vue';
import StyleSidebar from '@/components/StyleSidebar.vue';

type MenuItem = 'Upload' | 'Tilesets' | 'Metadata' | 'Performance' | 'Comparison' | 'Style';

const items: Array<{ title: MenuItem; icon: Component }> = [
  { title: 'Upload', icon: Upload },
  { title: 'Tilesets', icon: Layers },
  { title: 'Metadata', icon: FileText },
  { title: 'Performance', icon: ChartSpline },
  { title: 'Comparison', icon: ChartNoAxesColumn },
  { title: 'Style', icon: WandSparkles }
]

const activeItem = ref<MenuItem | null>(null)
const uploadSidebarOpen = computed(() => activeItem.value === 'Upload')
const tilesetSidebarOpen = computed(() => activeItem.value === 'Tilesets')
const metadataSidebarOpen = computed(() => activeItem.value === 'Metadata')
const performanceSidebarOpen = computed(() => activeItem.value === 'Performance')
const comparisonSidebarOpen = computed(() => activeItem.value === 'Comparison')
const styleSidebarOpen = computed(() => activeItem.value === 'Style')

function handleMenuClick(title: MenuItem) {
  if (activeItem.value === title) {
    activeItem.value = null;
  } else {
    activeItem.value = title;
  }
}
</script>