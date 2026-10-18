# Evolve a Skill with Deterministic Experiments

Take an existing skill, measure its quality with `claude plugin eval` and deterministic graders, then run an autoresearch loop (propose a refinement, evaluate it, revert if it regresses) to improve its structure and what it returns.

Each step contains:
- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

> **Prerequisite:** This lab assumes you have already practised the "manual x3, observe, codify" pattern from [Module 03: Creating & Managing Skills](../../demos/03-skills/readme.md). Here we focus on the *measurement* angle that this module frames in [`demos/07-optimize-observability/03-autoresearch-loop`](../../demos/07-optimize-observability/03-autoresearch-loop/readme.md): eval cases, graders, and metric-driven skill refinement.

**Tooling you need before Step 1:** Claude Code 2.1.269 or later (`claude --version`), since `claude plugin eval` arrived there. On Windows the case's scaffold script runs in Git Bash, which Claude Code already requires. There is nothing to install.

You work in [`02-evolution/release-notes-lab/`](02-evolution/release-notes-lab/readme.md), which ships the under-specified skill as a plugin plus the commit log it summarises. The completed reference is beside it in [`02-evolution/release-notes-lab-solution/`](02-evolution/release-notes-lab-solution/readme.md). Build your own suite first and use the solution to check it.

## Where to Open Claude Code

Every prompt below names paths relative to the lab folder (`release-notes/`, `experiments/`), so open Claude Code inside it. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/07-optimize-observability/02-evolution/release-notes-lab
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `release-notes-lab` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

Where the session opens does not decide what an eval run loads. Each run starts a fresh, isolated session in an empty folder with only the plugin under test, so this repo's own `CLAUDE.md`, `.claude/` and `.mcp.json` never reach it.

---

## Setup: Read What Ships

The starter holds the Typer CLI (`hello.py`, `math_utils.py`, `cli.py`, `requirements.txt`) and the plugin you are going to measure in `release-notes/`: a manifest, the skill at `release-notes/skills/release-notes/SKILL.md`, and `release-notes/evals/recent-changes/commits.txt`, the `git log --oneline` of that CLI's history, merge commit included. The skill is deliberately under-specified: no version section, no grouping by type (feature vs. fix), no rule about what to return. It works, and it produces different output on every run, which is exactly what makes it worth measuring.

The commit log ships as a file because an eval run cannot run `git`. A run starts in an empty workspace, and on native Windows a run granted `Bash` or `PowerShell` is refused, since there is no sandbox backend to confine it. The skill therefore reads the log the case copies in.

```text
Read release-notes/skills/release-notes/SKILL.md and release-notes/evals/recent-changes/commits.txt.
Tell me what the skill asks for, which commits the log holds, and which of them are not
user-facing changes.
```

**Expected result:** The skill's three steps (read `commits.txt`, summarise, return markdown), and seven commits: three `feat:`, one `fix:`, one `docs:`, one `chore:`, and `Merge branch 'docs/readme'`.

---

## Step 1: Write the Eval Case and Run the Baseline

**Goal:** Build the measurement before changing the skill. You cannot optimise what you cannot measure.

**Prompt:**

```text
Create an eval case for the release-notes plugin in release-notes/evals/recent-changes/:

  1. prompt.md: frontmatter max_turns: 10 and allowed_tools: [Read, Glob, Grep, Skill];
     body: Use the release-notes skill to write release notes for the recent changes.
  2. case.yaml: schema_version "1.1", name recent-changes, context.scaffold_script fixture.sh.
  3. fixture.sh: a bash script that copies commits.txt from its own folder into the
     current directory: cp "$(dirname "$0")/commits.txt" ./commits.txt
  4. One grader per file in graders/, frontmatter only:
     - skill-fired.md: type tool_used, tool Skill, input_match '"skill"\s*:\s*"(?:[\w-]+:)?release-notes"'
     - read-commits.md: type tool_used, tool Read, input_match 'commits\.txt'
     - version-heading.md: type regex, pattern '^# Version', flags m
     - features-heading.md: type regex, pattern '^## Features', flags m
     - fixes-heading.md: type regex, pattern '^## Fixes', flags m
     - no-merge.md: type regex, pattern 'Merge branch', match not_contains

Then run the baseline from this folder and do not read the answers in between:
claude plugin eval release-notes --scaffold --trust-plugin --no-publish --max-cost-usd 5 --output-dir experiments/v0

Then read experiments/v0/aggregate-result.json and tell me, for each grader in the with-arm,
how many of the three runs passed it, and how many runs ended with an error.
```

