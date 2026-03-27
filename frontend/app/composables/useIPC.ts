import { useWebSocket} from '@vueuse/core'

function eventsWebSocketUrl(apiBase: string, wsPath: string): string {
  const u = new URL(apiBase)
  u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'
  u.pathname = wsPath
  u.search = ''
  u.hash = ''
  return u.toString()
}

const EVENTS_WS_PATH = '/events/ws'

type Subscriber = [(event: Event) => void, string]
const subscribers = ref<Subscriber[]>([])
let wsInstance: ReturnType<typeof useWebSocket> | null = null

export function useIPC() {
  const config = useRuntimeConfig()

  const addSubscriber = (callback: (event: Event) => void, filter: string = '') => {
    subscribers.value.push([callback, filter])
  }

  if (!wsInstance) {
    wsInstance = useWebSocket(eventsWebSocketUrl(config.public.apiBase as string, EVENTS_WS_PATH), {
      autoReconnect: true,
      onConnected: () => console.log('connected'),
      onDisconnected: () => wsInstance = null,
      onError: (ws, event) => console.error('WebSocket error', event),
      onMessage: (ws, event) => {
        subscribers.value.forEach((subscriber: Subscriber) => {
          const [callback, filter] = subscriber
          if (event.data.startsWith(filter)) {
            callback(event)
          }
        })
      },
    })
  }

  return { ...wsInstance, addSubscriber }
}