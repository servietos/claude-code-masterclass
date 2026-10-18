# Reaudit

## Runs to an empty proposed diff

The proposed diff became empty on the third audit run. Runs one and three covered the whole folder (`.`). Run two covered only `.claude/skills/invoice-summary`.

| Run | Scope | Findings | Flags | Proposed diff |
|---|---|---|---|---|
| 1 | `.` (whole folder) | 13 | 5 | 14 hunks |
| 2 | `.claude/skills/invoice-summary` | 6 | 3 | 6 hunks |
| 3 | `.` (whole folder, after applying the run 1 and run 2 hunks) | 0 | 4 | empty |

Run 1 findings were 10 in Group 1 and 3 in Group 2. Run 2 findings all also appeared in run 1. Run 3 found no high or medium findings. Its one grep hit was trigger text in `invoice-reviewer.md:3`, which the audit keeps by design.

## Flags that remain after run 3

- **Reviewer coverage:** The reviewer reports only the three rules in `docs/review-checklist.md`, so defects outside those rules go unreported. This is a recall choice for you to make, and the audit cannot settle it.
- **"Do not hallucinate" (`SKILL.md:18`):** It restates a trained default. Removing it is low confidence, so it stays.
- **Model-side totals (`SKILL.md`):** The model still totals invoices, although `totalCents` in `src/invoices.ts` already does the arithmetic. Moving the work into code would change the skill's design, which you have not asked for.
- **`pointers.md` (outside the prompt surface):** Its rows for `npm run verify`, `Jest` and `docs/review-rules.md` no longer match the surface. It is checker output, so I left it unedited.

Flags 1 to 3 from run 1 (the 80-word versus 40-word conflict, the `verify` script, and the review path) were resolved by the applied diff, so they are not listed above.

## Last run's summary line

Run 3 ended with this line, quoted exactly:

> Result: the surface is clean. No high or medium findings, so no diff is proposed.
