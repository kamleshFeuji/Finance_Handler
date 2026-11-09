import { request, writeJSON } from './client.js'

export const listExpenses = (month, page, signal) => request(`expenses/?${new URLSearchParams({ month, page: String(page) })}`, { signal })
export const listCategories = (signal) => request('expense-categories/', { signal })
export const getOverview = (month, signal) => request(`overview/?${new URLSearchParams({ month })}`, { signal })
export async function saveExpense(data, entry) {
  return (await writeJSON(entry ? `expenses/${entry.id}/` : 'expenses/', entry ? 'PUT' : 'POST', data)).entry
}
export const deleteExpense = (entry) => writeJSON(`expenses/${entry.id}/`, 'DELETE', { expected_version: entry.version })
export async function saveCategory(data, category) {
  return (await writeJSON(category ? `expense-categories/${category.id}/` : 'expense-categories/', category ? 'PUT' : 'POST', data)).category
}
