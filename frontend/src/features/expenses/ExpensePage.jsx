import { useEffect, useRef, useState } from 'react'
import { deleteExpense, listCategories, listExpenses } from '../../api/expenses.js'
import { displayDate, money, today } from '../../lib/format.js'
import CategoryManager from './CategoryManager.jsx'
import ExpenseForm from './ExpenseForm.jsx'

export default function ExpensePage() {
  const [month, setMonth] = useState(() => today().slice(0, 7))
  const [page, setPage] = useState(1)
  const [attempt, setAttempt] = useState(0)
  const [data, setData] = useState(null)
  const [categories, setCategories] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [form, setForm] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const busy = useRef(false)
  useEffect(() => {
    let active = true
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 10000)
    setLoading(true); setData(null); setError('')
    Promise.all([listExpenses(month, page, controller.signal), listCategories(controller.signal)])
      .then(([entries, choices]) => { if (active) { setData(entries); setCategories(choices.results) } })
      .catch((failure) => { if (active) setError(failure.name === 'AbortError' ? 'Loading took too long. Please try again.' : failure.message) })
      .finally(() => { window.clearTimeout(timeout); if (active) setLoading(false) })
    return () => { active = false; controller.abort(); window.clearTimeout(timeout) }
  }, [month, page, attempt])
  function refresh(message) { setNotice(message); setPage(1); setAttempt((value) => value + 1) }
  function saved(entry) { setNotice(form?.entry ? 'Expense updated.' : 'Expense saved.'); setForm(null); setMonth(entry.spent_on.slice(0, 7)); setPage(1); setAttempt((value) => value + 1) }
  async function remove(entry) {
    if (busy.current || !window.confirm(`Delete ${money(entry.amount)} for ${entry.label || entry.category_name} on ${displayDate(entry.spent_on)}? This will remove it from your expense totals.`)) return
    busy.current = true; setDeleting(true); setError('')
    try { await deleteExpense(entry); refresh('Expense deleted.') } catch (failure) { setError(failure.message) }
    finally { busy.current = false; setDeleting(false) }
  }
  return <section className="onboarding-card" aria-labelledby="expense-title">
    <div className="income-heading"><div><p className="eyebrow">MONEY GOING OUT</p><h2 id="expense-title">Your expenses</h2></div><button type="button" disabled={loading || Boolean(form) || deleting || !categories.some((category) => !category.is_archived)} onClick={() => { setNotice(''); setForm({ entry: null }) }}>Add expense</button></div>
    <p className="form-intro">Everyday needs and things you enjoy, together in one clear record.</p>
    {notice && <p className="success-note" role="status">{notice}</p>}
    {form && <ExpenseForm key={form.entry?.id || 'new'} entry={form.entry} categories={categories} month={month} onSaved={saved} onCancel={() => setForm(null)} />}
    <div className="month-filter"><label htmlFor="expense-month">Expense month</label><input id="expense-month" type="month" value={month} disabled={Boolean(form) || deleting} onChange={(event) => { if (event.target.value) { setMonth(event.target.value); setPage(1); setNotice('') } }} /></div>
    {loading && <p role="status">Loading expenses…</p>}
    {error && <div className="form-error" role="alert"><p>{error}</p><button type="button" className="secondary" onClick={() => refresh('')}>Reload expenses</button></div>}
    {data && !loading && <>
      <div className="expense-stats"><div><span>Total expenses</span><strong>{money(data.total)}</strong></div><div><span>Essentials</span><strong>{money(data.essential)}</strong></div><div><span>Optional spending</span><strong>{money(data.optional)}</strong></div></div>
      {!data.results.length ? <div className="income-empty"><h3>No expenses recorded for this month</h3><p>Start with groceries, a bill, or something you enjoyed. Use Add expense above.</p></div> : <ul className="income-list" aria-label="Expense history">{data.results.map((entry) => <li key={entry.id}><div className="income-entry-main"><div><h3>{entry.label || entry.category_name}</h3><p>{displayDate(entry.spent_on)} · {entry.category_name} · {entry.is_essential ? 'Essential' : 'Optional'}</p>{entry.note && <p className="income-note">{entry.note}</p>}</div><strong>{money(entry.amount)}</strong></div><div className="income-entry-actions"><button type="button" className="text-button" disabled={Boolean(form) || deleting} aria-label={`Edit expense ${entry.label || entry.category_name}`} onClick={() => setForm({ entry })}>Edit</button><button type="button" className="text-button danger" disabled={Boolean(form) || deleting} aria-label={`Delete expense ${entry.label || entry.category_name}`} onClick={() => remove(entry)}>Delete</button></div></li>)}</ul>}
      {data.pages > 1 && <nav className="pagination" aria-label="Expense pages"><button type="button" className="secondary" disabled={page <= 1 || deleting || Boolean(form)} onClick={() => setPage(page - 1)}>Previous</button><span>Page {data.page} of {data.pages}</span><button type="button" className="secondary" disabled={page >= data.pages || deleting || Boolean(form)} onClick={() => setPage(page + 1)}>Next</button></nav>}
      {data.categories.length > 0 && <><h3 className="breakdown-title">Spending by category</h3><ul className="category-breakdown">{data.categories.map((category) => <li key={category.id}><span>{category.name}</span><strong>{money(category.total)}</strong></li>)}</ul></>}
      {!categories.some((category) => !category.is_archived) && <p className="info-note">Add or restore a category below to record an expense.</p>}
      <CategoryManager categories={categories} disabled={Boolean(form) || deleting} onChanged={refresh} />
    </>}
  </section>
}
