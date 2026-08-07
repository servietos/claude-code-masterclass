# Functional Test Results

Graded against `review-run-01.md` (pre-patch) and re-graded after the patch described in `../SKILL.md`.

| Property | Present (yes/no) | Evidence quoted from the review |
|---|---|---|
| F0 Documented gather commands surface the change | ~~no~~ -> yes (patched) | Prior run: "both diff commands returned zero lines, so the file content had to be read directly". Patched `SKILL.md` now names `git ls-files --others --exclude-standard` and `git diff --no-index -- /dev/null <file>`. |
| P1 Summary section | yes | "### Summary ... One new file introduces a percentage discount helper" |
| P2 Critical tier | yes | "**Critical**" with two entries |
| P3 Improvements tier | yes | "**Improvements**" with two entries |
| P4 Nitpicks tier (optional) | yes | "`fixtures/discount.ts:4` - `factor` is an indirection over `percent / 100`" |
| P5 Conclusion is Approved or Request Changes | yes | "Request Changes. The hardcoded credential alone blocks merge." |
| P6 Every finding cites `file_path:line_number` | yes (with caveat) | All six findings open with `fixtures/discount.ts:<n>`. Caveat: absolute line numbers were available only because the file was read whole; a `git diff` hunk header gives the reviewer offsets, not final line numbers. |
| P7 Explains why, not just what | yes (human-graded) | "rotating it means a code change plus a redeploy" |
| P8 Constructive, professional tone | yes (human-graded) | No mechanical grader; read by hand and judged constructive. |
| D1 Unguarded division flagged | yes | "`percent = 0` does not throw in TypeScript; it yields `Infinity`, so `applyDiscount(100, 0)` returns `0`" |
| D2 Hardcoded token flagged under Critical | yes | "a bearer token is hardcoded as a module constant (`sk-live-4f9c21ab7d0e`)" |
| D3 Missing test coverage flagged | ~~no~~ -> yes (patched) | Prior run: no finding mentioned tests at all, even though the Testability pillar exists, because the Findings structure has no bucket that forces a coverage statement. Patched `SKILL.md` now requires an explicit coverage line in every review. |

## Failures carried into the patch

| Failure | Layer | One-line justification |
|---|---|---|
| Row 2 of `trigger-cases.md` (diff before push) does not load reliably | description frontmatter | The words a developer actually types, "diff" and "push", are absent from the only text loaded before the skill fires. |
| F0: new files are invisible to the documented gather commands | workflow steps | Section 2 controls what gets gathered; `git diff` never shows untracked content. |
| D3: no coverage statement in the output | feedback structure | The Testability pillar already notices coverage, but the Findings structure never forces it to be reported, so it silently drops. |

Nothing else was flagged by a test, so nothing else was edited.
