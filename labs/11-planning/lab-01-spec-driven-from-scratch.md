# Drive a Feature Spec-First with Plan Mode

Build a feature for a small notes CLI by going through Plan Mode end-to-end. You will use Plan Mode for clarification and constraint iteration, Extended Thinking for one hard design decision, a `STATE.md` statefile as the persistent handoff document, and work packages with contracts for the actual work, then validate against explicit done criteria.

Each step contains:
- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

Work in [01-plan-mode/notes-cli/](01-plan-mode/notes-cli); the finished reference implementation sits beside it in [01-plan-mode/notes-cli-solution/](01-plan-mode/notes-cli-solution). Build your own first, then compare.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The starter is already in this repo, so there is nothing to scaffold: change into it and start the session there. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/11-planning/01-plan-mode/notes-cli
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `notes-cli` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/11-planning/01-plan-mode/notes-cli create STATE.md capturing the tag and pin decisions ....
```

That works for any step whose result is just files. It stops working at Step 6, where Claude runs the contract commands itself: `notes.db` is resolved against the directory the session was launched in, so a root session writes a second, empty database at the repo root and every check comes back empty with exit code 0. Launch inside the starter from Step 1 onward.

Launching inside the starter makes the lab folder the project and the repository a monorepo around it: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session and you read them from the repo root, without ever writing into them, and every path in the prompts below is relative to the lab folder.

---

## Setup: Run the Starter

The starter ships in this repo at [01-plan-mode/notes-cli/](01-plan-mode/notes-cli): `notes.py` with `add` and `list`, `db.py` with `get_connection()` and an `init_db()` that creates the `notes` table (id, body, created_at), and `requirements.txt` with Typer pinned. Nothing to generate; open Claude Code in that folder as the launch block above shows, then create the environment and install.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Git Bash:

```bash
python -m venv .venv
source .venv/Scripts/activate
pip install -r requirements.txt
```

On Windows the interpreter lives in `.venv\Scripts\`; Unix guides assume `.venv/bin/`. If your PowerShell execution policy blocks the activation script, skip activation and call the interpreter directly: `.venv\Scripts\python.exe notes.py list`. Keep the environment active: every later `python notes.py ...` step in this lab assumes it.

Seed two notes and confirm the CLI runs:

```bash
python notes.py add "Write the quarterly report"
python notes.py add "Buy milk"
python notes.py list
```

**Expected result:** `notes.db` appears beside `notes.py`, and `list` prints id, created_at and body, one note per line, newest id first:

```text
2  2026-08-03 13:34:47  Buy milk
1  2026-08-03 13:34:47  Write the quarterly report
```

`notes.db` is created relative to the working directory, so run every command from inside `notes-cli/`. A shell opened elsewhere silently creates a second, empty database and `list` prints nothing with exit code 0.

---

## Step 1: Enter Plan Mode

**Goal:** Activate Plan Mode and pose a deliberately under-specified feature request. Observe Claude respond with clarifying questions and no code.

**Prompt:**

Press `Shift+Tab` until the status bar reads `plan mode on`. Then submit:

```text
I want to add tags and pinning to notes-cli.
```

**Expected result:** Claude does not write any code. It produces a question list, likely covering tag storage (relational vs. denormalised), tag query semantics (AND vs. OR), pinning scope (per-tag vs. global), display behaviour, and migration of existing rows. The reply ends with a draft plan that is explicitly marked as provisional pending your answers.

---

## Step 2: Iterate the Plan With Constraints

**Goal:** Push back on Claude's first plan by ratcheting hard constraints. The point is to feel the difference between a vague brief and a constrained one, and to put the constraints *before* the ask in your follow-up.

**Prompt:**

Stay in Plan Mode. Submit:

```text
Constraints, these are non-negotiable:
  1. Tags are normalised in their own table with a junction table. No JSON columns.
  2. Multi-tag search must support AND across tags (note must have all of them).
  3. Pinned notes sort to the top of `list` output, then by id descending.
  4. Existing rows in notes.db must keep working, no destructive migration.
  5. No external dependencies beyond Typer.

