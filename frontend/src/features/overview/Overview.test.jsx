import { fireEvent, render, screen } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import App from '../../App.jsx'
import Overview from './Overview.jsx'
import { money } from '../../lib/format.js'

afterEach(() => vi.unstubAllGlobals())

it('uses recorded totals and allows income/expense navigation', async () => {
  const navigate = vi.fn()
  vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, json: async () => ({ income: '500.00', expenses: '200.25', remaining: '299.75', income_count: 1, expense_count: 2, essential: '150.00', optional: '50.25', categories: [{ id: 1, name: 'Groceries', total: '150.00' }] }) })))
  render(<Overview nickname="Alex" onNavigate={navigate} />)
  expect(await screen.findByText(money('299.75'))).toBeInTheDocument()
  expect(screen.getByText('Groceries')).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Record an expense' }))
  expect(navigate).toHaveBeenCalledWith('expenses')
})

it('shows supportive guidance for negative recorded remainders', async () => {
  vi.stubGlobal('fetch', vi.fn(async () => ({ ok: true, json: async () => ({ income: '0.00', expenses: '50.00', remaining: '-50.00', income_count: 0, expense_count: 1, essential: '50.00', optional: '0.00', categories: [] }) })))
  render(<Overview onNavigate={vi.fn()} />)
  expect(await screen.findByText(/There is no penalty for covering your needs/)).toBeInTheDocument()
})

it('opens the app on Overview with clear routes to entries and a separate Profile', async () => {
  vi.stubGlobal('fetch', vi.fn(async (url) => {
    let data
    if (url.endsWith('/health/')) data = { status: 'ok', database: 'connected' }
    else if (url.endsWith('/profile/')) data = { profile: { nickname: 'Alex', expected_monthly_income: '99999.00' } }
    else if (url.includes('/overview/')) data = { income: '0.00', expenses: '0.00', remaining: '0.00', income_count: 0, expense_count: 0, categories: [] }
    else if (url.includes('/income/')) data = { results: [], total: '0.00', count: 0, page: 1, pages: 1 }
    else if (url.includes('/expense-categories/')) data = { results: [{ id: 1, name: 'Food', default_essential: true, is_archived: false }] }
    else data = { results: [], total: '0.00', essential: '0.00', optional: '0.00', count: 0, page: 1, pages: 1, categories: [] }
    return { ok: true, json: async () => data }
  }))
  render(<App />)
  expect(await screen.findByRole('heading', { name: 'Your overview, Alex' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Overview', exact: true })).toHaveAttribute('aria-current', 'page')
  expect(screen.queryByText(money('99999.00'))).not.toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Record income' }))
  expect(await screen.findByRole('heading', { name: 'Your income' })).toBeInTheDocument()
  fireEvent.click(screen.getByRole('button', { name: 'Expenses', exact: true }))
  expect(await screen.findByRole('heading', { name: 'Your expenses' })).toBeInTheDocument()
  expect(await screen.findByRole('button', { name: 'Add expense' })).toBeEnabled()
  fireEvent.click(screen.getByRole('button', { name: 'Profile', exact: true }))
  expect(screen.getByText('Monthly income estimate')).toBeInTheDocument()
})

it('shows a load error without invented zero totals', async () => {
  vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Offline')))
  render(<Overview onNavigate={vi.fn()} />)
  expect(await screen.findByRole('alert')).toBeInTheDocument()
  expect(screen.queryByText(money('0.00'))).not.toBeInTheDocument()
})
