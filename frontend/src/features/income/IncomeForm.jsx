import { useEffect, useRef, useState } from 'react'
import { saveIncome } from '../../api/income.js'
import { sourceLabels, today } from './format.js'

export default function IncomeForm({ entry, month, onSaved, onCancel }) {
  const [form, setForm] = useState(() => ({
    amount: entry?.amount ?? '', source: entry?.source ?? 'salary', label: entry?.label ?? '',
    received_on: entry?.received_on ?? (month < today().slice(0, 7) ? `${month}-01` : today()), note: entry?.note ?? '',
  }))
  const [requestKey] = useState(() => crypto.randomUUID())
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [fields, setFields] = useState({})
  const busy = useRef(false)
  const heading = useRef(null)
  useEffect(() => { heading.current?.focus() }, [])

  function change(event) {
    setForm((previous) => ({ ...previous, [event.target.name]: event.target.value }))
    setFields((previous) => ({ ...previous, [event.target.name]: undefined }))
  }

  async function submit(event) {
    event.preventDefault()
    if (busy.current) return
    busy.current = true
    setSaving(true)
    setError('')
    setFields({})
    try {
      const payload = { ...form, ...(entry ? { expected_version: entry.version } : { request_key: requestKey }) }
      onSaved(await saveIncome(payload, entry))
    } catch (failure) { setError(failure.message); setFields(failure.fields || {}) }
    finally { busy.current = false; setSaving(false) }
  }

  const props = (key) => ({ id: `income-${key}`, name: key, value: form[key], onChange: change, 'aria-invalid': Boolean(fields[key]), 'aria-describedby': fields[key] ? `income-${key}-error` : undefined })
  const fieldError = (key) => fields[key] && <p className="field-error" id={`income-${key}-error`}>{fields[key].join(' ')}</p>

  return <section className="income-form" aria-labelledby="income-form-title">
    <h3 id="income-form-title" tabIndex="-1" ref={heading}>{entry ? 'Edit income' : 'Record money you received'}</h3>
    <p className="field-help">Only record income you have actually received. Future income belongs in your plan.</p>
    <form onSubmit={submit}>
      <fieldset disabled={saving}>
        <legend className="sr-only">Income details</legend>
        <div className="income-form-grid">
          <div className="form-field"><label htmlFor="income-amount">Amount (INR)</label><input {...props('amount')} type="number" inputMode="decimal" min="0.01" max="999999999999.99" step="0.01" required />{fieldError('amount')}</div>
          <div className="form-field"><label htmlFor="income-source">Income source</label><select {...props('source')} required>{Object.entries(sourceLabels).map(([key, label]) => <option key={key} value={key}>{label}</option>)}</select>{fieldError('source')}</div>
          <div className="form-field"><label htmlFor="income-received_on">Date received</label><input {...props('received_on')} type="date" max={today()} required />{fieldError('received_on')}</div>
          <div className="form-field"><label htmlFor="income-label">Label (optional)</label><input {...props('label')} maxLength={100} placeholder="For example: November salary" />{fieldError('label')}</div>
        </div>
        <div className="form-field"><label htmlFor="income-note">Note (optional)</label><textarea {...props('note')} maxLength={500} rows={2} />{fieldError('note')}</div>
      </fieldset>
      {error && <p className="form-error" role="alert">{error}</p>}
      <div className="form-actions"><button type="button" className="secondary" disabled={saving} onClick={onCancel}>Cancel</button><button type="submit" className="primary-action" disabled={saving}>{saving ? 'Saving…' : entry ? 'Save changes' : 'Save income'}</button></div>
    </form>
  </section>
}
