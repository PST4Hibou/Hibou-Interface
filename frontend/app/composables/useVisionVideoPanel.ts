import { useWebSocket } from '@vueuse/core'
import { eventsWebSocketUrl } from '~/utils/websocket'

export const VISION_CH_RAW = 0
export const VISION_CH_ANNOTATED = 1

const VISION_STREAM_WS_PATH = '/video/stream-ws'

export function useVisionVideoPanel(wsPath: string = VISION_STREAM_WS_PATH) {
  const config = useRuntimeConfig()
  const userStore = useUserStore()

  const activeChannel = ref(VISION_CH_ANNOTATED)
  const streamError = ref(false)

  let annotatedObjectUrl: string | null = null
  const annotatedSrc = ref<string | null>(null)

  const ptzMjpegUrl = computed(() => {
    const base = config.public.apiBase as string | undefined
    const token = userStore.accessToken
    if (!base?.trim() || !token) return null
    const u = new URL('/video/ptz-mjpeg', base.endsWith('/') ? base : `${base}/`)
    u.searchParams.set('token', token)
    return u.toString()
  })

  const displaySrc = computed(() =>
    activeChannel.value === VISION_CH_RAW ? ptzMjpegUrl.value : annotatedSrc.value
  )

  const displayKey = computed(() =>
    activeChannel.value === VISION_CH_RAW ? `raw|${ptzMjpegUrl.value ?? ''}` : 'annotated'
  )

  /** Raw: overlay while unauthenticated. Annotated: overlay until first WebSocket frame. Either: decode error. */
  const showVideoOverlay = computed(
    () =>
      streamError.value ||
      (activeChannel.value === VISION_CH_ANNOTATED && !annotatedSrc.value) ||
      (activeChannel.value === VISION_CH_RAW && !ptzMjpegUrl.value)
  )

  function setAnnotatedFromBlob(blob: Blob) {
    if (annotatedObjectUrl) {
      URL.revokeObjectURL(annotatedObjectUrl)
      annotatedObjectUrl = null
    }
    annotatedObjectUrl = URL.createObjectURL(blob)
    annotatedSrc.value = annotatedObjectUrl
  }

  async function handleVisionMessage(data: unknown) {
    let ab: ArrayBuffer
    if (typeof Blob !== 'undefined' && data instanceof Blob) {
      ab = await data.arrayBuffer()
    } else if (data instanceof ArrayBuffer) {
      ab = data
    } else {
      return
    }
    if (ab.byteLength < 2) return
    setAnnotatedFromBlob(new Blob([ab], { type: 'image/jpeg' }))
  }

  const visionWsUrl = computed(() => {
    const base = config.public.apiBase as string
    const token = userStore.accessToken
    if (!base?.trim() || !token) return ''
    return eventsWebSocketUrl(base, wsPath, token)
  })

  useWebSocket(visionWsUrl, {
    onMessage: (_ws, event) => {
      void handleVisionMessage(event.data)
    },
    onError: (_ws, evt) => {
      console.error('[vision] error', evt)
    },
    autoReconnect: {
      retries: Infinity,
      delay: 3000,
    },
  })

  watch(activeChannel, () => {
    streamError.value = false
  })

  watch(
    () => userStore.accessToken,
    () => {
      streamError.value = false
    }
  )

  onBeforeUnmount(() => {
    if (annotatedObjectUrl) {
      URL.revokeObjectURL(annotatedObjectUrl)
    }
  })

  return {
    VISION_CH_RAW,
    VISION_CH_ANNOTATED,
    activeChannel,
    streamError,
    ptzMjpegUrl,
    displaySrc,
    displayKey,
    showVideoOverlay,
  }
}
