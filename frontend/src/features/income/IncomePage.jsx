import { useEffect, useRef, useState } from 'react'
import { deleteIncome, listIncome } from '../../api/income.js'
import IncomeForm from './IncomeForm.jsx'
import { displayDate, money, sourceLabels, today } from './format.js'

export default function IncomePage() {
  const [month, setMonth] = useState(() => today().slice(0, 7))
  const [page, setPage] = useState(1)
  const [attempt, setAttempt] = useState(0)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')
  const [form, setForm] = useState(null)
  const [deleting, setDeleting] = useState(false)
  const deleteBusy = useRef(false)

  useEffect(() => {
    const controller = new AbortController()
    let active = true
    const timeout = window.setTimeout(() => controller.abort(), 10000)
    setLoading(true)
    setData(null)
    setError('')
    listIncome(month, page, controller.signal)
      .then((result) => { if (active) setData(result) })
      .catch((failure) => { if (active) setError(failure.name === 'AbortError' ? 'Loading took too long. Try again.' : failure.message) })
      .finally(() => { window.clearTimeout(timeout); if (active) setLoading(false) })
    return () => { active = false; controller.abort(); window.clearTimeout(timeout) }
  }, [month, page, attempt])

  function saved(entry) {
    setNotice(form?.entry ? 'Income updated.' : 'Income saved.')
    setForm(null)
    setMonth(entry.received_on.slice(0, 7))
    setPage(1)
    setAttempt((value) => value + 1)
  }

  async function remove(entry) {
    if (deleteBusy.current || !window.confirm(`Delete ${money(entry.amount)} from ${entry.label || sourceLabels[entry.source]} received on ${displayDate(entry.received_on)}? This will remove it from your income totals.`)) return
    deleteBusy.current = true
    setDeleting(true)
    setError('')
    setNotice('')
    try {
      await deleteIncome(entry)
      setNotice('Income deleted.')
      setPage(1)
      setAttempt((value) => value + 1)
    } catch (failure) { setError(failure.message) }
    finally { deleteBusy.current = false; setDeleting(false) }
  }

  return <section className="onboarding-card income-page" aria-labelledby="income-title">
    <div className="income-heading"><div><p className="eyebrow">MONEY COMING IN</p><h2 id="income-title">Your income</h2></div><button type="button" disabled={Boolean(form) || deleting} onClick={() => { setNotice(''); setForm({ entry: null }) }}>Add income</button></div>
    <p className="form-intro">A salary, freelance payment, or allowance — keep track of what you receive.</p>
    {notice && <p className="success-note" role="status">{notice}</p>}
    {form && <IncomeForm key={form.entry?.id || 'new'} entry={form.entry} month={month} onSaved={saved} onCancel={() => setForm(null)} />}
    <div className="month-filter"><label htmlFor="income-month">Show month</label><input id="income-month" type="month" value={month} disabled={Boolean(form) || deleting} onChange={(event) => { if (event.target.value) { setMonth(event.target.value); setPage(1); setNotice('') } }} /></div>
    {loading && <p role="status">Loading income…</p>}
    {error && <div className="form-error" role="alert"><p>{error}</p><button className="secondary" type="button" disabled={loading || deleting} onClick={() => { setPage(1); setAttempt((value) => value + 1) }}>Reload income</button></div>}
    {data && !loading && <>
      <div className="income-total"><div><span>Recorded income for selected month</span><strong>{money(data.total)}</strong></div><p>{data.count} {data.count === 1 ? 'entry' : 'entries'}<br /><span>Actual income, separate from your estimate</span></p></div>
      {data.results.length === 0 ? <div className="income-empty"><h3>No income recorded for this month</h3><p>Use Add income when you receive money. Irregular income is welcome here too.</p></div> : <ul className="income-list" aria-label="Income history">{data.results.map((entry) => <li key={entry.id}>
        <div className="income-entry-main"><div><h3>{entry.label || sourceLabels[entry.source]}</h3><p>{displayDate(entry.received_on)} · {sourceLabels[entry.source]}</p>{entry.note && <p className="income-note">{entry.note}</p>}</div><strong>{money(entry.amount)}</strong></div>
        <div className="income-entry-actions"><button type="button" className="text-button" disabled={Boolean(form) || deleting} aria-label={`Edit ${entry.label || sourceLabels[entry.source]} on ${displayDate(entry.received_on)}`} onClick={() => { setNotice(''); setForm({ entry }) }}>Edit</button><button type="button" className="text-button danger" disabled={Boolean(form) || deleting} aria-label={`Delete ${entry.label || sourceLabels[entry.source]} on ${displayDate(entry.received_on)}`} onClick={() => remove(entry)}>Delete</button></div>
      </li>)}</ul>}
      {data.pages > 1 && <nav className="pagination" aria-label="Income pages"><button type="button" className="secondary" disabled={page <= 1 || deleting || Boolean(form)} onClick={() => setPage(page - 1)}>Previous</button><span>Page {data.page} of {data.pages}</span><button type="button" className="secondary" disabled={page >= data.pages || deleting || Boolean(form)} onClick={() => setPage(page + 1)}>Next</button></nav>}
    </>}
  </section>
}
