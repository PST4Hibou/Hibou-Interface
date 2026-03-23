<template>
  <CardContent>
    <form class="space-y-6" @submit="onSubmit">
      <div class="space-y-2">
        <FormField v-slot="{ componentField }" name="identifier">
          <FormItem>
            <FormLabel>
              {{ t('login.identifier') }}
            </FormLabel>
            <FormControl>
              <Input
                v-bind="componentField"
                name="identifier"
                type="text"
                autocomplete="username"
                :placeholder="t('login.identifierPlaceholder')"
                required
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <div class="space-y-2">
        <FormField v-slot="{ componentField }" name="password">
          <FormItem>
            <FormLabel>
              {{ t('login.password') }}
            </FormLabel>
            <FormControl>
              <Input
                v-bind="componentField"
                name="password"
                type="password"
                autocomplete="current-password"
                :placeholder="t('login.passwordPlaceholder')"
                required
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
      </div>

      <p v-if="loginError" role="alert" class="text-destructive text-sm">
        {{ loginError }}
      </p>

      <Button type="submit" class="w-full">
        {{ t('login.submit') }}
      </Button>
    </form>
  </CardContent>
</template>

<script setup lang="ts">
import { useUserStore } from '~/stores/user'
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import * as z from 'zod'

const { t } = useI18n()
const localePath = useLocalePath()
const userStore = useUserStore()
const loginSchema = z.object({
  identifier: z.string().min(3).max(255),
  password: z.string().min(8).max(128),
})
const schema = toTypedSchema(loginSchema)
const { handleSubmit } = useForm({
  validationSchema: schema,
  initialValues: {
    identifier: '',
    password: '',
  },
})

const loginError = ref<string | null>(null)

function fetchErrorStatus(e: unknown): number | undefined {
  if (e && typeof e === 'object') {
    const o = e as { statusCode?: number; status?: number }
    if (typeof o.statusCode === 'number') return o.statusCode
    if (typeof o.status === 'number') return o.status
  }
  return undefined
}

const onSubmit = handleSubmit(async (values: z.infer<typeof loginSchema>) => {
  loginError.value = null
  try {
    await userStore.login(values.identifier, values.password)
    await navigateTo(localePath('/dashboard'))
  } catch (e: unknown) {
    const status = fetchErrorStatus(e)
    loginError.value = status === 401 ? t('login.errorInvalid') : t('login.errorGeneric')
  }
})
</script>
