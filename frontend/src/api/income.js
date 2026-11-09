import { request, writeJSON } from './client.js'

export function listIncome(month, page, signal) {
  return request(`income/?${new URLSearchParams({ month, page: String(page) })}`, { signal })
}

export async function saveIncome(entry, existing) {
  return (await writeJSON(existing ? `income/${existing.id}/` : 'income/', existing ? 'PUT' : 'POST', entry)).entry
}

export function deleteIncome(entry) {
  return writeJSON(`income/${entry.id}/`, 'DELETE', { expected_version: entry.version })
}
