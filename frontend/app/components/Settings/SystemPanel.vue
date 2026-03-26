<template>
  <Card>
    <CardHeader>
      <CardTitle>{{ $t('settings.tabs.system') }}</CardTitle>
    </CardHeader>
    <CardContent class="space-y-8">
      <form class="space-y-8" novalidate @submit="onSubmit">
        <section class="space-y-4">
          <h2 class="text-sm font-medium leading-none">
            {{ $t('settings.system.gpsTitle') }}
          </h2>
          <div class="grid gap-4 sm:grid-cols-3">
            <FormField v-slot="{ componentField }" name="latitude">
              <FormItem>
                <FormLabel>
                  {{ $t('settings.system.latitude') }}
                </FormLabel>
                <FormControl>
                  <Input
                    v-bind="componentField"
                    type="number"
                    step="any"
                    inputmode="decimal"
                    autocomplete="off"
                    :disabled="isLoading"
                    :placeholder="$t('settings.system.latitudePlaceholder')"
                    class="font-mono tabular-nums"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
            <FormField v-slot="{ componentField }" name="longitude">
              <FormItem>
                <FormLabel>
                  {{ $t('settings.system.longitude') }}
                </FormLabel>
                <FormControl>
                  <Input
                    v-bind="componentField"
                    type="number"
                    step="any"
                    inputmode="decimal"
                    autocomplete="off"
                    :disabled="isLoading"
                    :placeholder="$t('settings.system.longitudePlaceholder')"
                    class="font-mono tabular-nums"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
            <FormField v-slot="{ componentField }" name="angleFromLongitude">
              <FormItem>
                <FormLabel>
                  {{ $t('settings.system.angleFromLongitude') }}
                </FormLabel>
                <FormControl>
                  <Input
                    v-bind="componentField"
                    type="number"
                    step="any"
                    inputmode="decimal"
                    autocomplete="off"
                    :disabled="isLoading"
                    :placeholder="$t('settings.system.anglePlaceholder')"
                    class="font-mono tabular-nums"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>
        </section>
        <section class="space-y-4">
          <h3 class="text-sm font-medium leading-none">
            {{ $t('settings.map.title') }}
          </h3>
          <div class="grid gap-4 sm:grid-cols-3">
            <FormField v-slot="{ componentField }" name="mapboxStyle">
              <FormItem>
                <FormLabel>
                  {{ $t('settings.map.styleLabel') }}
                </FormLabel>
                <Select v-bind="componentField" :disabled="isLoading">
                  <FormControl>
                    <SelectTrigger class="w-full">
                      <SelectValue :placeholder="$t('settings.map.stylePlaceholder')" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem
                      v-for="id in MAPBOX_STYLE_IDS"
                      :key="id"
                      :value="id"
                    >
                      {{ $t(`settings.map.styleOptions.${id}`) }}
                    </SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            </FormField>
            <FormField v-slot="{ componentField }" name="mapZoom">
              <FormItem>
                <FormLabel>
                  {{ $t('settings.map.zoomLabel') }}
                </FormLabel>
                <FormControl>
                  <Input
                    v-bind="componentField"
                    type="number"
                    autocomplete="off"
                    :disabled="isLoading"
                    :placeholder="$t('settings.map.zoomPlaceholder')"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
            <FormField v-slot="{ componentField }" name="mapPitch">
              <FormItem>
                <FormLabel>
                  {{ $t('settings.map.pitchLabel') }}
                </FormLabel>
                <FormControl>
                  <Input
                    v-bind="componentField"
                    type="number"
                    step="any"
                    inputmode="decimal"
                    autocomplete="off"
                    :disabled="isLoading"
                    :placeholder="$t('settings.map.pitchPlaceholder')"
                    class="font-mono tabular-nums"
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            </FormField>
            <FormField v-slot="{ value, handleChange }" name="map3dBuildings">
              <FormItem class="flex flex-row items-center gap-3 space-y-0 sm:col-span-3">
                <FormControl>
                  <Checkbox
                    :model-value="value"
                    :disabled="isLoading"
                    @update:model-value="(v) => handleChange(v === true)"
                  />
                </FormControl>
                <FormLabel class="cursor-pointer font-normal !mt-0">
                  {{ $t('settings.map.buildings3dLabel') }}
                </FormLabel>
                <FormMessage />
              </FormItem>
            </FormField>
          </div>
        </section>
        <Button type="submit" :disabled="isLoading">
          {{ $t('settings.save') }}
        </Button>
      </form>
    </CardContent>
  </Card>
