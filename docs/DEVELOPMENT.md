# Two-developer workflow and Windows setup plan

Status: the first laptop has a working PostgreSQL connection and applied User/profile migrations. Single-user onboarding, profile summary/edit, local CSRF protection and readiness handling exist. Registration/login are deferred. Actual finance features, seed commands and a separate PostgreSQL test role remain future setup work.

## Independent local environments

Each developer uses Python 3.14, Node 24 LTS (first laptop: 24.12.0), PostgreSQL 18, Git and VS Code. Existing compatible installations are reused. Python, Node, PostgreSQL, Git and the app dependencies are free/open source. VS Code is the requested editor; VSCodium is an optional open-source editor distribution. No paid extension or cloud account is necessary to run SaveQuest.

Use official installers or approved package sources; install them manually if missing. Restart terminals after installation. Ensure PostgreSQL is running locally. Its SQL Shell (psql) or pgAdmin can be used if psql is not on PATH. No global npm package installation is required.

Check prerequisites in PowerShell:

```powershell
py -0p
py -3.14 --version
node --version
npm.cmd --version
git --version
psql --version
```

## First repository setup

Initialize a repository once with `git init -b main` if needed. Do not overwrite an existing repository. A remote GitHub repository is configured only when its owner supplies the intended URL. Local development works without a remote. If Git/Python are not found in an older VS Code terminal, open a new terminal after installation; the first laptop's Python and Git are installed under the user's local Programs folder.

Developer 2 clones the agreed repository using its actual URL, then:

```powershell
Set-Location 'C:\Git and GitHub\SaveQuest'
py -3.14 -m venv backend\.venv
.\backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.lock.txt
.\backend\.venv\Scripts\python.exe backend\scripts\init_env.py
```

On the first laptop, the virtual environment, Python dependencies and backend `.env` are already created. Do not recreate the environment or overwrite `.env`. The bootstrap generates a random Django secret and leaves an existing file untouched. Frontend environment defaults work without a local file; copy `.env.example` to `.env.local` only if customizing public display settings.

VS Code's workspace default Python interpreter points to `backend/.venv/Scripts/python.exe`. If a different interpreter was already selected, use **Python: Select Interpreter** from the command palette and choose that file. Installed first-laptop runtime: Python 3.14.6. Git initialization was declined during setup; no repository, commit or remote was created by the agent.

Using the venv Python executable directly avoids changing PowerShell execution policy. Activation is optional; do not weaken machine-wide policies to run setup.

## Configure PostgreSQL

