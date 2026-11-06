# Incremental development roadmap

Status: architecture approved on 6 November 2026. Local PostgreSQL connectivity and migrations work. Single-user onboarding approved and implemented on 7 November 2026: editable optional estimates/priorities/goal ideas with a saved summary. Registration/login are deferred by the owner. Git initialization was declined. Second-laptop setup remains a future rehearsal. Durations depend on availability; use acceptance gates rather than fixed promises.

| Phase / milestone | Deliverable | Acceptance gate |
| --- | --- | --- |
| 1 — Planning | Architecture, schema/ERD, UI wireframe, scope, rewards, workflow and risks | Owner reviews proposal and approves or requests changes |
| 2a — Reproducible skeleton | Git setup if needed, Python venv, Django config, custom User, React/Vite, PostgreSQL settings, example environments, locks and gitignore | Both laptops install from committed pins; no secrets tracked |
| 2b — Connectivity | Database-backed health endpoint; React calls it through Vite proxy | Connected, backend unavailable and DB unavailable states verified; Django checks and frontend build pass |
| 3a — Authentication deferred | Registration/login omitted for current local single-user app | Revisit only if multiple users or public use are requested |
| 3b — Profile/onboarding implemented | Three optional steps, local owner, estimates/priorities/goal ideas, saved summary/edit | 16 backend and 8 frontend tests pass; real PostgreSQL rollback check passed; browser visual check unavailable |
| 3c — Income/expenses | CRUD, defaults/custom categories, essential flag, audit, filters and pagination | Decimal/date validation, edits/deletes, totals and ownership tests pass |
| 3d — Goals and ledger | Goals/reserves, contributions, withdrawals, history and corrections | No double counting; idempotency, historical overdraft and concurrent withdrawal tests pass on PostgreSQL |
| 3e — Planning/emergency | Monthly goal allocations, capacity preview, emergency target setup | Plans never affect actuals; missing estimates and oversubscribed plans handled clearly |
| 3f — Dashboard/basic badges | Monthly selectors, trend/table, progress, first badges, responsive shell | Formula fixtures, empty/error states, cross-user access and badge retries pass |
| 3g — MVP review | Second-laptop rehearsal, end-to-end manual journeys, privacy check | Both users can complete core loop independently with consistent results |
| 4a — XP/levels | Event catalog, rule tests, XP history and progress | Unique/correct awards, no wealth bias or withdrawal penalties |
| 4b — Challenges/learning | Opt-in challenges, reviewed lessons/quizzes and badges | Affordable enrollment, server completion evidence, retry/correction tests |
| 4c — Simulator/celebrations | Deterministic scenario preview, subtle notifications | Assumptions visible, no stored money mutations, keyboard and reduced-motion checks |
| 5 — Personal testing | Approximately three months of real personal use on separate local setups | Track defects/feedback, reconcile calculations, test private backup/restore; prioritize useful fixes |
| 6 — Public readiness | Separate security/privacy/hosting/recovery/concurrency review | Explicit approval before any deployment or publication |

## Suggested two-developer slices

At each milestone, agree a small API contract first. One developer owns a backend service, migration and tests; the other owns the matching frontend journey and tests. Both review the full vertical feature, then swap roles for the next slice to share knowledge. Avoid simultaneous uncoordinated edits to the same models or settings.

Do not build the whole backend before user flows, and do not construct all frontend screens using fake data and call the feature complete. After onboarding, build one income/expense flow; the next slice is one goal and one contribution. Categories and explicit opening-balance conversion belong to those finance/ledger milestones.

## Definition of done

- Feature meets the agreed acceptance criteria and ownership rules.
- Backend has authoritative financial validation and relevant migration/constraint coverage.
- Main tests pass on the supported stack; frontend build succeeds when frontend changes.
- Loading, validation, empty, error and keyboard behavior work for the feature.
- Documentation and environment examples match shipped behavior.
- Reviewer can reproduce the feature on a separate laptop without copying private data.
- No credentials or real records in the diff, no silent data reset, and no unapproved deployment.

## Personal testing rhythm

Use a weekly short review: compare a few hand-calculated examples with the dashboard, note entry friction, check whether rewards cause pressure, and agree one or two next improvements. Keep personal amounts in private notes, not GitHub issues. At the end of three months assess whether the product is useful before expanding infrastructure or public features.
