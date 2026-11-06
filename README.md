# SaveQuest — Your Financial Journey

SaveQuest helps beginners decide where to save, understand why it matters, and build realistic habits while still enjoying life. Progress rewards planning, learning, and consistency rather than income or wealth.

## Project status

**Single-user local onboarding is implemented.**

The app now opens into a three-step onboarding form: nickname/income type, optional financial estimates, and savings priorities/goal ideas. Answers are saved in PostgreSQL, restored after refresh, and editable from the saved summary. Every question is optional; blank money values remain unknown rather than becoming zero.

The first laptop's PostgreSQL connection works and the profile migration is applied. Existing savings is an onboarding estimate only; no actual savings transactions or goals are created yet. Registration and login are deferred at the owner's request. One internal account with an unusable password owns the local profile; it is never selected by the browser.

Git initialization was not performed because that action was declined. No commits, remote configuration, or publication were made. `.gitignore` is prepared for when you initialize the repository.

The app remains loopback-only with CSRF-protected writes. Income/expense entry, actual goals, savings ledger, dashboard and gamification are future milestones. No deployment is authorized.

## Run locally

On the first laptop, the environment and database are already configured. On a fresh laptop, follow [the Windows setup guide](docs/DEVELOPMENT.md#configure-postgresql) first. From the repository root:

```powershell
.\backend\.venv\Scripts\python.exe backend\manage.py migrate
.\backend\.venv\Scripts\python.exe backend\manage.py runserver localhost:8000
```

In another PowerShell terminal:

```powershell
Set-Location frontend
npm.cmd run dev
```

Open `http://localhost:5173` and refresh once if an older page is open. You should see **About you**, the first onboarding step. Saved profiles open their summary instead. Connection/database failures still show an actionable status screen. Restart Django after pulling backend changes; keep both servers on `localhost`. If PowerShell blocks `npm.ps1`, use `npm.cmd` as shown; changing execution policy is unnecessary. The Python environment can also be used directly without activation.

## Read the plan

| Document | Contents |
| --- | --- |
| [Architecture](docs/ARCHITECTURE.md) | Stack, module boundaries, API, authentication, proposed folders |
| [Database](docs/DATABASE.md) | ER diagram, entity fields, constraints, financial calculations |
| [Features](docs/FEATURES.md) | Product vision, user journeys, MVP and deferred scope |
| [UI and dashboard](docs/UI_UX.md) | Navigation, wireframe, page/component structure, accessibility |
| [Gamification](docs/GAMIFICATION.md) | Badges, XP, progression, safe reward rules |
| [Roadmap](docs/ROADMAP.md) | Incremental delivery and acceptance gates |
| [Development](docs/DEVELOPMENT.md) | Windows setup plan, collaboration, tests, seed strategy |
| [Risks and decisions](docs/DECISIONS.md) | Assumptions, tradeoffs, questions for review |
| [Agent instructions](AGENTS.md) | Persistent project rules |

## Proposed technical baseline

React with JavaScript and Vite; custom CSS; Python and Django REST Framework; local PostgreSQL. Recharts is planned for charts. Each developer runs a separate local database using shared migrations; fictional seeds will arrive with financial models. All runtime tools are free and open source; no cloud account is required.

The first laptop uses Python 3.14, Node 24.12.0 and PostgreSQL 18. Django 5.2.19, DRF 3.18.3, React 19.3.1 and Vite 8.3.6 are installed. See the architecture document for compatibility references and the lockfiles for the full resolved dependency set. Recharts and routing will be installed when those features need them.

## Verification and next milestone

Passed: 16 backend tests, 8 frontend tests, and the production build. A real PostgreSQL smoke check verified profile creation/read/update, repeated saves, Decimal precision, unknown versus zero, database constraints and reserved-owner handling inside a rolled-back transaction. No fictional profile was retained. Separate test-database credentials are still unconfigured; this check did not claim to run an isolated database suite. Browser visual verification was blocked because the automation host could not determine the current browser URL.

Next milestone: record income and expenses, followed by goals and the savings ledger. Login remains deferred. Do not scaffold all product modules at once.

See [Windows setup](docs/DEVELOPMENT.md) for prerequisites and the proposed commands for both laptops.
