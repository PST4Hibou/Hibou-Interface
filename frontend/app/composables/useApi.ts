export function useApi() {
  const config = useRuntimeConfig()
  const userStore = useUserStore()

  const apiFetch = $fetch.create({
    baseURL: config.public.apiBase as string,
    credentials: 'include',
  })

  async function authenticatedFetch<T>(
    path: string,
    options?: Parameters<typeof apiFetch>[1]
  ): Promise<T> {
    const base =
      options?.headers && typeof options.headers === 'object' && !Array.isArray(options.headers)
        ? (options.headers as Record<string, string>)
        : {}
    const withAuth = (accessToken: string) =>
      apiFetch<T>(path, {
        ...options,
        headers: { ...base, Authorization: `Bearer ${accessToken}` },
      })

    let token = userStore.accessToken
    if (!token) throw createError({ statusCode: 401, message: 'Not authenticated' })

    try {
      return await withAuth(token)
    } catch (e) {
      const status = (e as { statusCode?: number }).statusCode ?? (e as { status?: number }).status
      if (status !== 401) throw e
      await userStore.refreshAccessToken()
      token = userStore.accessToken
      if (!token) throw e
      return await withAuth(token)
    }
  }

  return { apiFetch, authenticatedFetch }
}
