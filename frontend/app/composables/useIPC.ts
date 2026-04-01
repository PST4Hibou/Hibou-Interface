import { createSharedComposable, useWebSocket } from '@vueuse/core'
import { eventsWebSocketUrl } from '~/utils/websocket'

const EVENTS_WS_PATH = '/events/ws'

type Subscriber = [(event: Event) => void, string]

const useSharedIPC = createSharedComposable(() => {
  const config = useRuntimeConfig()
  const userStore = useUserStore()
  const subscribers = ref<Subscriber[]>([])

  const url = computed(() => {
    const base = config.public.apiBase as string
    const token = userStore.accessToken
    if (!base?.trim() || !token) return ''
    return eventsWebSocketUrl(base, EVENTS_WS_PATH, token)
  })

  const ws = useWebSocket(url, {
    autoReconnect: {
      retries: Infinity,
      delay: 3000,
    },
    onConnected: () => console.log('connected'),
    onError: (ws, event) => console.error('WebSocket error', event),
    onMessage: (_ws, event) => {
      subscribers.value.forEach((subscriber: Subscriber) => {
        const [callback, filter] = subscriber
        if (event.data.startsWith(filter)) {
          callback(event)
        }
      })
    },
  })

  const addSubscriber = (callback: (event: Event) => void, filter: string = '') => {
    subscribers.value.push([callback, filter])
  }

  return { ...ws, addSubscriber }
})

export function useIPC() {
  return useSharedIPC()
}
