# SaveQuest coding-agent instructions

## Current approval boundary

The project owner approved the architecture on 6 November 2026, single-user onboarding on 7 November 2026, and income tracking on 9 November 2026. The owner subsequently authorized expense tracking and clearer UI navigation/overview. Registration/login remain deferred. Work incrementally; goals and savings ledger follow expenses. Do not deploy or publish without explicit permission.

## Product and stack

- Make financial planning understandable, encouraging, and realistic for beginners.
- Use React **JavaScript**, Vite, custom CSS, Recharts, Python, Django, DRF, and PostgreSQL.
- Current mode uses one server-selected local profile, no registration/login. Gate profile APIs behind local-only settings, validate loopback clients/hosts, and keep CSRF protection even for anonymous writes. Multi-user authentication is deferred; never put authentication tokens in localStorage.
- Use only free/open-source development tools and local services; no mandatory cloud accounts.
- Do not introduce TypeScript, Next.js, Redux, Docker, Redis, Celery, microservices, or major dependencies without an approved demonstrated need.
- Keep the product name configurable when implementation begins.

## Working process after approval

1. Inspect existing files and relevant documentation before editing.
2. Explain the focused feature being implemented; deliver incrementally.
3. Preserve working code and user changes; never delete existing data without explicit approval.
4. Keep business calculations authoritative in backend services and use Decimal for money.
5. Select the current local owner on the server; never trust a client-supplied owner. Add authenticated ownership when multi-user mode is explicitly introduced.
6. Use transactions and row locks for savings mutations and related reward updates.
7. Record savings movements once. Plans, opening balances, income, and expenses have distinct meanings.
8. Commit migrations and dependency lockfiles; do not commit credentials, local environments, backups, logs, or real financial records.
9. Update documentation to reflect actual implementation, distinguishing proposed and shipped features.
10. Write and run relevant Django/PostgreSQL and Vitest/RTL tests. A module is incomplete until its main tests pass. Report failures and unrun checks honestly.
11. Use accessible labels, keyboard controls, clear validation, responsive layouts, and reduced-motion support.
12. Never penalize necessary expenses, missed targets, low income, or emergency withdrawals. Reward meaningful actions, not transaction frequency or monetary size.

Use feature branches, focused commits, and reviewed pull requests. Both developers must be able to reproduce setup independently with separate databases. Seed only fictional records and never reset a database implicitly.
