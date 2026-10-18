# Summary

| Grader | v0 | v1 | v1b | v2 |
|---|---|---|---|---|
| `version-heading` | 0 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `features-heading` | 0 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `fixes-heading` | 1 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `no-merge` | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `read-commits` | 3 of 3 | 3 of 3 | 3 of 3 | 3 of 3 |
| `notes-only` | not graded | not graded | 0 of 3 | 3 of 3 |
| runs with an error | 0 | 0 | 0 | 0 |
| with-arm score | 0.47 | 1.00 | 0.83 | 1.00 |

Final skill, both refinements promoted:

```markdown
---
name: release-notes
description: Generate release notes from recent git commits
---

# Release Notes

## When to use

When the user asks for a changelog, release notes, or a summary of recent commits.

## Steps

1. Read `commits.txt`, the output of `git log --oneline -10`.
2. Summarise the commits as user-facing release notes.
3. Return the notes as markdown with exactly this structure: a `# Version` heading, then `## Features` for `feat:` commits and `## Fixes` for `fix:` commits.
4. Return only the notes: nothing before the `# Version` heading and nothing after the last section.
```

Lessons about experiment design:

1. Measure before proposing: `no-merge` already passed in every v0 run, so a merge-exclusion step would have changed nothing measurable.
2. A grader added mid-loop needs its own baseline on the unchanged skill, or the improvement it reports cannot be told apart from the grader's arrival.
3. Read `skill-fired` before the score: a run that never loaded the skill measures the model, not the edit.

Follow-up experiment: `docs:` and `chore:` commits drop out of the notes entirely. Add a grader that
requires the readme change to appear, baseline it on the v2 skill, then propose a `## Other` section.
