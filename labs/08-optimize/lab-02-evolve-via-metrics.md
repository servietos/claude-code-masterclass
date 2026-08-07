# Evolve a Skill with Deterministic Experiments

Take an existing skill, measure its quality with a deterministic experiment harness, then run an autoresearch loop (propose a refinement, evaluate it, revert if it regresses) to improve correctness and abort rate.

Each step contains:
- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

> **Prerequisite:** This lab assumes you have already practised the "manual x3, observe, codify" pattern from [Module 03: Creating & Managing Skills](../../demos/03-skills/readme.md). Here we focus on the *measurement* angle that this module frames in [`demos/08-optimize/03-autoresearch-loop`](../../demos/08-optimize/03-autoresearch-loop/readme.md): deterministic experiments, autoresearch loops, and metric-driven skill refinement.

**Tooling you need on `PATH` before Step 1:** `python` (3.10 or newer), `git`, `claude`, and `jq`. The harness parses Claude Code's JSON envelope, and `jq` ships with neither Windows nor macOS by default: install it with `winget install jqlang.jq`, `brew install jq`, or `apt install jq`. If you would rather not add a dependency, have the runner parse the envelope with `python -c` instead, since this lab already requires Python.

You work in [`02-evolution/release-notes-lab/`](02-evolution/release-notes-lab/readme.md), which ships the Python project and the under-specified skill you are going to measure. The completed reference is beside it in [`02-evolution/release-notes-lab-solution/`](02-evolution/release-notes-lab-solution/readme.md). Build your own harness first and use the solution to check its contract.

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/08-optimize/02-evolution/release-notes-lab
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `release-notes-lab` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/08-optimize/02-evolution/release-notes-lab commit the files that already ship there as five separate commits ....
```

That works for the git history, and for any step whose result is just files. It does not work for the skill you are measuring: `.claude/skills/release-notes/SKILL.md` loads from the directory the session was launched in, and the `claude -p` calls inside the Step 1 runner read it from the directory they run in, so a root session measures runs that never loaded the skill your Step 3 and Step 5 edits are changing. Launch inside `release-notes-lab` from Step 1 onward.

Launching inside the starter is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session, and you read them from the repo root without ever writing into them. Every path in the prompts below is relative to the lab folder.

---

## Setup: Open the Starter and Give It a Git History

The starter already holds the Typer CLI (`hello.py`, `math_utils.py`, `cli.py`, `requirements.txt`) and the skill you are going to measure at `.claude/skills/release-notes/SKILL.md`. That skill is deliberately under-specified: no version section, no grouping by type (feature vs. fix), no handling of conventional-commit prefixes, no exclusion of merge commits. It works, and it produces different output on every run, which is exactly what makes it worth measuring.

Prove the CLI before you measure anything that depends on it:

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install -r requirements.txt
./.venv/Scripts/python.exe cli.py hello Ada
./.venv/Scripts/python.exe cli.py sum-values 2 3
```

On Linux or macOS use `.venv/bin/python`. Expected output:

```text
Hello, Ada!
5.0
```

The harness in Step 1 shells out to `git log`, and the runner cds to the repo root of whatever session it runs in, so the lab project needs a repository of its own. The starter ships without a `.git` directory, because a nested repository inside the class repo shows up as an embedded repo. Initialise one inside `release-notes-lab`:

```bash
git init
```

The release notes are generated from that history, so an empty repo gives the skill nothing to summarise. Commit the shipped files in pieces rather than in one lump:

```text
This project is already scaffolded and a git repository has just been initialised with no commits yet.

Commit the files that are already here as five separate commits, in this order, each with a descriptive conventional-commit message:
  1. requirements.txt
  2. hello.py
  3. math_utils.py
  4. cli.py
  5. .gitignore, readme.md and .claude/skills/release-notes/SKILL.md

Do not change the contents of any file and do not add new files. Stage and commit only.
```

**Expected result:** `git log --oneline` lists five commits, the working tree is clean, and `.claude/skills/release-notes/SKILL.md` is untouched.

---

## Step 1: Define a Deterministic Test Harness

**Goal:** Build the measurement scaffolding before changing the skill. You cannot optimise what you cannot measure.