**Expected result:** The case folder with `prompt.md`, `case.yaml`, `fixture.sh` and six graders, for example `graders/no-merge.md`:

```markdown
---
type: regex
pattern: 'Merge branch'
match: not_contains
---
```

The run prints one summary row:

```text
recent-changes  0.47  0.20  +0.27  6    $0.35   features-heading: pattern not found in last_message
```

| Grader | v0, with the plugin |
|---|---|
| `version-heading` | 0 of 3 |
| `features-heading` | 0 of 3 |
| `fixes-heading` | 1 of 3 |
| `no-merge` | 3 of 3 |
| `read-commits` | 3 of 3 |
| `skill-fired` (indicator) | 3 of 3 |
| runs with an error | 0 of 3 |

Three things about this suite are worth understanding before you copy it:

- **Three of the four metrics map onto graders.** Sections present is the three heading graders, merge commits excluded is `no-merge`, and the abort rate is the count of non-null `error` fields in `aggregate-result.json`. Identical output has no grader: plugin eval scores each run on its own and never compares runs to each other.
- **`--scaffold` is what runs `fixture.sh`.** Without it the run starts with no `commits.txt`, and `--trust-plugin` stands in for the trust prompt a run started from a session cannot answer. Pass both only for case files you wrote.
- **`skill-fired` is an indicator and carries no score.** In a run with and without the plugin, a `tool_used: Skill` grader can never pass without it, so plugin eval reports it and leaves it out of `WITH` and `W/OUT`. Read it first: a run where it failed measured the model alone and says nothing about your skill.

---

## Step 2: Propose a Skill Refinement

**Goal:** Use the autoresearch pattern of propose, evaluate, revert. Step 2 is the proposal. Do not apply it yet.

**Prompt:**

```text
Look at release-notes/skills/release-notes/SKILL.md and experiments/v0/aggregate-result.json.

Propose one focused refinement to the skill that should improve at least one metric without regressing the others. Examples of focused refinements:
  - Add a step explicitly excluding merge commits.
  - Add a step requiring # Version / ## Features / ## Fixes structure.
  - Add a worked example to the skill body showing the exact output format.
  - Add a rule to use conventional-commit prefixes (feat:, fix:) for categorisation.

Pick ONE, and say which grader would show it. Write the refinement as a proposed new SKILL.md
body in experiments/proposal-1.md. Do not modify the skill yet.

Explain in 2 to 3 sentences which metric you expect to improve and by how much.
```

**Expected result:** An `experiments/proposal-1.md` that targets the sections metric (1 of 9 heading checks at v0). Excluding merge commits is the tempting wrong pick: `no-merge` already passed in every v0 run, so that proposal could only stay flat.

---

## Step 3: Evaluate the Proposal

**Goal:** Apply the proposal, re-run the identical command, compare against the baseline.

**Prompt:**

```text
Apply the proposal:
  1. Back up the current skill: copy release-notes/skills/release-notes/SKILL.md to experiments/skill-v0.md
  2. Replace release-notes/skills/release-notes/SKILL.md with the proposal-1.md body.
  3. Re-run: claude plugin eval release-notes --scaffold --trust-plugin --no-publish --max-cost-usd 5 --output-dir experiments/v1

Then compare experiments/v0/aggregate-result.json to experiments/v1/aggregate-result.json in the
with-arm. For each grader, report:
  - Direction: improved, unchanged, regressed
  - Magnitude: the change in passing runs

Write the comparison to experiments/compare-v0-v1.md.
```

**Expected result:**

```text
recent-changes  1.00  0.20  +0.80  6    $0.34
```

The three heading graders went from 0, 0 and 1 of 3 to 3 of 3 each, and nothing else moved, as in [`compare-v0-v1.md`](02-evolution/release-notes-lab-solution/experiments/compare-v0-v1.md).

---

## Step 4: Revert or Promote, the Autoresearch Decision

