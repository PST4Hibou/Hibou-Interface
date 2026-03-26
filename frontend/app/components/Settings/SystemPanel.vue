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
import { Input } from '@/components/ui/input'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'
import { toast } from 'vue-sonner'
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
  mapZoom: z.number().min(0).max(100),
})

const schema = toTypedSchema(systemFormSchema)

const { handleSubmit, resetForm } = useForm({
  validationSchema: schema,
  initialValues: {
    latitude: 0,
    longitude: 0,
    angleFromLongitude: 0,
    mapZoom: 0,
  },
})

const DEFAULT_FORM = {
  latitude: 0,
  longitude: 0,
  angleFromLongitude: 0,
  mapZoom: 10,
} as const

function systemToFormValues(data: SystemSettings) {
  return {
    latitude: toFiniteOrZero(data.latitude),
    longitude: toFiniteOrZero(data.longitude),
    angleFromLongitude: toFiniteOrZero(data.angle_from_longitude),
    mapZoom: toFiniteOrZero(data.map_zoom),
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
    })
    resetForm({ values: systemToFormValues(data) })
    toast.success(t('settings.saved'))
  } catch {
    toast.error(t('settings.saveError'))
  } finally {
    isLoading.value = false
  }
})
</script>