**Prompt:**

```text
Create a test harness for the release-notes skill at experiments/runner.sh that:

  1. cds to the repo root, and takes three environment variables with defaults: RUNS (default 3), METRICS (default metrics.json), and BASE_REV (default empty).
  2. Measures the current working tree by default, because the working tree is the thing we are experimenting on.
     Only when BASE_REV is set: refuse to run if `git diff` or `git diff --cached` reports changes, record the current branch, `git checkout --detach "$(git rev-parse --verify "$BASE_REV")"`, and always check the recorded ref back out at the end.
  3. Invokes the skill RUNS times with `claude -p "Run the release-notes skill" --output-format json`.
  4. Reads .result and .is_error out of each envelope with jq, saving the markdown to experiments/runs/<timestamp>-<N>.md.
  5. After the runs, computes:
     - run_count
     - measured_rev (the SHA the runs actually saw)
     - identical_outputs: how many PAIRS of runs produced byte-identical markdown. Over three runs the only possible values are 0 (all three differ), 1 (exactly two match) and 3 (all three match).
     - sections_present: how many runs produced a # Version / ## Features / ## Fixes structure
     - merge_commits_included: how many runs mentioned a merge commit
     - aborted_runs: how many runs returned a non-zero exit code, is_error true, or empty output
  6. Writes those counts to the path in METRICS.

Then run it once against the current skill with METRICS=experiments/metrics-v0.json and report the file.
```

**Expected result:** An `experiments/runner.sh`, an `experiments/runs/` directory holding the raw envelopes and the extracted markdown, and `experiments/metrics-v0.json` with the baseline. Expect `sections_present: 0` (the skill never asks for structure), `identical_outputs: 0` (three free-form summaries rarely match byte for byte), `merge_commits_included` variable, and `aborted_runs: 0`. These are the numbers you will try to improve.

Three things about this harness are worth understanding rather than copying:

- **`identical_outputs` counts pairs, not runs.** That is the definition [`demos/08-optimize/03-autoresearch-loop`](../../demos/08-optimize/03-autoresearch-loop/readme.md) uses, and it is why `0` is a legal baseline. A count of matching *runs* could never be lower than 1.
- **`BASE_REV` is opt-in on purpose.** Checking out an older commit deletes everything added later, including `.claude/skills/release-notes/SKILL.md` and `runner.sh` itself, so the runs would measure a repo with no skill in it. Worse, Steps 3 to 5 edit `SKILL.md` without committing, and `git checkout` refuses to run over uncommitted changes (`error: Your local changes to the following files would be overwritten by checkout`). Set `BASE_REV=HEAD~4` only when you deliberately want to measure history, with a clean tree.
- **The envelope keys are real.** `claude -p "..." --output-format json` returns a result message carrying `result`, `is_error`, `type`, `subtype`, `duration_ms`, `session_id`, `total_cost_usd`, `num_turns` and `usage`. The harness needs exactly the first two.

Validate the metrics file before you trust it:

```bash
jq -e . experiments/metrics-v0.json
```

---

## Step 2: Propose a Skill Refinement

**Goal:** Use the autoresearch pattern of propose, evaluate, revert. Step 2 is the proposal. Do not apply it yet.

**Prompt:**

```text
Look at .claude/skills/release-notes/SKILL.md and experiments/metrics-v0.json from Step 1.

Propose one focused refinement to the skill that should improve at least one metric without regressing the others. Examples of focused refinements:
  - Add a step explicitly excluding merge commits.
  - Add a step requiring # Version / ## Features / ## Fixes structure.
  - Add a worked example to the skill body showing the exact output format.
  - Add a rule to use conventional-commit prefixes (feat:, fix:) for categorisation.

Pick ONE. Write the refinement as a proposed new SKILL.md body in a separate file: experiments/proposal-1.md. Do not modify the live skill yet.

Explain in 2 to 3 sentences which metric you expect to improve and by how much.
```

**Expected result:** An `experiments/proposal-1.md` containing a revised SKILL.md body, plus a short rationale. The proposal targets one metric, likely `sections_present` (forcing structured output) or `identical_outputs` (adding a worked example to anchor consistency).

---