Given those, revise the plan. Then tell me what is still ambiguous.
```

**Expected result:** Claude rewrites the plan against the constraints. The schema section now shows `tags`, `note_tags`, and a `pinned` column on `notes`. Claude flags remaining ambiguity, for example the CLI surface for tagging on add vs. retag, or whether `list` accepts a `--tag` filter. You answer those follow-ups in one more turn before continuing.

---

## Step 3: Extended Thinking on a Hard Decision

**Goal:** Use Extended Thinking for the one decision in the plan that is genuinely architectural (junction-table indexing strategy under multi-tag AND queries) and observe the difference between a quick answer and a deeper reasoning chain.

**Prompt:**

Still in Plan Mode. Submit:

```text
ultrathink about this:

For the multi-tag AND query, compare three approaches:
  A. SELECT with INTERSECT across one subquery per tag.
  B. GROUP BY note_id HAVING COUNT(DISTINCT tag_id) = N with an IN clause.
  C. A self-join chain.

For each: write the SQL, give the expected query plan on a notes table with ~10k rows and ~30k note_tags rows, and recommend the one to use. Explain why the others lose.
```

`ultrathink` is the keyword Claude Code recognises for one-off deeper reasoning on a single turn; phrases like `think hard` or `think more` are passed through as ordinary prompt text and trigger nothing. To raise reasoning depth for the whole session instead, use `/effort high` or `/effort xhigh` (also available as the `--effort` flag or the `CLAUDE_CODE_EFFORT_LEVEL` environment variable).

**Expected result:** A visibly longer reasoning chain than your previous turns. Claude produces three SQL variants, predicts the query plan for each (including which indexes get hit), and gives a recommendation with stated reasoning.

Claude will usually recommend Option B, because a single statement scales to any tag count. Measured on exactly the dataset this step specifies (10,000 notes, 30,000 note_tags rows, 50 tags, SQLite 3.49.1, best of 50 runs, identical 48-row result sets), Option B is in fact the slowest and the self-join chain the fastest: A 0.202 ms, B 0.507 ms, C 0.139 ms. `EXPLAIN QUERY PLAN` shows why: B pays for three temporary b-trees (`USE TEMP B-TREE FOR GROUP BY`, `FOR count(DISTINCT)`, `FOR ORDER BY`), while C resolves through covering index lookups on `sqlite_autoindex_tags_1 (name=?)` and `idx_note_tags_tag (tag_id=? AND note_id=?)`.

Either answer is acceptable here: all three are sub-millisecond at CLI scale and the lab's purpose is the *form* of the reasoning. Run `EXPLAIN QUERY PLAN` on your own data to check Claude's prediction against reality.

---

## Step 4: Author STATE.md as Your Statefile

**Goal:** Convert the agreed plan into a persistent `STATE.md`, a rolling document that any future Claude session reads first to know where the work stands. This is different from a spec: it captures decisions, current status, and the next concrete action, and it mutates every session.

**Prompt:**

Still in Plan Mode. Submit:

```text
Create STATE.md in the project root with these sections, in this order:

# Notes CLI: Project State

## Goal
[one sentence]

## Decisions
[bullet list of every decision we just locked in: schema, query strategy, pinning semantics, CLI surface]

## Status
- [x] Starter scaffolded
- [ ] Schema migration written
- [ ] Tag/pin commands implemented
- [ ] List filter implemented
- [ ] Done criteria validated

## Next Action
[the single next thing to do]

## Done Criteria
[verifiable bullet list: what must be true for this feature to be considered complete, expressed as commands you can run and outputs you can read]

## Open Questions
[anything still ambiguous, empty if none]

