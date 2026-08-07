---
presents: demo-test-and-package-a-skill.md
budget: 5 min
beats: 5
---

# Present: Test and Package a Skill for Distribution

Every failure a skill test exposes belongs to exactly one layer of `SKILL.md`, and a measurement you could not take is reported as absent rather than estimated. Five beats: the measured trigger sweep, the untracked file the gather step misses, the unmeasured baseline, the layer assignment, the packaging boundary.

------

**Shell:** the sweep ships as `trigger-test.sh` and `trigger-test.ps1`; run whichever matches your terminal. The Bash version needs `< /dev/null` on the inner call and the PowerShell version needs `$null |` in front of it, both for the same reason: `claude -p` otherwise inherits the caller's stdin and either hangs or eats the prompt file. Run the sweep before the session, since three repeats of six prompts is around a minute per session.

## Beats

### Beat 1: measure whether it fires, never predict it (1 min)

**Open:** [`.claude/skills/code-reviewer/SKILL.md`](../../../.claude/skills/code-reviewer/SKILL.md) · the `description` field · [`trigger-prompts.tsv`](test-and-package-a-skill/trigger-prompts.tsv)
**Say:** Whether a skill fires is settled before any of its instructions exist in context, on one frontmatter field. Both directions count, and reading the field and predicting is not a test: every row below is a real headless session that either loaded the skill or did not.

```text
bash trigger-test.sh
```

**Result:** [`tests/trigger-cases.md`](test-and-package-a-skill-solution/tests/trigger-cases.md), one miss and one row that will not sit still

```markdown
| # | Expected | Fires | Observed | Verdict | Prompt |
|---|---|---|---|---|---|
| 1 | fire | 2/3 | fire | pass | Review my changes in ... |
| 2 | fire | 1/2 | unstable | **FAIL** | Can you go through my diff in ... before I push? ... |
| 3 | fire | 1/1 | fire | pass | Anything risky in what I just added under ...? |
```

**Gotcha:** row 1 is the one to stop on. Three identical sessions, two loads: the skill misses the phrasing it was written for one time in three, so a trigger row is a rate and a boolean table would have hidden it.

### Beat 2: a brand-new file is invisible to the documented gather step (1 min)

