import { useEffect, useState } from 'react'
import { getHealth } from './api/health.js'
import { getProfile } from './api/profile.js'
import Onboarding from './features/onboarding/Onboarding.jsx'
import ProfileSummary from './features/onboarding/ProfileSummary.jsx'
import IncomePage from './features/income/IncomePage.jsx'
import ExpensePage from './features/expenses/ExpensePage.jsx'
import Overview from './features/overview/Overview.jsx'

const messages = {
  checking: ['Checking your connection', 'Making sure your local services are ready.'],
  connected: ['Your connection is ready', 'SaveQuest can reach your local database.'],
  'database-unavailable': ['Database setup needed', 'The backend is running. Configure PostgreSQL in backend/.env, then check again.'],
  offline: ['Cannot reach the backend', 'Start Django on localhost:8000, then check again.'],
  'profile-error': ['Could not load your profile', 'Your saved information has not been changed. Check the backend and apply the latest migrations, then try again.'],
}

export default function App() {
  const [state, setState] = useState('checking')
  const [attempt, setAttempt] = useState(0)
  const [profile, setProfile] = useState(null)
  const [editing, setEditing] = useState(false)
  const [page, setPage] = useState('overview')
  const name = import.meta.env.VITE_APP_NAME || 'SaveQuest'

  useEffect(() => {
    const controller = new AbortController()
    const timeout = window.setTimeout(() => controller.abort(), 8000)
    let active = true
    setState('checking')
    getHealth(controller.signal)
      .then(async (result) => {
        if (!active) return
        if (result.state !== 'connected') { setState(result.state); return }
        try {
          const saved = await getProfile(controller.signal)
          if (active) { setProfile(saved); setState('ready') }
        } catch { if (active) setState('profile-error') }
      })
      .catch(() => { if (active) setState('offline') })
      .finally(() => window.clearTimeout(timeout))
    return () => {
      active = false
      controller.abort()
      window.clearTimeout(timeout)
    }
  }, [attempt])

  useEffect(() => { document.title = `${name} — Your Financial Journey` }, [name])

  const [title, detail] = messages[state] || ['', '']
  return (
    <>
      <a className="skip-link" href="#main">Skip to content</a>
      <header className="site-header">
        <span className="brand-mark" aria-hidden="true">S</span>
        <span className="brand-name">{name}</span>
        <span className="local-tag">Your local savings space</span>
      </header>
      <main id="main">
        <section className={`intro${profile ? ' intro--compact' : ''}`} aria-labelledby="welcome-title">
          <p className="eyebrow">YOUR FINANCIAL JOURNEY</p>
          <h1 id="welcome-title">Small steps.<br /><span>Meaningful progress.</span></h1>
          <p className="intro-copy">A little planning today. More possibilities tomorrow.
            Your savings journey starts with a foundation you can build on.</p>
        </section>
        {state === 'ready' && profile && !editing && <nav className="app-navigation" aria-label="Main navigation">
          <button type="button" className={page === 'overview' ? 'nav-active' : ''} aria-current={page === 'overview' ? 'page' : undefined} onClick={() => setPage('overview')}>Overview</button>
          <button type="button" className={page === 'income' ? 'nav-active' : ''} aria-current={page === 'income' ? 'page' : undefined} onClick={() => setPage('income')}>Income</button>
          <button type="button" className={page === 'expenses' ? 'nav-active' : ''} aria-current={page === 'expenses' ? 'page' : undefined} onClick={() => setPage('expenses')}>Expenses</button>
          <button type="button" className={page === 'profile' ? 'nav-active' : ''} aria-current={page === 'profile' ? 'page' : undefined} onClick={() => setPage('profile')}>Profile</button>
        </nav>}
        {state === 'ready' && profile && !editing && page === 'overview' ? <Overview nickname={profile.nickname} onNavigate={setPage} /> : state === 'ready' && profile && !editing && page === 'expenses' ? <ExpensePage /> : state === 'ready' && profile && !editing && page === 'income' ? <IncomePage /> : state === 'ready' ? (
          profile && !editing
            ? <ProfileSummary profile={profile} onEdit={() => setEditing(true)} onNavigate={setPage} />
            : <Onboarding initial={profile} onCancel={() => setEditing(false)} onSaved={(saved) => { setProfile(saved); setEditing(false); setPage('profile') }} />
        ) : <section className="setup-card" aria-labelledby="setup-title">
          <div className="card-heading">
            <span className="step-number" aria-hidden="true">01</span>
            <div><p className="eyebrow">FIRST MILESTONE</p><h2 id="setup-title">A place to begin</h2></div>
            <span className="phase-tag">Environment setup</span>
          </div>
          <div className={`connection connection--${state}`} role="status" aria-live="polite" aria-busy={state === 'checking'}>
            <span className="status-dot" aria-hidden="true" />
            <div><h3>{title}</h3><p>{detail}</p></div>
          </div>
          <button type="button" disabled={state === 'checking'} onClick={() => setAttempt((value) => value + 1)}>
            {state === 'checking' ? 'Checking…' : 'Check connection again'}
          </button>
        </section>}
        <p className="closing-note">Built around your life. Progress at your own pace.</p>
      </main>
      <footer>Plan with purpose. Save with confidence.</footer>
    </>
  )
}
