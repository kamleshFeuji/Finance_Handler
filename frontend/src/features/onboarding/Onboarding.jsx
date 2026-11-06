import { useEffect, useRef, useState } from 'react'
import { saveProfile } from '../../api/profile.js'

const steps = ['About you', 'Your starting point', 'What matters to you']
const moneyFields = ['expected_monthly_income', 'essential_monthly_expenses', 'existing_savings_estimate']
const empty = { nickname: '', income_type: '', expected_monthly_income: '', essential_monthly_expenses: '', existing_savings_estimate: '', priority: '', goal_ideas: '' }

export const incomeLabels = { salary: 'Monthly salary', freelance: 'Freelance or irregular income', allowance: 'Allowance or part-time income', other: 'Other income' }
export const priorityLabels = { emergency: 'Build an emergency fund', security: 'Feel more financially secure', travel: 'Save for travel and experiences', enjoyment: 'Make room for hobbies and enjoyment', purchase: 'Work toward a purchase or education', explore: "I'm still figuring it out" }

export default function Onboarding({ initial, onSaved, onCancel }) {
  const [form, setForm] = useState(() => Object.fromEntries(Object.keys(empty).map((key) => [key, initial?.[key] ?? empty[key]])))
  const [step, setStep] = useState(0)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [fields, setFields] = useState({})
  const heading = useRef(null)
  const submitting = useRef(false)
  useEffect(() => { heading.current?.focus() }, [step])

  function change(event) {
    const { name, value } = event.target
    setForm((previous) => ({ ...previous, [name]: value }))
    setFields((previous) => ({ ...previous, [name]: undefined }))
  }

  async function submit(event) {
    event.preventDefault()
    if (step < 2) { setStep(step + 1); return }
    if (submitting.current) return
    submitting.current = true
    setSaving(true)
    setError('')
    setFields({})
    const payload = { ...form }
    moneyFields.forEach((key) => { payload[key] = form[key] === '' ? null : form[key] })
    try { onSaved(await saveProfile(payload)) } catch (failure) {
      const problems = failure.fields || {}
      setFields(problems)
      setError(failure.message)
      if (problems.nickname || problems.income_type) setStep(0)
      else if (moneyFields.some((key) => problems[key])) setStep(1)
    } finally { setSaving(false); submitting.current = false }
  }

  const controlProps = (name) => ({ name, id: name, value: form[name], onChange: change, 'aria-invalid': Boolean(fields[name]), 'aria-describedby': `${name}-help${fields[name] ? ` ${name}-error` : ''}` })
  const fieldError = (name) => fields[name] && <p className="field-error" id={`${name}-error`}>{fields[name].join(' ')}</p>

  return (
    <section className="onboarding-card" aria-labelledby="onboarding-title">
      <div className="onboarding-top"><span className="eyebrow">A PLAN THAT FITS YOUR LIFE</span><span className="step-count">Step {step + 1} of 3</span></div>
      <ol className="step-list" aria-label="Setup progress">{steps.map((label, index) => <li key={label} aria-current={index === step ? 'step' : undefined} className={index <= step ? 'step-active' : ''}><span aria-hidden="true">{index + 1}</span>{label}</li>)}</ol>
      <h2 id="onboarding-title" tabIndex="-1" ref={heading}>{steps[step]}</h2>
      <p className="form-intro">Every question is optional. An estimate is enough, and you can update it later.</p>
      <form onSubmit={submit}>
        <fieldset disabled={saving}>
          <legend className="sr-only">{steps[step]}</legend>
          {step === 0 && <>
            <div className="form-field"><label htmlFor="nickname">What should we call you?</label><input {...controlProps('nickname')} autoComplete="nickname" maxLength={60} placeholder="Your name or nickname" /><p className="field-help" id="nickname-help">A friendly name to make this space yours.</p>{fieldError('nickname')}</div>
            <div className="form-field"><label htmlFor="income_type">How do you receive income?</label><select {...controlProps('income_type')}><option value="">I'll decide later</option>{Object.entries(incomeLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><p className="field-help" id="income_type-help">There is no need for a fixed salary. Allowances and irregular income count too.</p>{fieldError('income_type')}</div>
          </>}
          {step === 1 && <>
            <p className="info-note">These are planning estimates in Indian rupees (INR), not recorded income, expenses, or savings transactions.</p>
            {[
              ['expected_monthly_income', 'Approximate monthly income', 'For irregular income, use a typical month or leave this blank.'],
              ['essential_monthly_expenses', 'Essential monthly expenses', 'Include rent, groceries, transport, bills, and other needs.'],
              ['existing_savings_estimate', 'Existing savings estimate', 'Roughly what you already have set aside. This will not count as new savings.'],
            ].map(([key, label, help]) => <div className="form-field" key={key}><label htmlFor={key}>{label}</label><div className="money-input"><span aria-hidden="true">₹</span><input {...controlProps(key)} type="number" inputMode="decimal" min="0" max="999999999999.99" step="0.01" placeholder="Optional" /></div><p className="field-help" id={`${key}-help`}>{help}</p>{fieldError(key)}</div>)}
          </>}
          {step === 2 && <>
            <div className="form-field"><label htmlFor="priority">What would you like to focus on first?</label><select {...controlProps('priority')}><option value="">I'll decide later</option>{Object.entries(priorityLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select><p className="field-help" id="priority-help">Choose what matters to you. You do not need to give up the things you enjoy.</p>{fieldError('priority')}</div>
            <div className="form-field"><label htmlFor="goal_ideas">Any goals on your mind?</label><textarea {...controlProps('goal_ideas')} rows={3} maxLength={500} placeholder="For example: a laptop, a trip, or a safety cushion" /><p className="field-help" id="goal_ideas-help">A few ideas are enough. You can create detailed savings goals later.</p>{fieldError('goal_ideas')}</div>
            <p className="info-note">Your profile stays in your local database. No bank details are needed.</p>
          </>}
        </fieldset>
        {error && <p className="form-error" role="alert">{error}</p>}
        <div className="form-actions">
          {step > 0 && <button type="button" className="secondary" disabled={saving} onClick={() => setStep(step - 1)}>Back</button>}
          {initial && <button type="button" className="text-button" disabled={saving} onClick={onCancel}>Cancel</button>}
          <button className="primary-action" type="submit" disabled={saving}>{saving ? 'Saving…' : step === 2 ? 'Save my starting point' : 'Continue'}</button>
        </div>
        <p className="optional-note">Leave a question blank to skip it.</p>
      </form>
    </section>
  )
}
