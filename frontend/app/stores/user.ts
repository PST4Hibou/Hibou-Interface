import { useAuthRepository } from '~/repositories/auth.repository'
import type { User } from '~/types/auth'

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
      const auth = useAuthRepository()
      const body = await auth.login(identifier, password)
      this.accessToken = body.access_token
      this.user = body.user
    },

    async refreshAccessToken() {
      const auth = useAuthRepository()
      try {
        const body = await auth.refreshAccessToken()
        this.accessToken = body.access_token
      } catch {
        this.accessToken = null
        this.user = null
      }
    },

    async fetchMe() {
      if (!this.accessToken) return
      const auth = useAuthRepository()
      try {
        this.user = await auth.fetchMe()
      } catch {
        this.user = null
        this.accessToken = null
      }
    },

    async logout() {
      const auth = useAuthRepository()
      try {
        await auth.logout()
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
