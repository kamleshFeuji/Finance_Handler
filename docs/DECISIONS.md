# Review decisions, risks and open questions

Status: architecture approved on 6 November 2026; single-user local onboarding approved on 7 November 2026. Setup uses Python 3.14, Node 24.12.0 and PostgreSQL 18. Working database connectivity and User/profile migrations are verified.

## Recommended defaults

| Topic | Proposed default | Why / tradeoff |
| --- | --- | --- |
| Currency | INR only, two decimal places | Matches brief; avoids misleading cross-currency totals |
| Period | Calendar month; timezone Asia/Kolkata initially, configurable profile timezone | Clear date boundaries; no invented salary-cycle logic |
| Identity | One server-selected local account with unusable password; no login/registration | Explicit owner scope change; local access checks and CSRF remain enforced |
| Goal model | One ledger destination per movement; category aggregates goals/reserves | Prevents duplicated category and goal contributions |
| Savings truth | Auditable append-only savings ledger; opening funds explicit | Corrections cost more design effort but preserve history |
| Plans | Per-goal monthly allocations | Category totals computed once; no conflicting duplicated plans |
| Recurrence | Manual entries first; confirmed templates later | Avoids automatically recording money that never arrived or was spent |
| Rewards | Three basic badges first; XP/challenges after MVP | Tests the savings concept before complex reward rules |
| Runtime | Local monolith and separate databases | Free, reproducible, manageable for two developers |
| Frontend/API | Vite proxy on a single browser origin | Reduces local cookie and CORS complexity |

## Technical risks and mitigations

| Risk | Mitigation / validation |
| --- | --- |
| Confusing available money with recorded estimates | Explicit labels; plans and actuals separate; dashboard explains manual records are not bank balances |
| Double-counted savings | One ledger, required destination, category/goal totals treated as views; test exact aggregate fixtures |
| Concurrent or backdated withdrawals causing negative balances | Goal row locks, atomic services, final running-balance validation and PostgreSQL concurrency tests |
| Cross-user relation leakage | Owner-scoped queries plus relation validation in every write path; tests with two users |
| CSRF gap on anonymous login | Explicit login/registration CSRF enforcement; enforce-CSRF test client and real browser checks |
| Editing targets or records to farm XP | Stable one-time evidence keys, frozen reward bases, no automatic rewards for corrections |
| Repeated imports/seeds/submissions | Scoped seed identities; operation idempotency with payload matching; no implicit reset |
| Financially stressful game mechanics | Amount-independent awards, no rankings or punishments, optional challenges, feedback from both users |
| Dependencies drift between laptops | Same runtime families, committed exact locks, npm ci, migration rehearsal on both machines |
| Existing savings misread as this month's achievement | Opening entry type excluded from monthly flows and reward triggers |
| App expansion delaying a usable product | Small vertical slices; automatic recurrence, simulator and education wait until core money flow works |
| Lost private data during testing | Private backups and tested restore before real use; no sharing live DBs |
| Local registration abuse/password recovery gaps at launch | Local-only first; design throttling, recovery and privacy before any public availability |
| Educational content mistaken for personalized guidance | Plain factual examples, visible assumptions, reviewed content; no promised returns |

## Questions for owner review

The following defaults let planning proceed; they are not blockers for reviewing the architecture:

1. Is INR-only with calendar-month reporting suitable for both developers' first three months?
2. Resolved: owner requested no registration/login for the single-user local application.
3. Should real-money personal testing begin immediately after MVP acceptance, or after the XP/learning enhancement phase? Recommendation: MVP first, then add only rewards that improve actual use.
4. Does either laptop already have a required Python, Node or PostgreSQL version? Confirm before producing locks, not by assuming installations exist.
5. Is the proposed MVP boundary acceptable: manual recurring entries, basic badges, and no XP/challenges/lessons/simulator until Phase 4?
6. How much time can each developer spend weekly? Use this to size milestones after approval; do not promise a calendar delivery date before knowing capacity.

The owner approved the architecture and incremental roadmap, authorizing Phase 2 setup. This does not authorize public deployment or an all-at-once implementation. Product questions can be revisited before their relevant feature milestone.

## Planning and setup verification record

- Read the complete supplied master project brief.
- Inspected the workspace; no pre-existing project files were found.
- Initial restricted-terminal inspection did not find Git or Python. An approved broader check subsequently found both user-installed programs. Node 24.12.0 and a running PostgreSQL 18 service are also installed.
- Consulted official stack, compatibility and CSRF guidance linked in the architecture document.
- After architecture approval, created the Django/React skeleton, Python virtual environment, environment examples/local bootstrap, dependency locks, custom-user migration and readiness screen.
- Three Django readiness tests, three frontend tests, frontend build, Django system checks and Python dependency checks pass. The database is mocked in readiness unit tests; live PostgreSQL authentication and applied migration history remain unverified without the local credentials.
- Verified that the npm lock reproduces the installation using an offline `npm ci`. A real, unmocked readiness request returned the expected HTTP 503 with the unconfigured database credentials and did not expose connection details.
- Git initialization was declined; no Git initialization, commit, or publication was performed.

## Single-user onboarding implementation

The owner chose local single-user operation and authorized onboarding on 7 November 2026. Profile GET/PUT and masked-token CSRF GET are implemented without relaxing global DRF authentication defaults. Local mode is explicit; non-loopback clients and unexpected hosts are denied. No client-supplied owner is accepted. The reserved account has an unusable password, and conflicts with usable or privileged accounts are rejected.

Existing savings is an editable estimate only until an explicit one-time ledger conversion is implemented. Goal ideas are plain text, not actual goals. No XP or recorded financial totals are generated from onboarding estimates. Missing amounts and zero remain distinct; resubmission updates one profile and preserves its original completion timestamp.

Applied profile migration; passed 16 backend tests, 8 frontend tests and production build. A real PostgreSQL smoke check passed and rolled back all fictional writes. Dedicated test-database credentials are not configured, so no isolated database suite was run. Visual browser checking was blocked by the browser automation host's URL-identification safety check; no UI action was performed after that stop.
