<template>
  <div
    class="relative flex h-full min-h-0 w-full min-w-0 flex-col overflow-hidden rounded-lg border border-border bg-muted/30"
  >
    <div
      v-if="!hasToken"
      class="flex flex-1 items-center justify-center p-4 text-center text-sm text-muted-foreground"
    >
      {{ $t('dashboard.mapMissingToken') }}
    </div>
    <div v-else ref="mapContainer" class="h-full min-h-0 w-full flex-1">
      <div
        class="absolute right-4 top-4 z-10 flex h-8 w-8 cursor-pointer items-center justify-center rounded bg-primary"
        @click="refreshMap"
      >
        <RefreshCwIcon class="size-4 text-primary-foreground" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { RefreshCwIcon } from 'lucide-vue-next'
import { useSettingsRepository } from '~/repositories/settings.repository'
import type { SystemSettings } from '~/types/settings'

const settingsRepo = useSettingsRepository()
const config = useRuntimeConfig()

const mapContainer = useTemplateRef<HTMLDivElement>('mapContainer')

const hasToken = computed(() => {
  const t = config.public.mapboxAccessToken
  return typeof t === 'string' && t.length > 0
})

const accessToken = computed(() => config.public.mapboxAccessToken as string)

const { data: settings, pending: isLoading } = await useAsyncData<SystemSettings>(
  'settings-users',
  () => settingsRepo.getSystem()
)

const angle = ref(90)

const droneAngle = ref(10)
onMounted(() => {
  setInterval(() => {
    droneAngle.value = (droneAngle.value - 1) % 360
  }, 500)
})

const { syncFromSettings } = useMapboxSystemMap(mapContainer, {
  accessToken,
  enabled: hasToken,
  settings,
  bearingDeg: angle,
  droneBearingDeg: droneAngle,
})

const refreshMap = () => {
  if (!hasToken.value || isLoading.value || !settings.value) return
  syncFromSettings()
}

const { addSubscriber } = useIPC()
addSubscriber((event) => {
  let data = event.data.split(' ')[1]
  if (!data) return

  let [azimuth, elevation] = data.split(',')
  azimuth = parseFloat(azimuth) / 10
  // elevation = parseFloat(elevation) / 10
  angle.value = azimuth
}, 'vision_angle')
console.log()
</script>
