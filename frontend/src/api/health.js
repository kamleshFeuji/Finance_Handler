const apiBase = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

export async function getHealth(signal) {
  const response = await fetch(`${apiBase}/health/`, {
    credentials: 'same-origin',
    headers: { Accept: 'application/json' },
    signal,
  })
  const data = await response.json()
  if (response.status === 503 && data.database === 'unavailable') {
    return { state: 'database-unavailable' }
  }
  if (!response.ok || data.status !== 'ok' || data.database !== 'connected') {
    throw new Error('Unexpected readiness response')
  }
  return { state: 'connected' }
}
