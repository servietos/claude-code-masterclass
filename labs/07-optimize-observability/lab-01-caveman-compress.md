# Compress a Bloated Harness with Caveman Mode

Compress a bloated `CLAUDE.md` by instructing Claude to rewrite it "as a caveman" (terse, no articles, no copulas, no hedging) while keeping every rule's meaning intact. Then verify the compressed version still binds the model the same way the original did, and codify the rewrite prompt as a reusable skill.

Each step contains:
- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

> **Why this matters:** Every token in `CLAUDE.md` is read on every turn. A 3,300-token harness file costs you 3,300 tokens on every turn of every session. Halving that without behaviour loss is one of the highest-leverage harness optimisations you can make.

The completed reference for this lab is [`01-compression/caveman-lab-solution/`](01-compression/caveman-lab-solution/readme.md). Build your own version first and use the solution to check your numbers.

This lab's project is [`01-compression/caveman-lab/`](01-compression/caveman-lab/readme.md), already in this repo. It ships the API, its tests and the bloated `CLAUDE.md` you are going to compress.

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/07-optimize-observability/01-compression/caveman-lab
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `caveman-lab` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/07-optimize-observability/01-compression/caveman-lab write tokens.py, a tiktoken counter that takes a file path as argv[1] ....
```

That works for the token counter, and for any step whose result is just files. It does not work for the harness itself: the bloated `CLAUDE.md` the starter ships and the `caveman` skill you write under `.claude/skills/` in Step 5 load from the directory the session was launched in, so a root session reads this repo's harness and never sees the lab's. Launch inside `caveman-lab` from Step 1 onward.

Launching inside the starter makes it the project and the repository a monorepo around it: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session, and you read them from the repo root without ever writing into them. Every path in the prompts below is relative to the lab folder.

---

## Setup: Prove the Starter Runs

The starter ships the Fastify API under `api/`, its Vitest suite, and the deliberately bloated `CLAUDE.md` at the project root. Install and prove it before you touch the harness:

```bash
npm install
npx tsc --noEmit
npm test
```

Expect `audited 101 packages, found 0 vulnerabilities`, a silent exit 0 from `tsc --noEmit`, and `Test Files 1 passed (1)` / `Tests 5 passed (5)`. A green baseline matters: Step 4 looks for regressions, and you cannot see a regression against a red starting point.

Confirm the harness is as bloated as advertised. It measures 3,048 words:

```bash
wc -w CLAUDE.md
```

```powershell
(Get-Content CLAUDE.md | Measure-Object -Word).Words
```

---

## Step 1: Baseline Token Count

**Goal:** Measure the cost of the original `CLAUDE.md` before compression so the improvement is concrete.

`tiktoken` is a third-party PyPI package, so install it into a virtual environment first. Never install it globally.

```bash
python -m venv .venv
./.venv/Scripts/python.exe -m pip install tiktoken
```

On Linux or macOS the interpreter is `.venv/bin/python`.

**Prompt:**

```text
Write a small Python script tokens.py that uses tiktoken (cl100k_base) to count tokens in any file passed as argv[1]. Then run it against CLAUDE.md with the .venv interpreter and print the result.

Also run it against api/index.ts so we have a non-prose baseline.

Save the results to baseline.txt with this format:
  CLAUDE.md: <tokens>
  api/index.ts: <tokens>
```

**Expected result:** A `tokens.py` script and a `baseline.txt` file. The starter ships the harness, so your numbers match exactly: `CLAUDE.md` is **3,313 tokens** for 3,048 words, and `api/index.ts` is **302 tokens**. The useful rule to carry away is that English prose runs about 1.05 to 1.10 tokens per word under `cl100k_base`, so a 3,000-word harness costs a bit over 3,000 tokens on every turn. Record your `CLAUDE.md` number, you will divide by it later.

> The demo [`demos/07-optimize-observability/02-caveman-compression`](../../demos/07-optimize-observability/02-caveman-compression/demo-caveman-compression.md) measures the same thing with `js-tiktoken` in Node. Same encoding, same counts.

---

## Step 2: Apply the Caveman-Mode Rewrite

**Goal:** Compress `CLAUDE.md` by instructing Claude to rewrite it in caveman speech. The compression comes from the prompt alone: terse broken grammar drops articles, copulas, and filler while keeping every rule.

**Prompt:**

```text
Rewrite CLAUDE.md as a caveman would say it.

Rules:
  - Short sentences. No articles (a, an, the). No copulas (is, are, was, were) where droppable. No hedging (please, kindly, generally, usually).
  - Imperatives only. "Do X" not "You should do X" or "It would be good to do X".
  - Preserve every rule. Same rules, same enforceability, fewer words.
  - Keep the section structure. Don't merge sections.
  - Preserve code fences and file paths exactly.

Save the result to CLAUDE.caveman.md. Do not overwrite CLAUDE.md yet.
```

**Expected result:** A `CLAUDE.caveman.md` file in the project root. Skim it: it reads brusque but every rule from the original should still be present. If a rule got lost, ask Claude to add it back in caveman form.

---

## Step 3: Measure the Compression

**Goal:** Confirm the token drop is real, and understand which half of it grammar buys you and which half costs you rationale.

**Prompt:**

```text
Run tokens.py against CLAUDE.caveman.md. Then compute:
  original_tokens = (CLAUDE.md token count from baseline.txt)
  caveman_tokens = (CLAUDE.caveman.md token count)
  reduction_percent = 100 * (1 - caveman_tokens / original_tokens)

Append the results to baseline.txt with this format:
  CLAUDE.caveman.md: <tokens>
  Reduction: <percent>%
