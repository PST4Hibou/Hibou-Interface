<script setup lang="ts">
import { Toaster } from '@/components/ui/sonner'

const { isDark } = useAppTheme()

const toastTheme = computed(() => (isDark.value ? 'dark' : 'light'))

useHead({
  meta: [
    {
      name: 'color-scheme',
      content: computed(() => (isDark.value ? 'dark' : 'light')),
    },
  ],
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
  <Toaster :theme="toastTheme" />
</template>
