<template>
  <div class="flex min-h-dvh flex-col items-center justify-center px-4 py-12">
    <Card class="w-full max-w-sm">
      <div class="space-y-1 text-center">
        <h1 class="text-xl font-semibold tracking-tight">
          {{ t('brand') }}
        </h1>
        <p class="text-sm text-muted-foreground">
          {{ t('login.subtitle') }}
        </p>
      </div>

      <AuthForm />
    </Card>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'blank',
})

const { t } = useI18n()
</script>
