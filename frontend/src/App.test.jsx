import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from './App.jsx'

afterEach(() => vi.unstubAllGlobals())

describe('local readiness screen', () => {
  it('shows connected only when the API confirms database readiness', async () => {
    vi.stubGlobal('fetch', vi.fn().mockImplementation(async (url) => ({
      ok: true, status: 200,
      json: async () => url.endsWith('/profile/') ? { profile: null } : { status: 'ok', database: 'connected' },
    })))
    render(<App />)
    expect(screen.getByRole('button', { name: 'Checking…' })).toBeDisabled()
    expect(await screen.findByRole('heading', { name: 'About you' })).toBeInTheDocument()
  })

  it('distinguishes an unavailable database from an unreachable backend', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false, status: 503,
      json: async () => ({ status: 'unavailable', database: 'unavailable' }),
    }))
    render(<App />)
    expect(await screen.findByText('Database setup needed')).toBeInTheDocument()
    expect(screen.queryByText('Your connection is ready')).not.toBeInTheDocument()
  })

  it('preserves an actionable error and can retry after a network failure', async () => {
    const fetchMock = vi.fn()
      .mockRejectedValueOnce(new TypeError('Network unavailable'))
      .mockResolvedValueOnce({
        ok: true, status: 200,
        json: async () => ({ status: 'ok', database: 'connected' }),
      })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ profile: null }) })
    vi.stubGlobal('fetch', fetchMock)
    render(<App />)
    expect(await screen.findByText('Cannot reach the backend')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Check connection again' }))
    expect(await screen.findByRole('heading', { name: 'About you' })).toBeInTheDocument()
  })
})