Run the following as the local PostgreSQL administrator. These commands create a dedicated non-superuser application role and separate database; they do not reuse a production database. Each laptop may use its own password. `\password` prompts interactively so credentials are not embedded in shell history.

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -h localhost
```

Inside psql:

```sql
CREATE ROLE savequest_app LOGIN;
\password savequest_app
CREATE DATABASE savequest OWNER savequest_app;
\q
```

For tests, prefer a separate local test role with permission to create disposable test databases, rather than granting application runtime credentials broader privileges:

```powershell
& 'C:\Program Files\PostgreSQL\18\bin\psql.exe' -U postgres -h localhost
```

```sql
CREATE ROLE savequest_test LOGIN CREATEDB;
\password savequest_test
\q
```

The test settings use this role, connect to the local postgres maintenance database for creation, and create a distinct `test_savequest` database. Never point test settings at personal or shared production data. Test role credentials stay local and are not runtime defaults. The current readiness unit tests mock the connection and do not create a database; future financial tests require this test role.

The administrator password is the one chosen when PostgreSQL was installed. Do not put that password in the app config or chat. If the role/database already exists, inspect it in pgAdmin before creating anything; do not drop or reset existing data. No roles or databases have been created automatically by the coding agent.

## Environment plan

`backend/.env.example` supplies these placeholder keys (not real values):

```dotenv
DJANGO_SECRET_KEY=replace-with-a-locally-generated-value
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=http://localhost:5173
DB_NAME=savequest
DB_USER=savequest_app
DB_PASSWORD=replace-with-your-local-password
DB_HOST=localhost
DB_PORT=5432
TEST_DB_NAME=test_savequest
TEST_DB_USER=savequest_test
TEST_DB_PASSWORD=replace-with-your-local-test-password
APP_DISPLAY_NAME=SaveQuest
```

The bootstrap script already generated the local secret on the first laptop. For a new clone run it once, then edit the ignored `backend/.env` to set `DB_PASSWORD` and (when needed) `TEST_DB_PASSWORD` to the passwords chosen with `\password`:

```powershell
.\backend\.venv\Scripts\python.exe backend\scripts\init_env.py
```

The Django secret fails fast if unset or still a placeholder. Missing database credentials cause readiness failure; there is no fallback database. `frontend/.env.example` contains only public settings such as `VITE_API_BASE_URL=/api/v1` and `VITE_APP_NAME=SaveQuest`. All `VITE_` values are public build inputs; never put secrets there.

## Apply migrations after configuring the database

```powershell
Set-Location 'C:\Git and GitHub\SaveQuest\backend'
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py migrate
```

The User and profile migrations are applied on the first laptop. On a new laptop run migrations after configuring its own application role/database and password. Migration files synchronize schema, never private records.

### Future seed command

`seed_demo` is not implemented yet. It will be introduced with fictional financial data after those models exist. Its planned invocation is `manage.py seed_demo --username demo_alex`.

Seed command design: explicitly invoked, repeatable, and scoped to a marked fictional account. Prompt for a password; never commit a demo password or reset an existing password on rerun. Use stable seed keys and get-or-create behavior; reruns must not duplicate ledger events or overwrite edits. If the username already belongs to an unmarked user, stop. No delete/truncate/reset behavior. Use fixed documented example dates or an explicit reference-month parameter; reruns must not gradually invent months of new transactions. Defaults/system catalogs can be seeded separately from demo financial records.

Each developer seeds their own database; migrations synchronize schema, not records. Use a second fictional account in tests to prove isolation. Never upload personal database dumps to the repository.

## Start both services

Backend terminal:

```powershell
Set-Location 'C:\Git and GitHub\SaveQuest\backend'
.\.venv\Scripts\python.exe manage.py runserver localhost:8000
```

Frontend terminal:

```powershell
Set-Location 'C:\Git and GitHub\SaveQuest\frontend'
npm.cmd ci
npm.cmd run dev
```

Vite uses `localhost:5173` with strict port selection and proxies `/api` to `http://localhost:8000`. Open `http://localhost:5173`. `npm.cmd` avoids PowerShell's script-policy restrictions without changing execution policy. Do not expose either development server to the LAN by default. Django's normal startup checks migration history, so configure PostgreSQL before starting it.

Connectivity checks (the health endpoint is implemented):

```powershell
Invoke-RestMethod http://localhost:8000/api/v1/health/
Invoke-RestMethod http://localhost:5173/api/v1/health/
```

Both should return `status: ok` and `database: connected` when database setup is complete; otherwise the health endpoint returns HTTP 503 with no raw database errors. Open the frontend to see onboarding, or the saved summary if already completed. Stop only the backend to verify the frontend's connection-error message. Do not stop a shared PostgreSQL service just for this test. Profile writes use a token from `/api/v1/csrf/`; registration/login are not implemented.

## Git collaboration

Use `main` for reviewed stable code and short feature branches such as `feature/goal-contributions`. Before changing a shared model, agree ownership and migration sequence. Commit Django migrations with code, not later. Resolve divergent migrations using Django's merge migration process after reviewing dependencies; never delete applied migrations to make conflicts disappear.

Routine commands once Git is configured:

```powershell
git switch main
git pull --ff-only
git switch -c feature/goal-contributions
git status --short
git diff --check
```

Review files before staging and make focused commits. Push the feature branch to the agreed remote and open a PR when requested. PR includes behavior, migration impact, tests actually run, and screenshots for visual changes. The other developer reviews calculations, ownership, usability and setup before merging. No personal financial examples in issue bodies or screenshots.

After pulling changes, both developers run locked dependency installation when locks changed, then migrations and relevant tests. Never copy `.env`, `.venv`, `node_modules`, or PostgreSQL data directories between laptops.

