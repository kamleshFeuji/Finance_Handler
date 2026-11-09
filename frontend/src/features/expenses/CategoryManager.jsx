import { useRef, useState } from 'react'
import { saveCategory } from '../../api/expenses.js'

export default function CategoryManager({ categories, disabled, onChanged }) {
  const [name, setName] = useState('')
  const [essential, setEssential] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const active = useRef(false)
  async function save(data, category) {
    if (active.current) return
    active.current = true; setBusy(true); setError('')
    try { await saveCategory(data, category); onChanged(category ? 'Category updated.' : 'Category added.'); setName(''); setEssential(false) }
    catch (failure) { setError(failure.fields?.name?.join(' ') || failure.message) }
    finally { active.current = false; setBusy(false) }
  }
  return <details className="category-manager"><summary>Manage expense categories</summary>
    <p className="field-help">Add a category of your own. Archiving hides a category from new entries; past spending stays in your history. Restore it any time.</p>
    <form onSubmit={(event) => { event.preventDefault(); save({ name, default_essential: essential }) }}><fieldset disabled={disabled || busy}><legend className="sr-only">New expense category</legend>
      <div className="form-field"><label htmlFor="category-name">New category name</label><input id="category-name" value={name} maxLength={100} required onChange={(event) => setName(event.target.value)} /></div>
      <label className="checkbox-label" htmlFor="category-default-essential"><input id="category-default-essential" type="checkbox" checked={essential} onChange={(event) => setEssential(event.target.checked)} />Usually essential</label>
      <button type="submit" className="secondary">Add category</button>
    </fieldset></form>
    {error && <p className="form-error" role="alert">{error}</p>}
    <ul className="category-list">{categories.map((category) => <li key={category.id}><span>{category.name}<small>{category.is_archived ? 'Archived' : category.default_essential ? 'Usually essential' : 'Usually optional'}</small></span><button type="button" className="text-button" disabled={disabled || busy} aria-label={`${category.is_archived ? 'Restore' : 'Archive'} ${category.name}`} onClick={() => save({ name: category.name, default_essential: category.default_essential, is_archived: !category.is_archived, expected_version: category.version }, category)}>{category.is_archived ? 'Restore' : 'Archive'}</button></li>)}</ul>
  </details>
}
