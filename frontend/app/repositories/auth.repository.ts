import { useApi } from '~/composables/useApi'
import type { AccessTokenResponse, TokenResponse, User } from '~/types/auth'

export function useAuthRepository() {
  const { apiFetch, authenticatedFetch } = useApi()

  return {
    login(identifier: string, password: string) {
      return apiFetch<TokenResponse>('/auth/login', {
        method: 'POST',
        body: { identifier, password },
      })
    },

    refreshAccessToken() {
      return apiFetch<AccessTokenResponse>('/auth/refresh', {
        method: 'POST',
      })
    },

    fetchMe() {
      return authenticatedFetch<User>('/auth/me', { method: 'GET' })
    },

    logout() {
      return apiFetch('/auth/logout', { method: 'POST' })
    },
  }
}
