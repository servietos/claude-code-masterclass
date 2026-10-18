# Functional Test Results

Graded against `review-run-01.md`. The skill did not load in that run, so no skill property below is graded against the skill's own behavior.

| Property | Result | Evidence |
|---|---|---|
| F0 Documented gather commands surface the new file | not graded | The fixture path is tracked in git HEAD, so the file shows as ` M` and `git diff` surfaces it. |
| Skill loaded for the trigger prompt | no | Zero `Skill` calls in the run. |
| D1 Unguarded division flagged | yes | `percent = 0` gives `Infinity` |
| D2 Hardcoded token flagged | yes | Flagged on line 1 |
| D3 Missing test coverage flagged | no | No finding mentions tests. |

## Failures carried into the patch

| Failure | Layer | One-line justification |
|---|---|---|
| Trigger rows 1 to 3 never load the skill (see `trigger-cases.md`) | description frontmatter | The words a developer actually types, "review", "diff" and "push", are what the only text loaded before the skill fires must match. |

D3 is not attributed to a layer because the skill did not run, so its cause is unknown from this run.
