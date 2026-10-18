---
presents: demo-test-and-package-a-skill.md
budget: 4 min
beats: 4
---

# Present: Test and Package a Skill for Distribution

Every failure a skill test exposes belongs to exactly one layer of `SKILL.md`, and a measurement you could not take is reported as absent. Four beats: the measured trigger sweep, the untracked file the gather step misses, the layer assignment, the packaging boundary.

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
| 1 | fire | 0/3 | no-fire | **FAIL** | Review my changes in demos/03-skills/05-test-and-package/test-and-package-a-skill. |
| 2 | fire | 0/3 | no-fire | **FAIL** | Can you go through my diff in demos/03-skills/05-test-and-package/test-and-package-a-skill before I push? I do not want to break anything. |
| 3 | fire | 0/3 | no-fire | **FAIL** | Anything risky in what I just added under demos/03-skills/05-test-and-package/test-and-package-a-skill? |
```

**Gotcha:** row 1 is the one to stop on. Three identical sessions and zero loads: the skill never fired on the phrasing it was written for. A trigger row is a rate, so the 0/3 is the finding, and a boolean table would have shown only FAIL.

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

**Result:** [`tests/review-run-01.md`](test-and-package-a-skill-solution/tests/review-run-01.md) records that the fixture path was already tracked in git HEAD, so the file shows as ` M` and `git diff` surfaces it; property F0 is not graded

```markdown
Its path is tracked in git HEAD from an earlier commit of this folder, so `git status` reports ` M` for it, not `??`, and `git diff` shows the change. The premise that a brand-new file is invisible to both diffs does not hold for this path.
```

**Gotcha:** the fixture had to stay uncommitted for the local-changes workflow to have anything to look at, and being uncommitted is exactly what makes `git diff` return nothing. In this repo the path was committed earlier, so the blind spot shows only with a path that was never committed.

### Beat 3: map each failure to one layer before editing anything (1 min)

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

**Result:** [`tests/functional-results.md`](test-and-package-a-skill-solution/tests/functional-results.md); the one failure this run measured, and the skill did not load in that run, so D3 has no layer yet

```markdown
| Failure | Layer | One-line justification |
|---|---|---|
| Trigger rows 1 to 3 never load the skill (see `trigger-cases.md`) | description frontmatter | The words a developer actually types, "review", "diff" and "push", must match the only text loaded before the skill fires. |
```

**Gotcha:** adding trigger keywords to the body changes nothing, because the body is not read until the skill has already loaded.

### Beat 4: packaging is a boundary, and the README sits outside it (1 min)

**Open:** [`dist/code-reviewer`](test-and-package-a-skill-solution/dist/code-reviewer) · [`tests/`](test-and-package-a-skill-solution/tests)
**Say:** Packaging decides what a stranger receives, and the material that helped you build the skill is not part of it. Anything inside the skill folder is text Claude loads and pays for on every use.

```text
3. Write dist/README.md for a human installing it, containing: what the
   skill does in two outcome sentences, install steps for both Claude Code (copy into .claude/skills/)
   and Claude.ai (zip and upload via Settings), one worked example prompt, and the measured
   before/after figures from tests/baseline-comparison.md.
```

**Result:** [`dist/README.md`](test-and-package-a-skill-solution/dist/README.md) opens on outcomes, and the `dist/code-reviewer.zip` built beside it holds exactly one entry, `code-reviewer/SKILL.md` (the archive is gitignored, so it exists only after you run the packaging step)

```markdown
# code-reviewer skill

The code-reviewer skill gives you a structured review of your local changes (staged or working tree) or of a GitHub pull request, covering correctness, maintainability, readability, efficiency, security, edge cases, testability, and project conventions. You get back a summary, findings sorted into Critical, Improvements, and Nitpicks, and a clear Approved or Request Changes verdict with `file_path:line_number` references.
```

**Gotcha:** `tests/` and the project's own `src/` stayed outside the archive, and the README sits one level up because a stray `README.md` inside a skill folder is not part of the contract and only adds tokens.

## If the room asks

| Question | Answer |
|---|---|
| Did the patch close F0? | Not in this run: the patched `SKILL.md` changed only the description, so the `git ls-files --others --exclude-standard` line is still missing. |
| Which distribution route should a five-person team use? | A GitHub repository they clone into `.claude/skills/`; this skill shells out to `git` and `gh`, so the API sandbox is the most constrained route. |
| Why not commit the fixture? | Once committed, `git status` is clean and both diffs return nothing, so the local-changes workflow has no change left to examine. |
