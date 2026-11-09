import { useEffect, useState } from 'react'
import { getOverview } from '../../api/expenses.js'
import { money, today } from '../../lib/format.js'

export default function Overview({ nickname, onNavigate }) {
  const [month, setMonth] = useState(() => today().slice(0, 7))
  const [data, setData] = useState(null)
  const [error, setError] = useState('')
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let active = true
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 10000)
    setData(null)
    setError('')
    getOverview(month, controller.signal).then((result) => { if (active) setData(result) })
      .catch((failure) => { if (active) setError(failure.name === 'AbortError' ? 'Loading took too long. Please try again.' : failure.message) })
      .finally(() => window.clearTimeout(timeout))
    return () => { active = false; controller.abort(); window.clearTimeout(timeout) }
  }, [month, attempt])

  return <section className="onboarding-card" aria-labelledby="overview-title">
    <p className="eyebrow">YOUR MONTH AT A GLANCE</p>
    <h2 id="overview-title">{nickname ? `Your overview, ${nickname}` : 'Your monthly overview'}</h2>
    <p className="form-intro">Record money as it comes in and goes out. Every small step helps you understand your month.</p>
    <div className="quick-actions"><button type="button" onClick={() => onNavigate('income')}>Record income</button><button type="button" className="secondary" onClick={() => onNavigate('expenses')}>Record an expense</button></div>
    <div className="month-filter"><label htmlFor="overview-month">Overview month</label><input id="overview-month" type="month" value={month} onChange={(event) => { if (event.target.value) setMonth(event.target.value) }} /></div>
    {error ? <div className="form-error" role="alert"><p>{error}</p><button type="button" className="secondary" onClick={() => setAttempt(attempt + 1)}>Retry overview</button></div> : !data ? <p role="status">Loading your month…</p> : <>
      <dl className="overview-stats">
        <div><dt>Recorded income</dt><dd>{money(data.income)}</dd><p>{data.income_count ? `${data.income_count} entries` : 'No income recorded'}</p></div>
        <div><dt>Recorded expenses</dt><dd>{money(data.expenses)}</dd><p>{data.expense_count ? `${data.expense_count} entries` : 'No expenses recorded'}</p></div>
        <div><dt>Remaining after expenses</dt><dd>{money(data.remaining)}</dd><p>Recorded income minus expenses</p></div>
      </dl>
      <p className="info-note">These totals come from your recorded entries, not your profile estimates. The remainder excludes savings transfers and is not your bank balance.</p>
      {Number(data.remaining) < 0 && <p className="balance-note">Recorded expenses are higher than recorded income for this month. You may be using earlier savings, or have income still to enter. There is no penalty for covering your needs.</p>}
      {!data.income_count && !data.expense_count && <p className="income-empty">Start with one income or expense entry using the buttons above. Your profile estimates stay separate.</p>}
      {data.expense_count > 0 && <>
        <h3>Where your spending went</h3><p className="field-help">Essentials {money(data.essential)} · Optional spending {money(data.optional)}</p>
        <ul className="category-breakdown">{(data.categories || []).map((category) => <li key={category.id}><span>{category.name}</span><strong>{money(category.total)}</strong></li>)}</ul>
      </>}
    </>}
  </section>
}
