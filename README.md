# SaveQuest — Your Financial Journey

SaveQuest helps beginners decide where to save, understand why it matters, and build realistic habits while still enjoying life. Progress rewards planning, learning, and consistency rather than income or wealth.

## Project status

**Single-user onboarding, income, expenses and a monthly overview are implemented.**

The app now opens into a three-step onboarding form: nickname/income type, optional financial estimates, and savings priorities/goal ideas. Answers are saved in PostgreSQL, restored after refresh, and editable from the saved summary. Every question is optional; blank money values remain unknown rather than becoming zero.

The main navigation is **Overview · Income · Expenses · Profile**. Returning users open Overview by default. Income supports salary, freelance, allowance and other sources. Expenses support default/custom categories, essentials versus optional spending, edits, confirmed deletion, month filtering and paginated history. Categories can be archived/restored without losing earlier expenses. Both histories show totals across every record in the selected month, not just the visible page.

Overview shows actual recorded income, expenses, essentials/optional spending, category totals and the remainder before savings. Profile contains onboarding estimates; editing these estimates never creates a transaction. Savings goals and the ledger are not implemented yet.

The first laptop's PostgreSQL connection works and profile/income/expense migrations are applied. Existing savings is an onboarding estimate only; no actual savings transactions or goals are created yet. Registration and login are deferred at the owner's request. One internal account with an unusable password owns the local profile; it is never selected by the browser.

Git initialization was not performed because that action was declined. No commits, remote configuration, or publication were made. `.gitignore` is prepared for when you initialize the repository.

The app remains loopback-only with CSRF-protected writes. Actual goals, savings ledger, charts and gamification remain future milestones. No deployment is authorized.

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

Open `http://localhost:5173`; use **Ctrl+Shift+R** if an older screen is open. New users complete About you first; returning users open Overview with Income, Expenses and Profile alongside it. Choose Income → Add income or Expenses → Add expense. After first onboarding, the profile confirmation includes direct links to both entry pages. Connection/database failures show actionable messages. Restart Django after pulling backend changes; keep both servers on `localhost`. Use `npm.cmd` if PowerShell blocks `npm.ps1`; execution policy changes and virtual-environment activation are unnecessary.

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

Passed: 40 backend tests, 29 frontend tests, production build, Django checks and migration consistency checks. Real PostgreSQL income/expense checks verified monthly totals, overview arithmetic, pagination, categories/archives, classification snapshots, edits/deletes, retries, ownership and audit atomicity. Fictional owners/records were rolled back without editing personal records. Live health, overview, income, expense and category API routes all return HTTP 200 through Vite; the server serves the updated navigation. Separate test-database credentials remain unconfigured. These rollback checks do not claim an isolated database suite. Visual browser inspection was unavailable because the browser access host could not connect.

Next milestone: savings goals and the savings ledger, then allocation planning and richer dashboard progress. Login remains deferred. Automatic recurring income/expenses are not implemented; record each payment once when received or spent. Do not scaffold all product modules at once.

See [Windows setup](docs/DEVELOPMENT.md) for prerequisites and the proposed commands for both laptops.
