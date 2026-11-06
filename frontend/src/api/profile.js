const base = (import.meta.env.VITE_API_BASE_URL || '/api/v1').replace(/\/$/, '')

async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${base}/${path}/`, { credentials: 'same-origin', ...options })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new Error('Cannot connect. Check that the backend is running, then try again.')
  }
  let data
  try { data = await response.json() } catch {
    throw new Error('The request could not be completed. Refresh the page and try again.')
  }
  if (!response.ok) {
    const error = new Error(data.message || 'Please check the highlighted fields and try again.')
    error.fields = data.errors || {}
    throw error
  }
  return data
}

export async function getProfile(signal) {
  return (await request('profile', { signal })).profile
}

export async function saveProfile(profile) {
  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), 12000)
  try {
    const { csrf_token: token } = await request('csrf', { signal: controller.signal })
    return (await request('profile', {
      method: 'PUT', signal: controller.signal,
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': token },
      body: JSON.stringify(profile),
    })).profile
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('Saving took too long. Your entries are still here; please try again.')
    throw error
  } finally { window.clearTimeout(timeout) }
}
