<template>
  <div class="p-8 space-y-6">
    <h1 class="text-xl font-semibold tracking-tight">
      {{ $t('settings.title') }}
    </h1>

    <Tabs default-value="system">
      <TabsList>
        <TabsTrigger value="system">
          {{ $t('settings.tabs.system') }}
        </TabsTrigger>
        <TabsTrigger value="users">
          {{ $t('settings.tabs.users') }}
        </TabsTrigger>
      </TabsList>

      <TabsContent value="system" class="mt-4">
        <SettingsSystemPanel />
      </TabsContent>

      <TabsContent value="users" class="mt-4">
        <SettingsUsersPanel />
      </TabsContent>
    </Tabs>
  </div>
</template>

<script setup lang="ts">
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'

definePageMeta({
  middleware: ['auth'],
})
</script>