Use the conversation we just had as the source of truth. Do not invent new decisions.
```

**Expected result:** A `STATE.md` file in the project root. The Decisions section reflects what was agreed in Steps 1 to 3 (junction tables, AND semantics, pinned-first sort, non-destructive migration, Typer-only). The Done Criteria section lists at least four runnable checks. These three all run clean against a finished implementation:

```bash
python notes.py tag add 1 work
python notes.py list --tag work --tag urgent
python notes.py pin 1 && python notes.py list
```

The first prints `tagged note 1 with work` and exits 0, the second returns only notes carrying both tags, and the third puts note 1 at the top of the listing with the rest still in id-descending order.

---

## Step 5: Decompose Into Work Packages

**Goal:** Break the plan into three independent units of work with explicit input/output contracts. Each unit must be small enough for one Claude session to complete without further clarification.

**Prompt:**

Still in Plan Mode. Submit:

```text
Decompose the work in STATE.md into three work packages. For each:
  - name (short, lowercase, hyphenated)
  - input: the files it may read and the section of STATE.md that governs it
  - output: the files it creates or modifies and the contract it must satisfy (a callable command + expected output)
  - depends on: which other package must finish first, if any

The three packages should be:
  1. schema-migration: adds the new tables and the pinned column without dropping data
  2. tag-commands: implements `tag add <id> <name>`, `tag remove <id> <name>`, `pin <id>`, `unpin <id>`
  3. list-filter: extends `list` with `--tag <name>` (repeatable, AND semantics) and pinned-first ordering

Return a markdown table. Do not implement anything yet.
```

**Expected result:** A three-row markdown table. `schema-migration` has no dependencies, `tag-commands` depends on it, `list-filter` depends on both. Each row's output column names a concrete verifiable command. For `schema-migration`, this one is a good contract because it parses unchanged in PowerShell, cmd and Git Bash:

```bash
python -c "import sqlite3; print(sqlite3.connect('notes.db').execute('select name from sqlite_master where type=?', ('table',)).fetchall())"
```

It must print `[('notes',), ('tags',), ('note_tags',)]`. Avoid the tempting `where type=\"table\"` variant: the nested double quotes are mangled by PowerShell before Python ever sees them, and it leans on SQLite treating a double-quoted token as a string literal.

---

## Step 6: Execute and Self-Critique Against Done Criteria

**Goal:** Exit Plan Mode, execute the three packages in dependency order, then have Claude critique its own output against the Done Criteria section of `STATE.md` before you declare the feature complete.

**Prompt:**

Approve the plan when Claude presents it (choose the option that switches you to manually approving edits), or press `Shift+Tab` to cycle past manual mode until the status bar reads `accept edits on`. Then submit:

```text
Execute the three packages from STATE.md in dependency order. After each package finishes:
  1. Update STATE.md: flip the matching Status checkbox to [x] and update Next Action.
  2. Run the package's contract command and paste the output below.

When all three are done, do a self-critique:
  - Walk through every bullet in the Done Criteria section.
  - For each, run the check and report PASS or FAIL with the actual command output.
  - If anything fails, fix it, re-run, and update STATE.md.

Do not declare the feature complete until every Done Criteria bullet is PASS.
```

**Expected result:** Claude runs each package, updates `STATE.md` after each, and ends with a self-critique block listing every Done Criteria bullet with its command, output, and PASS/FAIL status. All bullets are PASS. The `STATE.md` Status section is fully checked and Open Questions is empty. Verify by hand:

```bash
python notes.py list --tag work
python notes.py pin 1
python notes.py tag add 99 work
```

The first two exit 0 and behave as the criteria describe. The third targets a note that does not exist, prints `no note with id 99` and exits 1, which is the error path worth checking before you call the feature done.

---

## What You Just Practised

| Technique | Where it showed up |
|---|---|
| Plan Mode entry and constraint iteration | Steps 1 and 2 |
| Constraint-first prompting | Step 2 (constraints before the ask) |
| Extended Thinking on one turn | Step 3 (`ultrathink`) |
| Statefile as persistent handoff | Step 4 (`STATE.md`) |
| Work packages with contracts | Step 5 |
| Self-critique loop against done criteria | Step 6 |

[Lab 02](lab-02-spec-kit-and-bmad.md) covers the same workflow using `github/spec-kit` and the BMAD-METHOD templates so you can see how packaged tooling formalises what you just did by hand.
