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
        class="absolute right-4 top-4 h-8 w-8 bg-primary rounded z-10 cursor-pointer flex items-center justify-center"
        @click="refreshMap"
      >
        <RefreshCwIcon class="size-4 text-primary-foreground" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import mapboxgl from 'mapbox-gl'
import 'mapbox-gl/dist/mapbox-gl.css'
import { useResizeObserver } from '@vueuse/core'
import { useSettingsRepository } from '~/repositories/settings.repository'
import type { SystemSettings } from '~/types/settings'
import { RefreshCwIcon } from 'lucide-vue-next'

const settingsRepo = useSettingsRepository()
const config = useRuntimeConfig()
const CENTER_SOURCE_ID = 'system-center'
const CENTER_LAYER_ID = 'system-center-circle'

const mapContainer = useTemplateRef<HTMLDivElement>('mapContainer')
const mapInstance = shallowRef<mapboxgl.Map | null>(null)

function clearCenterCircleData(map: mapboxgl.Map) {
  const src = map.getSource(CENTER_SOURCE_ID) as mapboxgl.GeoJSONSource | undefined
  if (src) {
    src.setData({ type: 'FeatureCollection', features: [] })
  }
}

function ensureCenterCircleLayer(map: mapboxgl.Map) {
  if (map.getSource(CENTER_SOURCE_ID)) return
  map.addSource(CENTER_SOURCE_ID, {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
  })
  map.addLayer({
    id: CENTER_LAYER_ID,
    type: 'circle',
    source: CENTER_SOURCE_ID,
    paint: {
      'circle-radius': 10,
      'circle-color': '#f43f5e',
      'circle-opacity': 0.92,
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
    },
  })
}

function setCenterCircle(map: mapboxgl.Map, lng: number, lat: number) {
  ensureCenterCircleLayer(map)
  const src = map.getSource(CENTER_SOURCE_ID) as mapboxgl.GeoJSONSource
  src.setData({
    type: 'Feature',
    geometry: { type: 'Point', coordinates: [lng, lat] },
    properties: {},
  })
}

function syncCenterCircle() {
  const map = mapInstance.value
  if (!map?.isStyleLoaded()) return

  if (
    !settings.value ||
    settings.value.latitude === undefined ||
    settings.value.longitude === undefined ||
    settings.value.map_zoom === undefined
  ) {
    clearCenterCircleData(map)
    return
  }
  setCenterCircle(map, settings.value.longitude, settings.value.latitude)
}

const hasToken = computed(() => {
  const t = config.public.mapboxAccessToken
  return typeof t === 'string' && t.length > 0
})

const { data: settings, pending: isLoading } = await useAsyncData<SystemSettings>(
  'settings-users',
  () => settingsRepo.getSystem()
)

const refreshMap = () => {
  if (!hasToken.value) return
  if (isLoading.value) return
  if (!settings.value) return
  if (
    settings.value.latitude === undefined ||
    settings.value.longitude === undefined ||
    settings.value.map_zoom === undefined
  ) {
    const map = mapInstance.value
    if (map) syncCenterCircle()
    return
  }
  const map = mapInstance.value
  const { latitude: lat, longitude: lng, map_zoom: zoom } = settings.value
  map?.setCenter({ lng, lat })
  map?.setZoom(zoom)
  syncCenterCircle()
}
watch([settings, mapInstance], refreshMap, { immediate: true })

onMounted(() => {
  if (!hasToken.value) return
  const el = mapContainer.value
  if (!el) return

  mapboxgl.accessToken = config.public.mapboxAccessToken as string
  const map = new mapboxgl.Map({
    container: el,
    style: 'mapbox://styles/mapbox/satellite-v9',
    center: [2.3522, 48.8566],
    zoom: 10,
  })
  mapInstance.value = map

  map.on('load', () => {
    syncCenterCircle()
  })

  nextTick(() => {
    requestAnimationFrame(() => map.resize())
  })
})

useResizeObserver(mapContainer, () => {
  mapInstance.value?.resize()
})

onBeforeUnmount(() => {
  mapInstance.value?.remove()
  mapInstance.value = null
})
</script>