## Ignore-file coverage

The root `.gitignore` covers `.venv/`, `venv/`, `__pycache__/`, bytecode, test/tool caches, coverage output, `.env`, `.env.*` with explicit inclusion of `.env.example`, `node_modules/`, Vite build output, local logs, editor/OS clutter, private media, local PostgreSQL data and backups (`*.dump`, `*.backup`, local backup directories). Keep migrations, npm lockfile, Python lockfile and safe shared editor settings tracked. SQL is not blanket-ignored, so reviewed support scripts can be committed. Never rely on ignore patterns to protect a file already tracked; inspect staged changes.

## Testing commands and expanding coverage

Current backend readiness tests use SimpleTestCase with a mocked connection; run them without database credentials using the first command below. As features are added, database-backed tests will use PostgreSQL and the dedicated test settings. Normal Django TestCase will cover APIs/services; TransactionTestCase with separate connections will cover real row locks and concurrent withdrawals. Use `Client(enforce_csrf_checks=True)` for authentication/CSRF tests because ordinary test clients can otherwise hide protection defects.

```powershell
Set-Location 'C:\Git and GitHub\SaveQuest\backend'
.\.venv\Scripts\python.exe manage.py test accounts.tests config.tests --settings=config.settings.test
# Once database-backed feature tests are implemented and the test role exists:
# .\.venv\Scripts\python.exe manage.py test --settings=config.settings.test
.\.venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\.venv\Scripts\python.exe manage.py check
```

Frontend tests and build:

```powershell
Set-Location 'C:\Git and GitHub\SaveQuest\frontend'
npm.cmd ci
npm.cmd run test -- --run
npm.cmd run build
```

The current 16 backend tests cover serializers, local-mode access, anonymous CSRF, origin rejection, validation and readiness without requiring a test database. Eight frontend tests cover connection states, skipping fields, saving, editing, cancel, zero/unknown and server validation failures.

Before the first real profile exists, this optional smoke check exercises the real PostgreSQL save/read/update path inside a transaction and rolls back all fictional writes:

```powershell
# From backend; refuses to run if the local account already exists.
.\.venv\Scripts\python.exe scripts\check_onboarding.py
```

Do not rerun this smoke check after saving your profile; use a separately configured disposable test database for further persistence tests. The first-laptop smoke check passed and left no fictional account/profile. Full isolated database tests still require the dedicated test role; they were not claimed as run. Browser visual verification was unavailable because automation could not reliably identify the current URL.

The table below is the expanding feature-test plan, not a claim that these future modules are implemented:

| Area | Required meaningful coverage |
| --- | --- |
| Accounts | Registration validation, login/logout, password handling, CSRF including anonymous login, denied anonymous access |
| Isolation | Other-user list/detail/mutation, foreign categories/goals, dashboard aggregates, transaction correction IDs |
| Income/expenses | Decimal precision, invalid/negative/zero/future inputs, irregular income, edits/deletes/audit, filters, month/year boundaries |
| Savings | Opening exclusion, contributions, withdrawals, overfunding, target-less pockets, reversals/corrections, duplicate requests, ownership, concurrent withdrawals |
| Planning | Missing estimates versus zero, essentials above income, optional enjoyment allowance, monthly totals, emergency multiplication |
| Dashboard | Exact formulas, negative net savings, no income ratio, archived-goal history, trend totals versus ledger, no double counting |
| Rewards | One-time awards, no rewards for openings/target lowering/corrections, concurrency, reopened goals; later XP and challenge rules |
| Frontend | Form interactions, field/server errors, submit retry, loading/empty/error states, routing/session expiry, accessible progress and navigation |

Manual browser review covers the core authenticated journey on mobile/desktop, keyboard navigation, focus, contrast and reduced motion. Do not add test tooling for its own sake. A test is evidence of completion only after it has run and passed; report unavailable dependencies/environment separately.

## Private backups during personal use

Before real data is used, document a local `pg_dump`/`pg_restore` procedure and rehearse restore into a separate database. Store backups outside the Git checkout in a private location; do not send them between developers. Decide retention, device protection and deletion needs before public release. Never test recovery by overwriting the only working personal database.
