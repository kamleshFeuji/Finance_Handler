import { incomeLabels, priorityLabels } from './Onboarding.jsx'

const formatMoney = (value) => value == null ? 'Not provided' : new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR', maximumFractionDigits: 2 }).format(value)

export default function ProfileSummary({ profile, onEdit }) {
  return <section className="onboarding-card" aria-labelledby="summary-title">
    <p className="eyebrow">YOUR STARTING POINT IS SAVED</p>
    <h2 id="summary-title">{profile.nickname ? `Welcome, ${profile.nickname}.` : "You're ready to begin."}</h2>
    <p className="form-intro">Small steps are enough. Here is the starting point you can build on.</p>
    <dl className="profile-grid">
      <div><dt>Income type</dt><dd>{incomeLabels[profile.income_type] || 'Not provided'}</dd></div>
      <div><dt>Your first priority</dt><dd>{priorityLabels[profile.priority] || 'Not decided yet'}</dd></div>
      <div><dt>Monthly income estimate</dt><dd>{formatMoney(profile.expected_monthly_income)}</dd></div>
      <div><dt>Essential expenses estimate</dt><dd>{formatMoney(profile.essential_monthly_expenses)}</dd></div>
      <div><dt>Existing savings estimate</dt><dd>{formatMoney(profile.existing_savings_estimate)}</dd></div>
      <div><dt>Goals on your mind</dt><dd className="goal-ideas">{profile.goal_ideas || 'Room for something meaningful'}</dd></div>
    </dl>
    <p className="info-note">These figures are estimates, not recorded transactions. Income, expense entries, and detailed goal tracking are the next steps for SaveQuest.</p>
    <button type="button" onClick={onEdit}>Edit my starting point</button>
  </section>
}
