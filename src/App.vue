<script setup>
import { RouterView } from 'vue-router'
import Toaster from '@/components/ui/toast/Toaster.vue'
</script>

<template>
  <RouterView v-slot="{ Component }">
      <component :is="Component" />
  </RouterView>
  <Toaster />
</template>