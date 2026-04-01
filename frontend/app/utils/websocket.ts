export function eventsWebSocketUrl(
  apiBase: string,
  wsPath: string,
  token?: string | null,
): string {
  const u = new URL(apiBase)
  u.protocol = u.protocol === 'https:' ? 'wss:' : 'ws:'
  u.pathname = wsPath
  u.hash = ''
  if (token?.trim()) {
    u.searchParams.set('token', token.trim())
  } else {
    u.search = ''
  }
  return u.toString()
}