</template>

<script setup lang="ts">
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { toast } from 'vue-sonner'
import { MAPBOX_STYLE_IDS, isMapboxStyleId } from '~/lib/mapboxStyles'
import { useSettingsRepository } from '~/repositories/settings.repository'
import type { SystemSettings } from '~/types/settings'

const { t } = useI18n()
const settingsRepo = useSettingsRepository()

function toFiniteOrZero(v: unknown): number {
  if (typeof v === 'number' && Number.isFinite(v)) return v
  return 0
}

const systemFormSchema = z.object({
  latitude: z.preprocess(toFiniteOrZero, z.number().min(-90).max(90)),
  longitude: z.preprocess(toFiniteOrZero, z.number().min(-180).max(180)),
  angleFromLongitude: z.preprocess(toFiniteOrZero, z.number().min(0).max(360)),
  mapboxStyle: z.enum(MAPBOX_STYLE_IDS),
  mapZoom: z.number().min(0).max(100),
  mapPitch: z.preprocess(toFiniteOrZero, z.number().min(0).max(85)),
  map3dBuildings: z.boolean(),
})

const schema = toTypedSchema(systemFormSchema)

const { handleSubmit, resetForm } = useForm({
  validationSchema: schema,
  initialValues: {
    latitude: 0,
    longitude: 0,
    angleFromLongitude: 0,
    mapboxStyle: 'satellite',
    mapZoom: 0,
    mapPitch: 0,
    map3dBuildings: false,
  },
})

const DEFAULT_FORM = {
  latitude: 0,
  longitude: 0,
  angleFromLongitude: 0,
  mapboxStyle: 'satellite',
  mapZoom: 10,
  mapPitch: 0,
  map3dBuildings: false,
} as const

function systemToFormValues(data: SystemSettings) {
  const styleId = data.mapbox_style
  return {
    latitude: toFiniteOrZero(data.latitude),
    longitude: toFiniteOrZero(data.longitude),
    angleFromLongitude: toFiniteOrZero(data.angle_from_longitude),
    mapboxStyle: styleId && isMapboxStyleId(styleId) ? styleId : 'satellite',
    mapZoom: toFiniteOrZero(data.map_zoom),
    mapPitch: toFiniteOrZero(data.map_pitch),
    map3dBuildings: data.map_3d_buildings === true,
  }
}

const isLoading = ref(false)

onMounted(async () => {
  isLoading.value = true
  try {
    const data = await settingsRepo.getSystem()
    resetForm({ values: systemToFormValues(data) })
  } catch {
    resetForm({ values: { ...DEFAULT_FORM } })
  } finally {
    isLoading.value = false
  }
})

const onSubmit = handleSubmit(async (values) => {
  isLoading.value = true
  try {
    const data = await settingsRepo.updateSystem({
      latitude: values.latitude,
      longitude: values.longitude,
      angle_from_longitude: values.angleFromLongitude,
      map_zoom: values.mapZoom,
      map_pitch: values.mapPitch,
      map_3d_buildings: values.map3dBuildings,
      mapbox_style: values.mapboxStyle,
    })
    resetForm({ values: systemToFormValues(data) })
    await refreshNuxtData('settings-users')
    toast.success(t('settings.saved'))
  } catch {
    toast.error(t('settings.saveError'))
  } finally {
    isLoading.value = false
  }
})
</script>
