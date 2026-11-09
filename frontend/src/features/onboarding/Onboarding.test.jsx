import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import App from '../../App.jsx'

afterEach(() => vi.unstubAllGlobals())

function mockAPI({ existing = null, failSave = false } = {}) {
  let saved = existing
  const fetchMock = vi.fn(async (url, options = {}) => {
    let data
    let status = 200
    if (url.endsWith('/health/')) data = { status: 'ok', database: 'connected' }
    else if (url.includes('/overview/')) data = { income: '0.00', expenses: '0.00', remaining: '0.00', income_count: 0, expense_count: 0, essential: '0.00', optional: '0.00', categories: [] }
    else if (url.endsWith('/csrf/')) data = { csrf_token: 'masked-token' }
    else if (options.method === 'PUT') {
      if (failSave) { status = 400; data = { errors: { expected_monthly_income: ['Enter a valid amount.'] } } }
      else { saved = { ...JSON.parse(options.body), onboarding_completed_at: '2026-11-07T00:00:00Z' }; data = { profile: saved } }
    } else data = { profile: saved }
    return { ok: status === 200, status, json: async () => data }
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

async function start() {
  render(<App />)
  await screen.findByRole('heading', { name: 'About you' })
}

describe('single-user onboarding', () => {
  it('allows every question to be skipped and sends unknown money as null with CSRF', async () => {
    const fetchMock = mockAPI()
    await start()
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.click(screen.getByRole('button', { name: 'Save my starting point' }))
    expect(await screen.findByText("You're ready to begin.")).toBeInTheDocument()
    const [, options] = fetchMock.mock.calls.find(([, options]) => options?.method === 'PUT')
    expect(options.headers['X-CSRFToken']).toBe('masked-token')
    expect(JSON.parse(options.body).expected_monthly_income).toBeNull()
  })

  it('saves irregular income and zero estimates, reloads, and permits editing', async () => {
    mockAPI()
    await start()
    fireEvent.change(screen.getByLabelText('What should we call you?'), { target: { value: 'Alex' } })
    fireEvent.change(screen.getByLabelText('How do you receive income?'), { target: { value: 'freelance' } })
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.change(screen.getByLabelText('Approximate monthly income'), { target: { value: '0' } })
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.change(screen.getByLabelText('Any goals on your mind?'), { target: { value: 'A laptop' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save my starting point' }))
    expect(await screen.findByText('Welcome, Alex.')).toBeInTheDocument()
    expect(screen.getByText('A laptop')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Edit my starting point' }))
    expect(screen.getByLabelText('What should we call you?')).toHaveValue('Alex')
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    expect(screen.getByLabelText('Approximate monthly income')).toHaveValue(0)
    expect(screen.getByLabelText('Essential monthly expenses')).toHaveValue(null)
  })

  it('returns to the invalid field while preserving entered values after a server error', async () => {
    mockAPI({ failSave: true })
    await start()
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.change(screen.getByLabelText('Approximate monthly income'), { target: { value: '100' } })
    fireEvent.click(screen.getByRole('button', { name: 'Continue' }))
    fireEvent.click(screen.getByRole('button', { name: 'Save my starting point' }))
    expect(await screen.findByText('Enter a valid amount.')).toBeInTheDocument()
    expect(screen.getByLabelText('Approximate monthly income')).toHaveValue(100)
    expect(screen.getByLabelText('Approximate monthly income')).toHaveAttribute('aria-invalid', 'true')
  })

  it('opens an existing profile without onboarding and can cancel edits', async () => {
    mockAPI({ existing: { nickname: 'Alex', goal_ideas: 'Travel', expected_monthly_income: '5000.00' } })
    render(<App />)
    fireEvent.click(await screen.findByRole('button', { name: 'Profile', exact: true }))
    expect(await screen.findByText('Welcome, Alex.')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Edit my starting point' }))
    fireEvent.change(screen.getByLabelText('What should we call you?'), { target: { value: 'Changed' } })
    fireEvent.click(screen.getByRole('button', { name: 'Cancel' }))
    expect(screen.getByText('Welcome, Alex.')).toBeInTheDocument()
  })

  it('reports a profile load failure instead of showing a blank new profile', async () => {
    vi.stubGlobal('fetch', vi.fn(async (url) => {
      if (url.endsWith('/health/')) return { ok: true, json: async () => ({ status: 'ok', database: 'connected' }) }
      throw new TypeError('Network unavailable')
    }))
    render(<App />)
    expect(await screen.findByText('Could not load your profile')).toBeInTheDocument()
    expect(screen.queryByRole('heading', { name: 'About you' })).not.toBeInTheDocument()
  })
})
