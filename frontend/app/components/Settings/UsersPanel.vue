<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ $t('settings.tabs.users') }}</CardTitle>
      <CardDescription>
        {{ $t('settings.users.description') }}
      </CardDescription>
    </CardHeader>
    <CardContent>
      <div v-if="isLoading" class="space-y-3">
        <Skeleton class="h-10 w-full" />
        <Skeleton class="h-10 w-full" />
        <Skeleton class="h-10 w-full" />
      </div>
      <div v-else class="rounded-md border border-border">
        <Table>
          <TableHeader class="bg-muted/50">
            <TableRow>
              <TableHead class="px-3 text-muted-foreground">
                {{ $t('settings.users.columnId') }}
              </TableHead>
              <TableHead class="px-3 text-muted-foreground">
                {{ $t('settings.users.columnIdentifier') }}
              </TableHead>
              <TableHead class="px-3 text-muted-foreground">
                {{ $t('settings.users.columnCreatedAt') }}
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            <TableRow v-if="users.length === 0">
              <TableCell colspan="3" class="p-6 text-center text-muted-foreground whitespace-normal">
                {{ $t('settings.users.empty') }}
              </TableCell>
            </TableRow>
            <TableRow
              v-for="u in users"
              :key="u.id"
            >
              <TableCell class="px-3 font-mono tabular-nums">
                {{ u.id }}
              </TableCell>
              <TableCell class="px-3 whitespace-normal">
                {{ u.identifier }}
              </TableCell>
              <TableCell class="px-3 text-muted-foreground">
                {{ formatCreatedAt(u.created_at) }}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </div>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { useSettingsRepository } from '~/repositories/settings.repository'
import type { UserListItem } from '~/types/users'

const settingsRepo = useSettingsRepository()
const { locale } = useI18n()

const { data, pending: isLoading } = await useAsyncData<UserListItem[]>(
  'settings-users',
  () => settingsRepo.listUsers(),
  { default: () => [] },
)

const users = computed(() => data.value ?? [])

function formatCreatedAt(iso: string) {
  const d = new Date(iso)
  const localeTag = locale.value === 'fr' ? 'fr-FR' : 'en-US'
  return d.toLocaleString(localeTag, { dateStyle: 'medium', timeStyle: 'short' })
}
</script>