```

**Expected result:** `baseline.txt` updated with the caveman line and the reduction percentage. Expect roughly **50 to 75 percent**, and where you land inside that band is a decision you make. Measured on the solution harness:

| File | Tokens (`cl100k_base`) | Reduction |
|---|---|---|
| `CLAUDE.md` | 3,313 | baseline |
| `CLAUDE.caveman.md` (every rule *and* its rationale kept) | 1,538 | 53.6% |
| `CLAUDE.caveman-strict.md` (every rule kept, rationale prose deleted) | 734 | 77.8% |

Grammar alone buys you about half. The rest only comes from deleting the prose that explains *why* a rule exists. That is a deliberate trade to make before the parity test in Step 4: rationale is what keeps a rule applying correctly to cases you did not enumerate. If you land above 78 percent, check for dropped rules before you congratulate yourself.

**Prompt (optional second pass):**

```text
Produce CLAUDE.caveman-strict.md: same rules as CLAUDE.caveman.md, but delete every sentence that only explains why a rule exists. Keep the rules themselves verbatim in caveman form. Run tokens.py on it and append the count and reduction to baseline.txt.
```

Now you have two candidates and a real choice to test.

---

## Step 4: Behaviour Parity Test

**Goal:** Confirm the compressed `CLAUDE.md` actually binds the model the same way the original does. A token saving that loses behaviour is a regression.

This step needs two live Claude Code sessions with a restart between them, so it cannot be scripted. Pick tasks that probe rules in the harness: a rule about no inline comments, a rule about error-handling style, and a rule about file organisation.

**Prompt:**

```text
I'm going to run a behaviour parity test on this harness.

Step A: Read CLAUDE.md (the original). Then perform these three tasks and save the outputs to parity/original/:
  1. Add a DELETE /users/:id endpoint to api/index.ts with input validation.
  2. Write a Vitest test file for the existing POST /users endpoint.
  3. Add a new file api/health.ts exporting a health check function.

Step B: Rename CLAUDE.md to CLAUDE.original.md, rename your chosen caveman file to CLAUDE.md, then restart this session. (I will do this part by hand and re-run you.)
```

After the rename, restart Claude Code (`/exit`, then `claude`) and run:

```text
Now do the same three tasks again (DELETE endpoint, POST test, health.ts) and save the outputs to parity/caveman/.

Then diff parity/original/ against parity/caveman/ and report:
  - Did any of the harness rules from CLAUDE.original.md fail to apply in the caveman run?
  - Are the outputs functionally equivalent (same endpoints, same test coverage, same file layout)?
  - List any rule-level regressions with the exact rule from CLAUDE.original.md that was violated.
```

**Expected result:** A diff between the two output sets with a verdict. The desired outcome is "no rule-level regressions, outputs are functionally equivalent". Run `npx tsc --noEmit` and `npm test` after each pass too: a rule violation that breaks the build shows up there before you read a single diff. If regressions appear, they tell you exactly which rules the caveman rewrite weakened, and whether the strict variant cut a rationale that was load-bearing after all. Go back to Step 2 and tighten the wording on those rules.

---

## Step 5: Codify Caveman Mode as a Reusable Skill

**Goal:** Promote the compression prompt to a skill so any future project can compress its `CLAUDE.md` with one slash command.

**Prompt:**

```text
Create a Claude Code skill at .claude/skills/caveman/SKILL.md in this lab project with this content shape:

---
name: caveman
description: Rewrite the active file in caveman speech to compress token cost by roughly 50 to 75 percent while preserving every rule. Use when CLAUDE.md or a skill body has grown verbose and the token cost is becoming noticeable in every turn.
---

# Caveman Compression

## When to use

When CLAUDE.md, a skill body, or any prose harness file has grown verbose and you want to reduce its token cost without losing rules.

## Steps

1. Read the target file in full.
2. Rewrite it in caveman speech:
   - Drop articles (a, an, the).
   - Drop copulas (is, are, was, were) wherever droppable.
   - Drop hedging (please, kindly, generally, usually, it would be good to, you should).
   - Imperatives only.
   - Preserve every rule with the same enforceability.
   - Preserve section headings and code fences exactly.
3. Save the result alongside the original as <filename>.caveman.<ext>.
4. Run a token counter on both and report the reduction percentage.
5. State whether rationale prose was kept or dropped, because that is the difference between roughly 50 and roughly 78 percent.
6. Recommend a behaviour parity test before replacing the original.

## Anti-patterns

- Do not merge sections to save tokens.
- Do not drop rules even if they seem redundant in the original.
- Do not "improve" rules: preserve the effect of their wording; the phrasing may change.

Then test the skill by invoking it on CLAUDE.original.md from Step 4 and confirming it produces the same compressed output you got by hand.
```

**Expected result:** A `labs/07-optimize-observability/01-compression/caveman-lab/.claude/skills/caveman/SKILL.md` whose folder name matches its frontmatter `name` and whose `description` carries the trigger phrases. Skills are discovered when the session starts, so `/exit` and `claude` again before you try to invoke it. Invoking it needs a live session; the file, its location and its frontmatter can be checked without one. Running the skill on `CLAUDE.original.md` produces a `CLAUDE.original.caveman.md` with a reduction in the same band you measured by hand, and the compression is now repeatable across any project.

---

## What You Just Practised

| Technique | Where it showed up |
|---|---|
| Token-cost baseline measurement with `tiktoken` | Step 1 |
| Caveman compression as a prompt technique | Step 2 |
| Token reduction metric (roughly 50 to 75 percent, depending on rationale kept) | Step 3 |
| Behaviour parity and regression testing for a harness change | Step 4 |
| Codifying a recurring prompt as a reusable skill | Step 5 |

[Lab 02](lab-02-evolve-via-metrics.md) builds on the skill-codification mechanic by *measuring* an existing skill's quality with deterministic experiments and tightening it via an autoresearch loop.
