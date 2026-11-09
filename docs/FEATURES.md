# Product understanding and scope

Status: onboarding/profile, income, expense/category tracking and a basic monthly overview are implemented. Registration/login are deferred. Goals, savings ledger, richer dashboard and rewards below remain planned.

## Vision and core problems

SaveQuest is a friendly savings companion for students, first-time earners, young professionals, and people with irregular income. Its core loop is: understand your situation → choose a realistic plan → record money set aside → see progress → learn something useful → adjust without shame.

| User problem | Product response |
| --- | --- |
| “I don't know where to begin.” | Short optional onboarding with a clear explanation for every question |
| “I can see transactions, but don't know what to save for.” | Savings pockets for emergencies, security, experiences and personal goals |
| “Long-term goals feel distant.” | Small milestones, visible progress, optional realistic monthly plans |
| “My income changes each month.” | Actual income entries plus optional estimates; revise plans each month |
| “Saving feels like giving up enjoyment.” | Explicit room for hobbies/travel and user-controlled priorities |
| “I missed a target or needed emergency money.” | Supportive recalculation, no punishment, no lost XP |
| “Financial terms are confusing.” | Plain labels and small contextual explanations; lessons later |

The application records what users tell it. It does not move money, connect to banks, maintain tax accounts, recommend securities, or verify balances.

## MVP journeys and acceptance criteria

1. **Open your local space.** No registration/login. The backend selects one internal owner. Profile APIs require local mode, loopback access and CSRF protection for writes. Multi-user authentication is deferred.
2. **Onboard in small steps — implemented.** Nickname; income type including irregular; optional monthly income, essentials and existing-savings estimates; primary priority and free-text goal ideas. Every question can be skipped. Missing estimates differ from zero. Save, refresh and edit from a summary. Existing savings remains an estimate until explicit conversion during the ledger milestone; onboarding creates no actual money entries or goals.
3. **Record income and expenses — implemented.** Add, edit, confirm deletion and browse by calendar month with pagination and whole-month totals. Income sources include salary, freelance, allowance and other. Expenses support standard/custom categories, essential/optional status, category summaries and archive/restore. Actual dates cannot be future; amounts must be positive with at most two decimals. Retries do not add money twice, stale edits/deletes are rejected, and profile estimates never count as transactions.
4. **Plan savings.** Default and custom savings pockets, per-goal monthly allocations, editable plans, and clear plan-versus-actual totals. Suggestions fit the user's estimated remaining capacity after needs and chosen enjoyment budget. Never equate a plan with saved money.
5. **Create a goal and record progress.** Name, pocket, target, optional date; recorded contributions and withdrawals; goal history and correction workflow. Handle target-less category reserves, overfunding, multiple goals, and withdrawals from completed goals.
6. **Build an emergency pocket.** User chooses essentials and coverage months; preview target, set it, record savings and withdrawals. No penalty for using it. This is a simple goal variant in MVP, not a separate money model.
7. **Understand your month — basic Overview implemented.** Returning users see recorded income/expenses, remainder before savings, essential/optional spending and category totals. Buttons lead directly to the income/expense screens; estimates remain on Profile. Negative remainders are allowed and explained without shame. Savings plans/rates, emergency progress, goals, badges and six-month trends remain future dashboard enhancements. Never show invented sample records as real data.
8. **Earn basic badges.** First goal, first recorded contribution, first completed goal. Awards are idempotent and amount-independent. A completed goal can reopen without removing its earned badge.
9. **Adjust profile — basic editing implemented.** Edit onboarding answers or cancel edits. Currency is INR for the first version. No logout in local mode. Future target/estimate changes must clearly explain their planning effects.

Manual entries and recurring-pattern labels can be supported first. Automatic recurring entry generation, future schedules, and sophisticated recurrence editing are deferred to avoid phantom actual transactions.

## Future enhancements

Phase 4 adds XP and levels, opt-in challenges, milestone notifications, emergency/travel/consistency/learning badges, short reviewed lessons and quizzes, and a deterministic simulator. Later work may add confirmed recurring templates, personal CSV export, and optional reminders if testing demonstrates value. No external financial integrations or promised returns are planned.

Simulator assumptions: no interest or inflation by default; fixed user-entered contributions, whole calendar months, no automatic income changes. Required months = ceiling of remaining target / monthly contribution when contribution is positive; zero contribution produces “No completion estimate.” Show baseline versus scenario, capacity warnings, and the assumptions. Scenario inputs never write actual savings or award XP. Interest/inflation may appear in clearly separate educational examples later.

Education begins with why save, needs/wants, emergency funds, budgeting, goal setting, saving/investing, inflation, and compound interest. Examples and quizzes require content review before release. No personalized investment recommendations.

## Deliberately outside initial scope

Bank syncing, payments, investing/trading, credit scoring, taxes, household shared accounts, foreign-exchange conversion, public leaderboards, subscriptions, social feeds, cloud hosting, and complex notifications. Product name is a configurable display value; changing it must not change database identifiers or API URLs.

## Success measures during three-month personal testing

Track through the developers' private notes first: time to record an expense/contribution, whether both people can explain planned versus actual savings, calculation defects, confusing labels, progress visibility, and whether users feel pressured by rewards. Success is sustainable understanding and usable records; higher savings totals or daily streaks alone are not a product success measure.