**Goal:** Decide on the metrics alone. Promote the refinement only if the target metric improved AND no other metric regressed beyond a defined tolerance.

**Prompt:**

```text
Apply this decision rule to the with-arm:

  PROMOTE if:
    - The targeted graders passed in more runs
    - AND no other scored grader lost more than 1 run
    - AND no run ended with an error

  REVERT if:
    - The targeted graders did not improve
    - OR any other scored grader lost more than 1 run
    - OR any run ended with an error

Based on experiments/v1/aggregate-result.json, what is the decision? If REVERT, restore
release-notes/skills/release-notes/SKILL.md from experiments/skill-v0.md and write a note to
experiments/lessons.md explaining what was learned even from the revert. If PROMOTE, write a
note to experiments/lessons.md explaining the win.
```

**Expected result:** PROMOTE, and a lessons entry: a format the skill only implies is a suggestion, a format it names is a constraint the model follows on every run.

Watch the error count closely. A jump there rarely means the model failed: it usually means the case broke, for example a scaffold that never ran because `--scaffold` was missing.

---

## Step 5: Grade the Defect You Can See

**Goal:** Every scored grader is now at 3 of 3, so the next metric needs a grader before it can be a target. Read a real answer, write the grader, and baseline the unchanged skill with it.

**Prompt:**

```text
Run one more run so we can read an actual answer:
claude plugin eval release-notes --scaffold --trust-plugin --no-publish --max-cost-usd 1 --runs 1 --ablation none --keep-temp --output-dir experiments/peek

Read the final result from out/trace.jsonl in the kept temp folder it prints, and tell me
what in that answer is not release notes. Then delete the kept temp folder and experiments/peek.

Add release-notes/evals/recent-changes/graders/notes-only.md: type regex,
pattern '^-{3}\s*$', flags m, match not_contains. Re-run the unchanged skill with the identical
command into experiments/v1b, and report the with-arm passes per grader.
```

**Expected result:** The answer runs past the notes into a horizontal rule and a note about the skill:

```text
## Fixes

- Virtualenv and cache directories are now ignored by version control.

---

- **No version number:** `commits.txt` doesn't name a release version, so I left the heading as `# Version`. Tell me the version and I'll add it.
```

`notes-only` passes 0 of 3 in v1b and every other grader 3 of 3. The pattern spells three hyphens as `-{3}` on purpose: a literal `---` in a grader file's frontmatter fails the case with `invalid YAML frontmatter: YAML Parse error: Unexpected EOF`.

---

## Step 6: Run the Loop One More Time

**Goal:** Practise the full propose, evaluate, revert-or-promote cycle a second time so the rhythm lives in your hands as well as in the lab instructions.

**Prompt:**

```text
Repeat Steps 2 to 4 with experiments/proposal-2.md, targeting notes-only, backing up the skill
to experiments/skill-v1.md and writing experiments/v2. Compare against experiments/v1b, the
baseline that already had the grader.

At the end, write experiments/summary.md with:
  - Table rows comparing v0, v1, v1b and v2 with-arm passes per grader
  - The final state of release-notes/skills/release-notes/SKILL.md (promoted refinements only)
  - Three lessons learned about experiment design
  - One follow-up experiment you would run if you had another hour
```

**Expected result:**

```text
recent-changes  1.00  0.33  +0.67  6    $0.33
```

`notes-only` went from 0 of 3 to 3 of 3 with nothing else moving, so proposal 2 is promoted too. The [`summary.md`](02-evolution/release-notes-lab-solution/experiments/summary.md) records the trajectory, the surviving skill, and the lesson that a grader added mid-loop needs its own baseline on the unchanged skill.

---

## What You Just Practised

| Concept | Where it showed up |
|---|---|
| An eval case: prompt, scaffold fixture, one grader per check | Step 1 |
| Mapping metrics onto graders, and naming the one no grader expresses | Step 1 |
| The plugin-fired indicator and the with/without baseline | Step 1 |
| Autoresearch loop: propose, evaluate, promote or revert | Steps 2 to 4 |
| Decision rule based on grader passes alone | Step 4 |
| A new grader gets its own baseline before it becomes a target | Steps 5 and 6 |