## Step 3: Evaluate the Proposal

**Goal:** Apply the proposal, re-run the harness, compare against the baseline.

**Prompt:**

```text
Apply the proposal:
  1. Back up the current skill: cp .claude/skills/release-notes/SKILL.md experiments/skill-v0.md
  2. Replace .claude/skills/release-notes/SKILL.md with the proposal-1.md body.
  3. Re-run the harness with METRICS=experiments/metrics-v1.json bash experiments/runner.sh

Then compare experiments/metrics-v0.json to experiments/metrics-v1.json. For each metric, report:
  - Direction: improved, unchanged, regressed
  - Magnitude: the delta

Write the comparison to experiments/compare-v0-v1.md.
```

**Expected result:** A `compare-v0-v1.md` with a per-metric verdict. The hoped-for outcome is that the targeted metric improved (for example `sections_present` went from 0 to 3) and no other metric regressed. Reality is often messier: adding a strict structure can *reduce* `identical_outputs`, because the model now has more surface area to vary on.

Note that the skill edit is uncommitted at this point. That is deliberate, and it is exactly why the harness measures the working tree by default.

---

## Step 4: Revert or Promote, the Autoresearch Decision

**Goal:** Decide based on metrics, not vibes. Promote the refinement only if the target metric improved AND no other metric regressed beyond a defined tolerance.

**Prompt:**

```text
Apply this decision rule:

  PROMOTE if:
    - The targeted metric improved (delta > 0 in the right direction)
    - AND no other metric regressed by more than 1 unit
    - AND aborted_runs stayed at 0

  REVERT if:
    - The targeted metric did not improve
    - OR any other metric regressed by more than 1 unit
    - OR aborted_runs increased

Based on experiments/metrics-v1.json, what is the decision? If REVERT, restore .claude/skills/release-notes/SKILL.md from experiments/skill-v0.md and write a note to experiments/lessons.md explaining what was learned even from the revert.

If PROMOTE, write a note to experiments/lessons.md explaining the win, then propose proposal-2.md targeting a different metric.
```

**Expected result:** Either a revert with a documented lesson (for example "adding a structure section reduced output consistency, try a worked example instead") or a promotion with a follow-up proposal. Either outcome teaches you something about your harness, which is the autoresearch loop's whole purpose.

Watch `aborted_runs` closely. A jump there rarely means the model failed: it usually means the harness broke, for example a malformed envelope, a missing `jq`, or a checkout that removed the skill mid-run.

---

## Step 5: Run the Loop One More Time

**Goal:** Practise the full propose, evaluate, revert-or-promote cycle a second time so the rhythm is in your hands, not just in the lab instructions.

**Prompt:**

```text
Repeat Steps 2 to 4 with proposal-2.md, writing experiments/metrics-v2.json. Target a different metric than proposal-1 targeted.

At the end, write experiments/summary.md with:
  - Table rows comparing v0, v1 and v2 metrics
  - The final state of .claude/skills/release-notes/SKILL.md (promoted refinements only)
  - Three lessons learned about deterministic experiment design
  - One follow-up experiment you would run if you had another hour
```

**Expected result:** A `summary.md` with the metric trajectory across two loop iterations, the surviving skill, and a written reflection. The lessons typically cover: start with the simplest metric you can compute, target one metric per iteration, and revert without sentiment when metrics regress.

---

## What You Just Practised

| Concept | Where it showed up |
|---|---|
| Deterministic experiment harness over `claude -p --output-format json` | Step 1 |
| Metric definition (`identical_outputs` as a pair count, `sections_present`, `aborted_runs`) | Step 1 |
| Measuring the working tree, and why a base-commit checkout has to be opt-in and guarded | Step 1 |
| Autoresearch loop: propose, evaluate, promote or revert | Steps 2 to 4 |
| Decision rule based on metric deltas, not vibes | Step 4 |
| Iterating the loop for compounding improvement | Step 5 |

This is the discipline behind treating skills as *living artefacts*: every change is a measured experiment, not a wishful edit. [Lab 03](lab-03-memory-architectures.md) turns the same measuring instinct on memory itself, comparing in-context loading, an episodic statefile, and an MCP knowledge graph on one recall task.
