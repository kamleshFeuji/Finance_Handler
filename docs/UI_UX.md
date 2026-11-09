# Proposed UI and dashboard

Status: responsive onboarding, profile editing, income/expense tracking and basic Overview are implemented. Returning users open Overview; navigation explicitly offers Overview, Income, Expenses and Profile. Profile estimates are labelled as planning inputs and link to actual entry screens. Overview has income/expense/remainder cards and recording shortcuts. Expense history has monthly type/category totals, add/edit/delete forms and a category manager with archive/restore. Navigation uses two columns on narrow screens. The larger savings dashboard wireframe below remains a future design. Registration/login are omitted.

## Visual direction

Use a calm light canvas, dark navy text, teal for ordinary progress, and restrained warm accents for achievements. Soft cards, generous spacing, system fonts, short labels, and simple line icons keep the product approachable. Validate final foreground/background contrast during implementation; color choices here are directions, not an audited palette.

Show one suggested next step, not a wall of game notifications. Say “You set aside ₹500” and “You can adjust this month's plan.” Avoid “failed,” negative streak messages, wealth rankings, and charts that imply investment growth.

## Navigation and pages

| Destination | Main content | MVP? |
| --- | --- | --- |
| Dashboard | Current month summary, progress, trend and next action | Yes |
| My Savings | Pockets, monthly planner, emergency setup, ledger history | Yes |
| Financial Goals | Goal list/detail, contribution/withdrawal/correction forms | Yes |
| Money / Expenses | Expense and Income tabs, quick entry, filters | Yes |
| Challenges | Opt-in realistic habits | Phase 4 |
| Achievements | Earned/available badges, later XP/levels | Basic badges |
| Learn | Short lessons, quizzes, learning progress | Phase 4 |
| Profile and Settings | Nickname, estimates, preferences and sign-out | Yes |

Desktop: sidebar plus top bar with month selector and quick actions. MVP navigation includes only implemented pages; do not show broken placeholder links. Mobile: bottom navigation for Home, Savings, Add, Goals and More. More contains Money, Achievements, Settings and later Learn/Challenges. The Add button opens an accessible choice between income, expense and savings; no unlabeled floating icon.

## Initial dashboard wireframe

The amounts below are fictional design examples only.

```text
┌───────────────────────────────────────────────────────────────────────────┐
│ SaveQuest          Hello, Alex         [November 2026 ▾]   [Quick add +]   │
├──────────────┬────────────────────────────────────────────────────────────┤
│ Dashboard    │ Your next step: choose a comfortable savings plan          │
│ My Savings   │ [Review this month's plan]                                │
│ Goals        ├───────────────────┬───────────────────┬────────────────────┤
│ Money        │ Income ₹40,000    │ Expenses ₹25,000  │ Remainder ₹11,000  │
│ Achievements │ Recorded so far   │ Needs + enjoyment │ After net savings  │
│ Settings     ├───────────────────┴───────────────────┴────────────────────┤
│              │ Plan ₹6,000   |   Net saved ₹4,000   |   Savings rate 10% │
│              │ Contributions ₹5,000 · Withdrawals ₹1,000                 │
│              ├────────────────────────────┬───────────────────────────────┤
│              │ Emergency pocket           │ Your goals                    │
│              │ ₹18,000 / ₹90,000          │ Laptop  █████░░░  62%         │
│              │ ███░░░░░░░ 20%             │ Travel  ███░░░░░  35%         │
│              │ [Add savings] [History]    │ [View goals] [New goal]       │
│              ├────────────────────────────┼───────────────────────────────┤
│              │ Six-month net saving trend │ Small steps count             │
│              │ [Chart + data table]       │ First Step badge earned       │
│              │ Missing history explained  │ [See achievements]            │
└──────────────┴────────────────────────────┴───────────────────────────────┘
```

Mobile order: greeting/month → next action → compact income/expense/remainder summary → savings plan and actual → emergency → active goals → trend → badges. Cards stack at narrow widths; money amounts must not truncate. A screen with no records has no fictional amounts and offers “Add your first entry” or “Create a goal.” Months with no entries say “No entries recorded”; they do not claim the user earned or spent nothing.

Phase 4 adds a small level/XP strip and at most one active challenge summary. The MVP does not show arbitrary XP or a simulated level.

## React structure

```text
src/
  app/
    App.jsx, AppShell.jsx, routes.jsx, SessionProvider.jsx
  api/
    client.js, auth.js, finances.js, savings.js, dashboard.js
  components/
    Button.jsx, FormField.jsx, MoneyInput.jsx, DateInput.jsx
    Dialog.jsx, ProgressBar.jsx, StatusMessage.jsx, EmptyState.jsx
    LoadingState.jsx, ErrorState.jsx, Pagination.jsx
  features/
    auth/           LoginPage, RegisterPage, ProtectedRoute
    onboarding/     OnboardingPage, IncomeStep, PrioritiesStep
    dashboard/      DashboardPage, SummaryCard, SavingsTrend
    finances/       MoneyPage, IncomeForm, ExpenseForm, EntryList
    savings/        SavingsPage, AllocationPlanner, EmergencyPlanner
    goals/          GoalsPage, GoalDetailPage, GoalCard, TransactionForm
    achievements/   AchievementsPage, BadgeCard
    profile/        ProfilePage
    # Later: challenges/, education/, simulator/
```

Keep domain hooks next to features and API requests outside presentation components. Store filter state in URL search parameters where useful. Fetch server summaries rather than recomputing balances from one paginated history page. Start with explicit refresh after mutations; avoid speculative optimistic balance updates.

## Form and interaction behavior

- Savings contribution form asks amount, date, destination and optional note. Withdrawal form explains the effect without discouragement. Show server-confirmed values after submission.
- Disable duplicate submit while pending and send an operation idempotency UUID. Preserve it across retry after an uncertain network response. Keep the form input when validation fails.
- Expense entry defaults to today in the user's configured timezone; selecting a category suggests essential status but the user can change it.
- Plans explain “planned” and “recorded.” Show a warning if the plan exceeds estimated capacity and let users revise assumptions. Never silently create actual entries from a plan.
- Show loading, empty, error and success states separately. Announce asynchronous outcomes through a polite live region. A failed fetch must never look like a zero balance.
- Confirm destructive income/expense deletion with the entry description; corrections show original and replacement side by side before submission.

## Accessibility acceptance

Use semantic headings, landmarks, a skip link, real buttons, associated labels, fieldsets for related questions, useful error text and visible focus. Dialogs trap and restore focus and close with Escape when safe. All actions work by keyboard; target areas are comfortably touchable. Aim for WCAG AA contrast (4.5:1 normal text, 3:1 large text and relevant UI boundaries).

Progress bars expose accessible labels/values; reserve pockets without targets use balance text rather than a meaningless percentage. Charts have a text summary and data table. Information is never communicated by color alone. Test at 320px width, tablet, desktop and 200% zoom. Respect `prefers-reduced-motion`; progress transitions are short, and celebrations never flash or block entry. Badge notifications must not interrupt keyboard focus.
