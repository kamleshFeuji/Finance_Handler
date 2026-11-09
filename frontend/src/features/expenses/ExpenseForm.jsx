import { useEffect, useRef, useState } from 'react'
import { saveExpense } from '../../api/expenses.js'
import { today } from '../../lib/format.js'

export default function ExpenseForm({ entry, month, categories, onSaved, onCancel }) {
  const available = categories.filter((category) => !category.is_archived || category.id === entry?.category)
  const first = available.find((category) => category.id === entry?.category) || available[0]
  const [form, setForm] = useState(() => ({ amount: entry?.amount ?? '', category: entry?.category ?? first?.id ?? '', is_essential: entry?.is_essential ?? first?.default_essential ?? false, spent_on: entry?.spent_on ?? (month < today().slice(0, 7) ? `${month}-01` : today()), label: entry?.label ?? '', note: entry?.note ?? '' }))
  const [requestKey] = useState(() => crypto.randomUUID())
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [fields, setFields] = useState({})
  const busy = useRef(false)
  const heading = useRef(null)
  useEffect(() => { heading.current?.focus() }, [])
  function change(event) {
    const { name, value, checked, type } = event.target
    setForm((previous) => ({ ...previous, [name]: type === 'checkbox' ? checked : name === 'category' ? Number(value) : value, ...(name === 'category' ? { is_essential: categories.find((category) => category.id === Number(value))?.default_essential ?? false } : {}) }))
    setFields((previous) => ({ ...previous, [name]: undefined }))
  }
  async function submit(event) {
    event.preventDefault()
    if (busy.current) return
    busy.current = true; setSaving(true); setError(''); setFields({})
    try { onSaved(await saveExpense({ ...form, ...(entry ? { expected_version: entry.version } : { request_key: requestKey }) }, entry)) }
    catch (failure) { setError(failure.message); setFields(failure.fields || {}) }
    finally { busy.current = false; setSaving(false) }
  }
  const props = (name) => ({ id: `expense-${name}`, name, value: form[name], onChange: change, 'aria-invalid': Boolean(fields[name]), 'aria-describedby': fields[name] ? `expense-${name}-error` : undefined })
  const fieldError = (name) => fields[name] && <p className="field-error" id={`expense-${name}-error`}>{fields[name].join(' ')}</p>
  return <section className="income-form" aria-labelledby="expense-form-title">
    <h3 id="expense-form-title" ref={heading} tabIndex="-1">{entry ? 'Edit expense' : 'Record money you spent'}</h3>
    <p className="field-help">A quick record is enough. Spending on your needs is part of the plan.</p>
    <form onSubmit={submit}><fieldset disabled={saving}><legend className="sr-only">Expense details</legend>
      <div className="income-form-grid">
        <div className="form-field"><label htmlFor="expense-amount">Expense amount (INR)</label><input {...props('amount')} type="number" inputMode="decimal" min="0.01" max="999999999999.99" step="0.01" required />{fieldError('amount')}</div>
        <div className="form-field"><label htmlFor="expense-category">Category</label><select {...props('category')} required>{available.map((category) => <option key={category.id} value={category.id}>{category.name}{category.is_archived ? ' (archived)' : ''}</option>)}</select>{fieldError('category')}</div>
        <div className="form-field"><label htmlFor="expense-spent_on">Date spent</label><input {...props('spent_on')} type="date" max={today()} required />{fieldError('spent_on')}</div>
        <div className="form-field"><label htmlFor="expense-label">Expense label (optional)</label><input {...props('label')} maxLength={100} placeholder="For example: weekly groceries" />{fieldError('label')}</div>
      </div>
      <div className="form-field"><label className="checkbox-label" htmlFor="expense-is_essential"><input id="expense-is_essential" name="is_essential" type="checkbox" checked={form.is_essential} onChange={change} />Essential expense</label><p className="field-help">Needs such as food, rent, bills or healthcare. Uncheck for optional spending; both belong in your budget.</p>{fieldError('is_essential')}</div>
      <div className="form-field"><label htmlFor="expense-note">Expense note (optional)</label><textarea {...props('note')} maxLength={500} rows={2} />{fieldError('note')}</div>
    </fieldset>{error && <p className="form-error" role="alert">{error}</p>}
      <div className="form-actions"><button type="button" className="secondary" disabled={saving} onClick={onCancel}>Cancel</button><button type="submit" className="primary-action" disabled={saving || !form.category}>{saving ? 'Saving…' : entry ? 'Save expense changes' : 'Save expense'}</button></div>
    </form>
  </section>
}
