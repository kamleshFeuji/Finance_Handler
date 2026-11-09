import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { deleteExpense, listCategories, listExpenses, saveCategory, saveExpense } from '../../api/expenses.js'
import ExpensePage from './ExpensePage.jsx'
import { money, today } from '../../lib/format.js'

vi.mock('../../api/expenses.js', () => ({ deleteExpense: vi.fn(), listCategories: vi.fn(), listExpenses: vi.fn(), saveCategory: vi.fn(), saveExpense: vi.fn() }))
const choices = [{ id: 1, name: 'Groceries', default_essential: true, is_archived: false, version: 1 }, { id: 2, name: 'Entertainment', default_essential: false, is_archived: false, version: 1 }]
const entry = { id: 5, amount: '100.25', category: 1, category_name: 'Groceries', is_essential: true, spent_on: today(), label: 'Weekly food', note: '', version: 1 }
const empty = { results: [], total: '0.00', essential: '0.00', optional: '0.00', count: 0, page: 1, pages: 1, categories: [] }
const populated = { ...empty, results: [entry], total: '100.25', essential: '100.25', count: 1 }
beforeEach(() => { vi.resetAllMocks(); listExpenses.mockResolvedValue(empty); listCategories.mockResolvedValue({ results: choices }) })
afterEach(() => vi.restoreAllMocks())

it('records a categorized expense and lets the user override suggested essential status', async () => {
  saveExpense.mockResolvedValue(entry)
  render(<ExpensePage />)
  await screen.findByText('No expenses recorded for this month')
  fireEvent.click(screen.getByRole('button', { name: 'Add expense' }))
  expect(screen.getByLabelText('Essential expense')).toBeChecked()
  fireEvent.change(screen.getByLabelText('Category'), { target: { value: '2' } })
  expect(screen.getByLabelText('Essential expense')).not.toBeChecked()
  fireEvent.click(screen.getByLabelText('Essential expense'))
  fireEvent.change(screen.getByLabelText('Expense amount (INR)'), { target: { value: '50.25' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save expense' }))
  expect(await screen.findByText('Expense saved.')).toBeInTheDocument()
  expect(saveExpense).toHaveBeenCalledWith(expect.objectContaining({ amount: '50.25', category: 2, is_essential: true, request_key: expect.any(String) }), null)
})

it('preserves input and submission key on a failed save', async () => {
  saveExpense.mockRejectedValueOnce(new Error('Offline')).mockResolvedValueOnce(entry)
  render(<ExpensePage />)
  await screen.findByText('No expenses recorded for this month')
  fireEvent.click(screen.getByRole('button', { name: 'Add expense' }))
  fireEvent.change(screen.getByLabelText('Expense amount (INR)'), { target: { value: '10' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save expense' }))
  await screen.findByText('Offline')
  expect(screen.getByLabelText('Expense amount (INR)')).toHaveValue(10)
  const key = saveExpense.mock.calls[0][0].request_key
  fireEvent.click(screen.getByRole('button', { name: 'Save expense' }))
  await screen.findByText('Expense saved.')
  expect(saveExpense.mock.calls[1][0].request_key).toBe(key)
})

it('edits an existing expense using its original version', async () => {
  listExpenses.mockResolvedValue(populated); saveExpense.mockResolvedValue({ ...entry, version: 2 })
  render(<ExpensePage />)
  fireEvent.click(await screen.findByRole('button', { name: 'Edit expense Weekly food' }))
  fireEvent.change(screen.getByLabelText('Expense amount (INR)'), { target: { value: '125' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save expense changes' }))
  await screen.findByText('Expense updated.')
  expect(saveExpense).toHaveBeenCalledWith(expect.objectContaining({ amount: '125', expected_version: 1 }), entry)
})

it('requires confirmation and reloads after deleting an expense', async () => {
  listExpenses.mockResolvedValueOnce(populated).mockResolvedValue(empty)
  vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true)
  deleteExpense.mockResolvedValue({})
  render(<ExpensePage />)
  fireEvent.click(await screen.findByRole('button', { name: 'Delete expense Weekly food' }))
  expect(deleteExpense).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button', { name: 'Delete expense Weekly food' }))
  await screen.findByText('Expense deleted.')
  expect(deleteExpense).toHaveBeenCalledWith(entry)
  await screen.findByText('No expenses recorded for this month')
})

it('adds custom categories and can archive or restore existing ones', async () => {
  saveCategory.mockResolvedValue({ id: 3 })
  render(<ExpensePage />)
  await screen.findByText('No expenses recorded for this month')
  fireEvent.click(screen.getByText('Manage expense categories'))
  fireEvent.change(screen.getByLabelText('New category name'), { target: { value: 'Pets' } })
  fireEvent.click(screen.getByRole('button', { name: 'Add category' }))
  await screen.findByText('Category added.')
  expect(saveCategory).toHaveBeenCalledWith({ name: 'Pets', default_essential: false }, undefined)
  await waitFor(() => expect(listExpenses).toHaveBeenCalledTimes(2))
  fireEvent.click(screen.getByText('Manage expense categories'))
  fireEvent.click(screen.getByRole('button', { name: 'Archive Groceries' }))
  await screen.findByText('Category updated.')
  expect(saveCategory).toHaveBeenLastCalledWith(expect.objectContaining({ is_archived: true, expected_version: 1 }), choices[0])
})

it('can edit entries that keep an archived category', async () => {
  listCategories.mockResolvedValue({ results: [{ ...choices[0], is_archived: true }] })
  listExpenses.mockResolvedValue(populated)
  render(<ExpensePage />)
  fireEvent.click(await screen.findByRole('button', { name: 'Edit expense Weekly food' }))
  expect(screen.getByRole('option', { name: 'Groceries (archived)' })).toBeInTheDocument()
  expect(screen.getByRole('button', { name: 'Save expense changes' })).toBeEnabled()
})

it('uses full-month server totals rather than summing a page', async () => {
  listExpenses.mockResolvedValue({ ...populated, total: '1000.00', essential: '900.00', optional: '100.00', count: 26, pages: 2 })
  render(<ExpensePage />)
  expect(await screen.findByText(money('1000.00'))).toBeInTheDocument()
  expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()
})

it('does not show zero balances when a request fails', async () => {
  listExpenses.mockRejectedValue(new Error('Database unavailable'))
  render(<ExpensePage />)
  await screen.findByText('Database unavailable')
  expect(screen.queryByText(money('0.00'))).not.toBeInTheDocument()
})
