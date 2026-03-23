import { useApi } from '~/composables/useApi'
import type { AccessTokenResponse, TokenResponse, User } from '~/types/auth'

export const useUserStore = defineStore('user', {
  state: () => ({
    user: null as User | null,
    accessToken: null as string | null,
    initialized: false,
  }),

  getters: {
    isAuthenticated: (state) => state.user !== null && state.accessToken !== null,
  },

  actions: {
    async login(identifier: string, password: string) {
      const { apiFetch } = useApi()
      const body = await apiFetch<TokenResponse>('/auth/login', {
        method: 'POST',
        body: { identifier, password },
      })
      this.accessToken = body.access_token
      this.user = body.user
    },

    async refreshAccessToken() {
      const { apiFetch } = useApi()
      try {
        const body = await apiFetch<AccessTokenResponse>('/auth/refresh', {
          method: 'POST',
        })
        this.accessToken = body.access_token
      } catch {
        this.accessToken = null
        this.user = null
      }
    },

    async fetchMe() {
      if (!this.accessToken) return
      const { authenticatedFetch } = useApi()
      try {
        this.user = await authenticatedFetch<User>('/auth/me', { method: 'GET' })
      } catch {
        this.user = null
        this.accessToken = null
      }
    },

    async logout() {
      const { apiFetch } = useApi()
      try {
        await apiFetch('/auth/logout', { method: 'POST' })
      } finally {
        this.user = null
        this.accessToken = null
      }
    },

    async initializeSession() {
      if (this.initialized) return
      await this.refreshAccessToken()
      if (this.accessToken) {
        await this.fetchMe()
      }
      this.initialized = true
    },
  },
})
