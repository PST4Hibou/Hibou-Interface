import { useApi } from '~/composables/useApi'
import type { SystemSettings } from '~/types/settings'
import type { UserListItem } from '~/types/users'

export function useSettingsRepository() {
  const { authenticatedFetch } = useApi()

  return {
    listUsers() {
      return authenticatedFetch<UserListItem[]>('/settings/users', { method: 'GET' })
    },

    getSystem() {
      return authenticatedFetch<SystemSettings>('/settings/system', { method: 'GET' })
    },

    updateSystem(body: SystemSettings) {
      return authenticatedFetch<SystemSettings>('/settings/system', {
        method: 'PUT',
        body,
      })
    },
  }
}
