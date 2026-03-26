<template>
  <div class="flex min-h-0 flex-1 flex-col">
    <div class="flex min-h-0 flex-1 gap-3 p-3">
      <div class="flex min-h-0 min-w-0 flex-1 flex-col">
        <DashboardVideoPanel />
      </div>
      <div class="flex min-h-0 min-w-0 flex-1 flex-col">
        <DashboardMapPanel />
      </div>
    </div>
    <div class="max-h-[45vh] shrink-0 overflow-y-auto border-t border-border">
      <div class="p-4">
        <h2 class="pb-4 text-2xl font-bold">System Status</h2>
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card v-for="status in systemStatus" :key="status.name">
            <CardHeader>
              <CardTitle class="flex justify-between">
                {{ status.name }}
                <NuxtLink v-if="status.link" :href="status.link" target="_blank" class="ml-2">
                  <ExternalLink class="size-4" />
                </NuxtLink>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div
                    class="size-2 rounded-full"
                    :class="status.status ? 'bg-green-500' : 'bg-red-500'"
                  ></div>
                </div>
                <div class="text-sm text-muted-foreground">
                  {{ status.status ? 'Online' : 'Offline' }}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        <Card class="mt-4 w-xl p-4">
          <h2 class="mb-2 text-lg font-semibold">Test event</h2>
          <Input v-model="event" type="text" placeholder="Test event" />
          <Button class="mt-2" :disabled="!ws" @click="ws?.send(event)">Send</Button>
        </Card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ExternalLink } from 'lucide-vue-next'

/** Same path as the FastAPI WebSocket route (`/events` router + `/ws`). */
const EVENTS_WS_PATH = '/events/ws'

definePageMeta({
  middleware: ['auth'],
})

const config = useRuntimeConfig()

const event = ref('')

const systemStatus = ref([
  {
    name: 'PTZ Camera',
    status: true,
    link: 'http://192.168.250.30',
  },
  {
    name: 'Yamaha Tio',
    status: false,
  },
  {
    name: 'Server',
    status: true,
  },
  {
    name: 'Je sais pas quoi',
    status: true,
  },
])

function eventsWebSocketUrl(apiBase: string, wsPath: string): string {
  const u = new URL(apiBase)
  u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'
  u.pathname = wsPath
  u.search = ''
  u.hash = ''
  return u.toString()
}

const ws = shallowRef<WebSocket | null>(null)

onMounted(() => {
  const socket = new WebSocket(eventsWebSocketUrl(config.public.apiBase as string, EVENTS_WS_PATH))
  socket.onmessage = (e) => {
    // console.log(e)
  }
  ws.value = socket
})

onBeforeUnmount(() => {
  ws.value?.close()
})
</script>
