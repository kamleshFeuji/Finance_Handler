import { afterEach, expect, it, vi } from 'vitest'
import { deleteIncome, saveIncome } from './income.js'

afterEach(() => vi.unstubAllGlobals())

it('sends a masked CSRF token and the creation key on POST', async () => {
  const fetch = vi.fn(async (url) => ({ ok: true, json: async () => url.endsWith('/csrf/') ? { csrf_token: 'masked' } : { entry: { id: 1 } } }))
  vi.stubGlobal('fetch', fetch)
  await saveIncome({ amount: '25.50', request_key: 'stable-key' }, null)
  expect(fetch).toHaveBeenLastCalledWith('/api/v1/income/', expect.objectContaining({
    method: 'POST', credentials: 'same-origin',
    headers: expect.objectContaining({ 'X-CSRFToken': 'masked' }),
    body: JSON.stringify({ amount: '25.50', request_key: 'stable-key' }),
  }))
})

it('includes the current version in CSRF-protected DELETE', async () => {
  const fetch = vi.fn(async (url) => ({ ok: true, json: async () => url.endsWith('/csrf/') ? { csrf_token: 'masked' } : { message: 'Deleted' } }))
  vi.stubGlobal('fetch', fetch)
  await deleteIncome({ id: 4, version: 3 })
  expect(fetch).toHaveBeenLastCalledWith('/api/v1/income/4/', expect.objectContaining({ method: 'DELETE', body: '{"expected_version":3}' }))
})
