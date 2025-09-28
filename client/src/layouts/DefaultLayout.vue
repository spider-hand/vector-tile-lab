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
                <SidebarMenuButton @click="handleMenuClick(item.title)">
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

    <UploadSidebar :open="uploadSidebarOpen" @update:open="(value) => uploadSidebarOpen = value" />
    <MetadataSidebar :open="metadataSidebarOpen" @update:open="(value) => metadataSidebarOpen = value" />
    <PerformanceSidebar :open="performanceSidebarOpen" @update:open="(value) => performanceSidebarOpen = value" />
  </SidebarProvider>
</template>

<script setup lang="ts">
import { ref } from 'vue'
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
import { ChartSpline, FileText, Upload } from 'lucide-vue-next';


const items = [
  { title: 'Upload', icon: Upload },
  { title: 'Metadata', icon: FileText },
  { title: 'Performance', icon: ChartSpline }
]

const uploadSidebarOpen = ref(false)
const metadataSidebarOpen = ref(false)
const performanceSidebarOpen = ref(false)

function handleMenuClick(title: string) {
  switch (title) {
    case 'Upload':
      uploadSidebarOpen.value = !uploadSidebarOpen.value
      metadataSidebarOpen.value = false
      performanceSidebarOpen.value = false
      break
    case 'Metadata':
      metadataSidebarOpen.value = !metadataSidebarOpen.value
      uploadSidebarOpen.value = false
      performanceSidebarOpen.value = false
      break
    case 'Performance':
      performanceSidebarOpen.value = !performanceSidebarOpen.value
      uploadSidebarOpen.value = false
      metadataSidebarOpen.value = false
    default:
      break
  }
}
</script>