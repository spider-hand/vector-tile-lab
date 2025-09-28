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
    <TuneSidebar :open="tuneSidebarOpen" @update:open="(value) => tuneSidebarOpen = value" />
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
import TuneSidebar from '@/components/TuneSidebar.vue';
import { FlaskConical, Upload } from 'lucide-vue-next';


const items = [
  { title: 'Upload', icon: Upload },
  { title: 'Tune', icon: FlaskConical },
]

const uploadSidebarOpen = ref(false)
const tuneSidebarOpen = ref(false)

function handleMenuClick(title: string) {
  switch (title) {
    case 'Upload':
      uploadSidebarOpen.value = !uploadSidebarOpen.value
      tuneSidebarOpen.value = false
      break
    case 'Tune':
      tuneSidebarOpen.value = !tuneSidebarOpen.value
      uploadSidebarOpen.value = false
      break
    default:
      break
  }
}
</script>