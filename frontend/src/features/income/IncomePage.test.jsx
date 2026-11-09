import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { deleteIncome, listIncome, saveIncome } from '../../api/income.js'
import IncomePage from './IncomePage.jsx'
import { money, today } from './format.js'

vi.mock('../../api/income.js', () => ({ listIncome: vi.fn(), saveIncome: vi.fn(), deleteIncome: vi.fn() }))

const entry = { id: 5, amount: '100.25', source: 'freelance', label: 'Contract payment', received_on: today(), note: 'Fictional example', version: 3 }
const empty = { results: [], total: '0.00', count: 0, page: 1, pages: 1 }
const populated = { results: [entry], total: '100.25', count: 1, page: 1, pages: 1 }

beforeEach(() => { vi.resetAllMocks(); listIncome.mockResolvedValue(empty) })
afterEach(() => vi.restoreAllMocks())

describe('income entry and history', () => {
  it('shows the server total across all pages rather than summing the visible rows', async () => {
    listIncome.mockResolvedValue({ ...populated, total: '3000.00', count: 26, pages: 2 })
    render(<IncomePage />)
    expect(await screen.findByText(money('3000.00'))).toBeInTheDocument()
    expect(screen.getByText('26 entries')).toBeInTheDocument()
    expect(screen.getByText('Page 1 of 2')).toBeInTheDocument()
  })

  it('records income with a stable submission key and refreshes the month', async () => {
    listIncome.mockResolvedValueOnce(empty).mockResolvedValue(populated)
    saveIncome.mockResolvedValue(entry)
    render(<IncomePage />)
    await screen.findByText('No income recorded for this month')
    fireEvent.click(screen.getByRole('button', { name: 'Add income' }))
    fireEvent.change(screen.getByLabelText('Amount (INR)'), { target: { value: '100.25' } })
    fireEvent.change(screen.getByLabelText('Income source'), { target: { value: 'freelance' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save income' }))
    expect(await screen.findByText('Income saved.')).toBeInTheDocument()
    expect(await screen.findByText('Contract payment')).toBeInTheDocument()
    expect(saveIncome).toHaveBeenCalledWith(expect.objectContaining({ amount: '100.25', source: 'freelance', request_key: expect.any(String) }), null)
  })

  it('keeps entered values and the same submission key when retrying after a network error', async () => {
    saveIncome.mockRejectedValueOnce(new Error('Connection interrupted')).mockResolvedValueOnce(entry)
    render(<IncomePage />)
    await screen.findByText('No income recorded for this month')
    fireEvent.click(screen.getByRole('button', { name: 'Add income' }))
    fireEvent.change(screen.getByLabelText('Amount (INR)'), { target: { value: '100.25' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save income' }))
    expect(await screen.findByText('Connection interrupted')).toBeInTheDocument()
    expect(screen.getByLabelText('Amount (INR)')).toHaveValue(100.25)
    const originalKey = saveIncome.mock.calls[0][0].request_key
    fireEvent.click(screen.getByRole('button', { name: 'Save income' }))
    await screen.findByText('Income saved.')
    expect(saveIncome.mock.calls[1][0].request_key).toBe(originalKey)
  })

  it('edits using the original version and displays field errors without dropping input', async () => {
    listIncome.mockResolvedValue(populated)
    const failure = new Error('Check the amount')
    failure.fields = { amount: ['Enter a valid amount.'] }
    saveIncome.mockRejectedValueOnce(failure).mockResolvedValueOnce({ ...entry, version: 4 })
    render(<IncomePage />)
    await screen.findByText('Contract payment')
    fireEvent.click(screen.getByRole('button', { name: /^Edit Contract/ }))
    fireEvent.change(screen.getByLabelText('Amount (INR)'), { target: { value: '250' } })
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }))
    expect(await screen.findByText('Enter a valid amount.')).toBeInTheDocument()
    expect(screen.getByLabelText('Amount (INR)')).toHaveValue(250)
    expect(screen.getByLabelText('Amount (INR)')).toHaveAttribute('aria-invalid', 'true')
    expect(saveIncome).toHaveBeenCalledWith(expect.objectContaining({ amount: '250', expected_version: 3 }), entry)
    fireEvent.click(screen.getByRole('button', { name: 'Save changes' }))
    expect(await screen.findByText('Income updated.')).toBeInTheDocument()
  })

  it('requires confirmation before deletion and reloads totals after success', async () => {
    listIncome.mockResolvedValueOnce(populated).mockResolvedValue(empty)
    const confirm = vi.spyOn(window, 'confirm').mockReturnValueOnce(false).mockReturnValueOnce(true)
    deleteIncome.mockResolvedValue({ message: 'Income entry deleted.' })
    render(<IncomePage />)
    await screen.findByText('Contract payment')
    fireEvent.click(screen.getByRole('button', { name: /^Delete Contract/ }))
    expect(deleteIncome).not.toHaveBeenCalled()
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining('Contract payment'))
    fireEvent.click(screen.getByRole('button', { name: /^Delete Contract/ }))
    expect(await screen.findByText('Income deleted.')).toBeInTheDocument()
    expect(await screen.findByText('No income recorded for this month')).toBeInTheDocument()
    expect(deleteIncome).toHaveBeenCalledWith(entry)
  })

  it('shows fetch failures as errors instead of an empty balance and allows retry', async () => {
    listIncome.mockRejectedValueOnce(new Error('Cannot load income')).mockResolvedValueOnce(empty)
    render(<IncomePage />)
    expect(await screen.findByText('Cannot load income')).toBeInTheDocument()
    expect(screen.queryByText(money('0.00'))).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Reload income' }))
    expect(await screen.findByText('No income recorded for this month')).toBeInTheDocument()
  })

  it('loads another page and resets pagination when the month changes', async () => {
    listIncome.mockImplementation(async (month, page) => ({ ...populated, page, pages: 2, count: 26 }))
    render(<IncomePage />)
    await screen.findByText('Page 1 of 2')
    fireEvent.click(screen.getByRole('button', { name: 'Next' }))
    await screen.findByText('Page 2 of 2')
    fireEvent.change(screen.getByLabelText('Show month'), { target: { value: '2025-01' } })
    await waitFor(() => expect(listIncome).toHaveBeenLastCalledWith('2025-01', 1, expect.any(AbortSignal)))
  })
})
