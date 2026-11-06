# Proposed gamification rules

Status: design for review. Basic badges are MVP; XP, levels, lessons and challenges are Phase 4. Rule values below are initial product choices to evaluate during personal testing, not implemented behavior.

## Principles

Reward understanding, preparation and repeatable habits. Never grant points according to salary, absolute wealth, transaction size or number of repeated entries. Do not use leaderboards, daily pressure, purchase rewards, lost levels, or penalties for withdrawals/missed plans. An emergency withdrawal is a valid use of savings.

All awards are server evaluated, traceable and idempotent. Self-reported data cannot be verified as real money; avoid incentives to fabricate it and make no verification claims.

## Basic MVP badges

| Badge | Trigger | Repeat behavior |
| --- | --- | --- |
| First Step | First valid named savings goal created | Once per user; reserve setup alone does not count |
| First Savings | First non-opening contribution recorded | Once per user, irrespective of amount |
| Goal Champion | First named goal reached through recorded contributions | Once per user; reopening/recompleting does not repeat |

Opening balances do not earn contribution/completion rewards. A goal already funded at creation does not award Goal Champion merely because its target is below its opening funds. The completion rule must observe an actual qualifying contribution crossing a target that was above the prior balance. Lowering a target alone does not earn completion rewards.

## Phase 4 XP catalog

| Meaningful action | Proposed XP | Uniqueness / limits |
| --- | --- | --- |
| First goal created | 25 | Once per user |
| First recorded contribution | 25 | Once per user; excludes openings/corrections |
| First goal completed | 50 | Once per user; same crossing rule as badge |
| Introductory lesson passed | 20 | Once per user/lesson; re-taking gives feedback only |
| Emergency 25% milestone | 30 | Once per user for this milestone, across target changes |
| Emergency 50% milestone | 30 | Once per user for this milestone |
| Emergency 100% milestone | 40 | Once per user for this milestone |
| Realistic monthly savings plan met | 30 | Once per user/calendar month, maximum 12 yearly |
| Approved challenge completed | 20 | At most one rewarded challenge per user/month initially |

Snapshot an emergency target when the user first records a qualifying contribution; milestones use that reward basis. An explicit later change can update planning progress but cannot reset earned milestone identities. Opening funds alone never trigger milestone XP. Rules must not create XP by repeated goal creation/deletion, withdrawals followed by re-contributions, ledger corrections, or toggling target amounts.

Monthly plan rewards use a positive plan committed by the seventh local calendar day, frozen for reward evaluation. Normal plans remain freely editable for personal use. Evaluate only after month close, using net ordinary savings and excluding openings. Users with missing/nonpositive estimated capacity simply skip this optional reward; they still have learning and planning rewards. Changes to past data recalculate reporting but do not repeatedly re-earn historical rewards. A correction is not a reward action. Introduce an evaluation record unique per user/month and rule version with the award evidence when this feature is built.

Store XP as an event sum, not an incremented client counter. Badge and XP checks run explicitly inside the originating transaction; unique constraints prevent races and retries. A rule revision does not automatically re-award an existing one-time action. Notifications are shown only after commit. Historical corrections retain earned awards with evidence marked corrected if necessary; do not shame users or subtract XP.

## Levels

| Level | Title | Lifetime XP threshold |
| --- | --- | --- |
| 1 | Savings Starter | 0 |
| 2 | Smart Saver | 100 |
| 3 | Consistent Saver | 250 |
| 4 | Savings Explorer | 500 |
| 5 | Financial Goal Achiever | 850 |
| 6 | Savings Champion | 1,300 |

Titles are playful labels, not certifications of financial security. Users progress through learning and habits without needing a high salary. Revisit thresholds during testing if progression is too slow or encourages busywork. Show progress toward the next threshold, keep maximum level behavior explicit, and never reset XP each month.

## Later badges and challenges

Emergency Ready: first qualifying 25% emergency milestone. Travel Explorer: first travel goal completion. Consistent Saver: three consecutive closed months with a realistic committed plan met; a missed month starts a new possible sequence but never removes earlier awards. Knowledge Builder: complete the introductory lesson set. Each is a one-time user award.

Examples of opt-in challenges: choose a comfortable amount to save within a week, make an emergency plan, review a week's spending, or finish a lesson. ₹500 can be an example, never a mandatory target. Explain evidence, duration and affordability before joining. Freeze target/rule/version for an enrollment. The server evaluates savings using the ledger; the client cannot post “completed=true.” No skipping essentials, borrowing to save, arbitrary repeated entry rewards, or purchased boosts.

## Verification requirements

Test same-event retries, concurrent awards, goal deletion/recreation, opening balances, target reductions, backdated corrections, zero income, completed-goal withdrawals, lesson retries, enrollment duplicates, monthly boundaries and leap years. Verify no rewards depend on a high income or contribution amount, and no XP is removed for emergency use. Test notifications after successful commit and absence after rolled-back operations.