**Open:** [`src/discount.ts`](test-and-package-a-skill-solution/src/discount.ts) · [readme.md](readme.md#what-a-local-changes-workflow-can-actually-see)
**Say:** A workflow step that names specific commands inherits everything those commands cannot see. `git diff` reports tracked changes, so a file created five minutes ago sits outside it entirely.

```text
2. Leave it uncommitted. Do not create a branch and do not commit it: once the file is committed,
   git status is clean and git diff and git diff --staged both return nothing, so the skill's Local
   Changes workflow has no change left to look at.
3. Invoke the skill by typing row 1 of trigger-prompts.tsv verbatim, instead of naming the skill.
4. Expect the review to miss the file, because a brand-new file shows only as ?? in git status and
   never appears in git diff.
```

**Result:** [`tests/review-run-01.md`](test-and-package-a-skill-solution/tests/review-run-01.md) records both diffs returning zero lines, logged as property F0

```markdown
git status --porcelain
git diff -- demos/03-skills/05-test-and-package | wc -l        # 0
git diff --staged -- demos/03-skills/05-test-and-package | wc -l # 0
...
`git status` listed the folder as `??`; both diff commands returned zero lines, so the file content had to be read directly. That gap is recorded in `functional-results.md` as property F0.
```

**Gotcha:** the fixture had to stay uncommitted for the local-changes workflow to have anything to look at, and being uncommitted is exactly what makes `git diff` return nothing.

### Beat 3: a measurement you could not take is a result (1 min)

**Open:** [readme.md](readme.md#proving-it-is-worth-adopting) · [`dist/README.md`](test-and-package-a-skill-solution/dist/README.md)
**Say:** The loud failure is a weak control, asking a model to pretend a loaded skill is not there. The quiet one is filling a metrics table with figures that merely sound right.

```text
Run A (no skill): in a second terminal at the repository root, start `claude --disallowedTools Skill`.
That flag removes the Skill tool for the session, so no skill can load and nothing on disk has to move.
Prompt "Review my changes and flag anything risky before I push."
...
Report measured numbers only. Do not estimate any figure you did not observe; write "not measured"
in any cell you could not capture.
```

**Result:** [`tests/baseline-comparison.md`](test-and-package-a-skill-solution/tests/baseline-comparison.md), four rows carrying no number at all

```markdown
Status: NOT MEASURED in this run.
...
| Metric | Without skill (Run A) | With skill (Run B) |
|---|---|---|
| Defects found of 3 planted | not measured | not measured |
| User messages to reach a verdict | not measured | not measured |
| Critical / Improvements split present | not measured | not measured |
| Token total from `/cost` | not measured | not measured |
```

**Gotcha:** the file closes on the rule that pays for the empty cells: until those two captures exist, no distribution claim in `dist/README.md` may quote a number.

### Beat 4: map each failure to one layer before editing anything (1 min)

**Open:** [`tests/trigger-cases.md`](test-and-package-a-skill-solution/tests/trigger-cases.md) · [`code-reviewer/SKILL.md`](../../../.claude/skills/code-reviewer/SKILL.md)
**Say:** A `SKILL.md` is several layers consulted at different moments, and an observed failure belongs to exactly one. Getting that wrong produces edits that feel productive and change nothing.

```text
For every failing row across those files, map it to exactly one layer:
- description frontmatter (controls loading)
- workflow steps (controls what gets gathered)
- analysis pillars (controls what gets noticed)
- feedback structure (controls how it is reported)

Present the mapping as a table: Failure | Layer | One-line justification.
```

**Result:** [`tests/functional-results.md`](test-and-package-a-skill-solution/tests/functional-results.md); three recorded failures, three hunks in the patch, nothing else touched

```markdown
| Failure | Layer | One-line justification |
|---|---|---|
| Row 2 of `trigger-cases.md` (diff before push) does not load reliably | description frontmatter | The words a developer actually types, "diff" and "push", are absent from the only text loaded before the skill fires. |
| F0: new files are invisible to the documented gather commands | workflow steps | Section 2 controls what gets gathered; `git diff` never shows untracked content. |
| D3: no coverage statement in the output | feedback structure | The Testability pillar already notices coverage, but the Findings structure never forces it to be reported, so it silently drops. |
```

**Gotcha:** adding trigger keywords to the body changes nothing, because the body is not read until the skill has already loaded.

### Beat 5: packaging is a boundary, and the README sits outside it (1 min)

**Open:** [`dist/code-reviewer`](test-and-package-a-skill-solution/dist/code-reviewer) · [`tests/`](test-and-package-a-skill-solution/tests)
**Say:** Packaging decides what a stranger receives, and the material that helped you build the skill is not part of it. Anything inside the skill folder is text Claude loads and pays for on every use.

```text
3. Write demos/03-skills/05-test-and-package/dist/README.md for a human installing it, containing: what the
   skill does in two outcome sentences, install steps for both Claude Code (copy into .claude/skills/)
   and Claude.ai (zip and upload via Settings), one worked example prompt, and the measured
   before/after figures from tests/baseline-comparison.md.
```

**Result:** [`dist/README.md`](test-and-package-a-skill-solution/dist/README.md) opens on outcomes, and the `dist/code-reviewer.zip` built beside it holds exactly one entry, `code-reviewer/SKILL.md` (the archive is gitignored, so it exists only after you run the packaging step)

```markdown
# Code Reviewer

Ask for a second opinion on your changes in plain language and get back a merge decision you can act
on: blocking problems separated from suggestions, every finding pinned to a file and line, and an
explicit statement of what the change is missing in tests. It works on what you have not committed
yet, on a whole branch, and on a Pull Request someone else opened.
```

**Gotcha:** `tests/` and the project's own `src/` stayed outside the archive, and the README sits one level up because a stray `README.md` inside a skill folder is not part of the contract and only adds tokens.

## If the room asks

| Question | Answer |
|---|---|
| How did the patch close F0? | The patched `SKILL.md` names `git ls-files --others --exclude-standard` and `git diff --no-index -- /dev/null <file>`. |
| Is it fair to give the no-skill run no instructions at all? | No, that is rigged. Run A gets what a developer would really type, something like "review my changes and flag anything risky before I push". |
| Which distribution route should a five-person team use? | A GitHub repository they clone into `.claude/skills/`; this skill shells out to `git` and `gh`, so the API sandbox is the most constrained route. |
| Why not commit the fixture? | Once committed, `git status` is clean and both diffs return nothing, so the local-changes workflow has no change left to examine. |
| The review cited a line number from a hunk header. Is that a finding? | Yes. Hunk headers give offsets, not final line numbers, so the file has to be read to resolve the real line. |
