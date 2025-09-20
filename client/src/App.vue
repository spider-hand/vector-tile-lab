<template>
  <Toaster />
  <RouterView />
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import { Toaster } from './components/ui/sonner';
</script>
