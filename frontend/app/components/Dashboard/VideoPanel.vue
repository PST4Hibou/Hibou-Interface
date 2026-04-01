<template>
  <div
    class="relative flex h-full min-h-0 w-full flex-col overflow-hidden rounded-lg border border-border bg-black/80"
  >
    <img
      v-show="frameSrc && !streamError"
      :src="frameSrc ?? undefined"
      class="h-full w-full object-contain"
      alt=""
      referrerpolicy="no-referrer"
      @error="streamError = true"
      @load="streamError = false"
    />
    <div
      v-if="!frameSrc || streamError"
      class="absolute inset-0 flex flex-col items-center justify-center bg-muted/30 p-6 text-center"
    >
      <p class="text-sm font-medium text-foreground">
        {{ $t('dashboard.videoTitle') }}
      </p>
      <p class="mt-1 max-w-sm text-sm text-muted-foreground">
        <template v-if="!frameSrc">
          {{ $t('dashboard.videoNeedToken') }}
        </template>
        <template v-else>
          {{ $t('dashboard.videoStreamFailed') }}
        </template>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useWebSocket } from '@vueuse/core'

const config = useRuntimeConfig()

const frameSrc = ref<string | null>(null)
const streamError = ref(false)
let frameObjectUrl: string | null = null

function setFrameFromBlob(blob: Blob) {
  if (frameObjectUrl) {
    URL.revokeObjectURL(frameObjectUrl)
    frameObjectUrl = null
  }
  frameObjectUrl = URL.createObjectURL(blob)
  frameSrc.value = frameObjectUrl
}

function eventsWebSocketUrl(apiBase: string, wsPath: string): string {
  const u = new URL(apiBase)
  u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'
  u.pathname = wsPath
  u.search = ''
  u.hash = ''
  return u.toString()
}

useWebSocket(eventsWebSocketUrl(config.public.apiBase as string, '/video/stream-ws'), {
  onMessage: (_ws, event) => {
    const data = event.data
    if (typeof Blob !== 'undefined' && data instanceof Blob) {
      setFrameFromBlob(data)
    } else if (data instanceof ArrayBuffer) {
      setFrameFromBlob(new Blob([data], { type: 'image/jpeg' }))
    }
  },
  onError: (_ws, evt) => {
    console.error('[vision] error', evt)
  },
  autoReconnect: true,
})

onBeforeUnmount(() => {
  if (frameObjectUrl) {
    URL.revokeObjectURL(frameObjectUrl)
  }
})
</script>
