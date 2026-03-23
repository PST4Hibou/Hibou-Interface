export default defineNuxtRouteMiddleware(async () => {
  if (import.meta.server) return
  const userStore = useUserStore()
  await userStore.initializeSession()

  if (!userStore.isAuthenticated) {
    const localePath = useLocalePath()
    return navigateTo(localePath('/'))
  }
})
