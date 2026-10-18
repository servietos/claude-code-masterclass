# Harvest the Current State of a Bike Rental Shop

Map what a running shop already does before anyone plans a change to it. Parallel subagents read the code, the database schema and the owner's process notes and spreadsheet, each appending cited bullets once to a shared `ledger.md`. You then turn the ledger into `current-state.md` with a gap list and check its claims against the sources.

Each step contains:
- **Goal**: what you are building
- **Prompt**: paste this into Claude Code (or a shell command, where noted)
- **Expected result**: what the outcome looks like

Work in [03-harvest/bike-rental-shop/](03-harvest/bike-rental-shop). The starter holds only the shop's existing sources; `ledger.md` and `current-state.md` are what you produce.

---

## The Problem

A bike rental shop runs on a small Python app, an Excel workbook and the owner's habits. The owner asks for four things: reminders before a bike is due, deposits tracked and refunded, bikes flagged when service is overdue, and a weekly late-fee report. Planning those from a chat with the owner produces a plan that rebuilds what the workbook already does and misses what the app never stored.

By the end you hold a `current-state.md` that says, for each request, whether it already exists, partly exists or is missing, with a source behind every line. You also hold the evidence that a harvest summary is a claim until someone opens the file it cites.

---

## Where to Open Claude Code

This lab builds its own files, so open Claude Code inside the lab project. A session opened at the repo root writes `ledger.md` there, and the subagents then read paths that do not exist. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/11-planning/03-harvest/bike-rental-shop
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and ignores the `cd` above. Open `bike-rental-shop` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

Every path in the prompts below is relative to the lab folder.

---

## Setup: Look at the Starter

The starter is a brownfield project in three parts, and none of them was written for this lab's questions:

| Folder | Holds |
|---|---|
| `shop-app/` | The Python rental app: `app.py`, `rentals.py`, `fees.py`, `db.py`, `schema.sql` and one test file |
| `shop-sources/process-notes.md` | The owner's record of one week at the counter |
| `shop-sources/rentals-tracker.xlsx` | The workbook with a `Rentals` sheet and a `Service` sheet |

The workbook step needs openpyxl. Install it into a virtual environment.

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

If your PowerShell execution policy blocks the activation script, skip activation and call `.venv\Scripts\python.exe` directly.

The harvest reads files and never needs the app to run. The one command worth running first shows the sources are all there:

```bash
python -c "import pathlib; print(sorted(str(p) for p in pathlib.Path('.').rglob('*') if p.is_file() and '.venv' not in p.parts))"
```

**Expected result:** a list of ten entries: `.gitignore`, `requirements.txt`, the six files under `shop-app/` (`app.py`, `db.py`, `fees.py`, `rentals.py`, `schema.sql` and `tests/test_rent.py`) and the two files under `shop-sources/`. There is no `ledger.md`, no `current-state.md` and no `shop.db`.

---

## Step 1: Fix the Ledger Contract

**Goal**: Four subagents cannot talk to each other, so they share one file. Four writers editing one file overwrite each other, so the rules for writing to it come first.

**Prompt:**

```text
Create ledger.md in this folder with a title line and a "## How to write here" section
that states these rules:
  1. Each harvester adds ONE section, with a "## <source>" heading, in a single append at the end of its run.
  2. A section is bullets only. Every bullet states one observed fact and ends with a citation in parentheses:
     the file path, plus the sheet and cell, or the symbol or line, it came from.
  3. Facts only: no recommendations, no judgement of what is missing.
  4. A harvester writes no other file.
Write nothing else into the file yet.
```

**Expected result:** `ledger.md` exists with a title and the four rules and no source sections. The rules are the contract every subagent in Step 2 is held to, and a bullet without a citation in parentheses will fail the check in Step 3.

---

## Step 2: Harvest in Parallel

**Goal**: Three independent sources get three subagents at the same moment. Each subagent reads in its own context window and returns only a summary, so the hundreds of lines it read never reach your conversation.

**Prompt:**

```text
Harvest the current state of this bike rental shop into ledger.md, following the rules at its top.
Spawn three general-purpose subagents in parallel, one per source:
  1. Code: every file under shop-app/ except schema.sql. Cover what each command does, where each
     capability lives, which constants and formulas the code uses, and which behaviour has a test.
  2. Data schema: shop-app/schema.sql, plus how the code reads and writes each table and column.
     Name every column that no code writes to.
  3. Process and spreadsheet: shop-sources/process-notes.md, and shop-sources/rentals-tracker.xlsx
     read with a short openpyxl script using load_workbook(..., data_only=False) so formulas come back,
     not cached values.
Each subagent appends its section in ONE shell append and writes no other file.
Wait for all three, then report the bullet count per heading.
```

**Expected result:** Claude starts three subagents side by side. Type `/tasks` while they run to see all three. When they finish, `ledger.md` holds the rules block and three new sections with a count per heading from Claude. Counts differ from run to run; a section with fewer than about eight bullets usually means the subagent skimmed.

---

## Step 3: Check the Shape of the Ledger

**Goal**: Before anything is built on the ledger, prove it follows its own contract. A section with uncited bullets or a missing heading is a harvest that failed quietly.

**Command:**

```bash
python -c "import re; t=open('ledger.md',encoding='utf-8').read(); print('headings', len(re.findall(r'^## ', t, re.M))); b=[l for l in t.splitlines() if l.startswith('- ')]; print('bullets', len(b)); print('uncited', len([l for l in b if not re.search(r'\)\.?$', l.rstrip())]))"
```

**Expected result:** three lines. `headings` is 4 (the "How to write here" section plus the three sources), `bullets` matches the total Claude reported in Step 2 (the contract's own rules are numbered, so they do not count), and `uncited` is `0`. If `uncited` is above zero, paste this into Claude Code:

```text
In ledger.md, list every bullet that does not end with a citation in parentheses. For each, open the source,
add the real citation, and leave every other line untouched.
```

Run the check again until `uncited` is `0`.

---

## Step 4: Turn the Ledger into the Current-State Document

**Goal**: The ledger is raw harvest. The current-state document keeps what was observed apart from what was concluded, and judges the owner's request against it.

**Prompt:**

```text
Read ledger.md and write current-state.md with four sections: Inventory, How it is used, Limits, Gap list.
Keep what was observed apart from what you conclude: every Inventory and How it is used line cites the
source path from the ledger; Limits and Gap list may conclude, but each line names the observation it rests on.
The Gap list judges this request from the shop owner against the current state, one row per capability,
each marked exists, partly exists or missing, with a Sources column naming the files behind the mark:
  1. Remind a customer the day before a bike is due.
  2. Record the deposit when a bike goes out and refund it when the bike comes back.
  3. Flag bikes whose service is overdue.
  4. Report the late fees collected in a week.
  5. Let customers book a bike online.
Where the app and the workbook disagree, say so in Limits and keep both values.
```

**Expected result:** `current-state.md` with four sections and a five-row gap list. Read the Limits section for two findings the owner never mentioned: the app and the workbook charge different late fees (the app computes 4.00 per day with a 40.00 cap in `fees.py`, the workbook 5 per day with a 50 cap in its `Late Fee` column), and several schema columns (`deposit_cents`, `customers.email`, `bikes.last_service_date`) are never written by any code. Row 5 should read `missing`; rows 1 to 4 typically read `partly exists`, and the Sources column should tell you which of the app or the workbook covers the part that exists.

---

## Step 5: Spot-Check Three Ledger Claims by Hand

**Goal**: The document inherits the ledger's mistakes, and the ledger inherits each subagent's. Opening the source yourself for three claims shows you what a verified claim looks like before you ask Claude to verify the rest.

**Commands:** pick the three claims below in `ledger.md` or `current-state.md` and run one command each. Find the matching bullet in your file; the wording differs from run to run.

Claim A, the app's late fee constants:

```bash
python -c "print(open('shop-app/fees.py').read())"
```

Claim B, the workbook's late fee formula:

```bash
python -c "from openpyxl import load_workbook; ws = load_workbook('shop-sources/rentals-tracker.xlsx')['Rentals']; print(ws['H2'].value)"
```

Claim C, that no code writes `deposit_cents`:

```bash
python -c "import pathlib; print([str(p) for p in pathlib.Path('shop-app').rglob('*.py') if 'deposit' in p.read_text()])"
```

**Expected result:** Command A prints the whole of `fees.py`, which contains the lines `LATE_FEE_PER_DAY_CENTS = 400` and `LATE_FEE_CAP_CENTS = 4000`. Command B prints `=IF(G2="","",MIN(G2*5,50))`. Command C prints `[]`, an empty list, so no Python file mentions a deposit. 

Each result must agree with the bullet Claude wrote. If one bullet states a different number or names a file that does not contain the thing, you found a harvest error: note the line, since the next step fixes it.

---

## Step 6: Check the Whole Document Against the Sources

**Goal**: Hand the check to a fresh subagent that reads sources only. A checker that reads `ledger.md` repeats the ledger's mistakes.

**Prompt:**

```text
Spawn one general-purpose subagent to check current-state.md against the sources it cites, with ledger.md left unread.
For every Limits line and every Gap list row, it opens the file that line cites and reports held or violated,
with the line, cell or symbol it checked. Correct any line in current-state.md that does not hold and list
what changed. No other file is touched.
```

**Expected result:** a report with one held-or-violated verdict per Limits line and Gap list row, each carrying a line, cell or symbol. Most come back held; a violated verdict names the correction it made in `current-state.md`, such as a citation to the wrong file or a gap row marked `exists` when only the workbook covers it. The report ends with the list of changes, and `ledger.md` is unchanged. Confirm that with a final check:

```bash
python -c "import pathlib; print(sorted(p.name for p in pathlib.Path('.').iterdir() if p.is_file()))"
```

It lists `.gitignore`, `current-state.md`, `ledger.md` and `requirements.txt`: the two documents are the only files the lab added.

---

## What You Just Practised

| Technique | Where it showed up |
|---|---|
| A shared ledger with a writing contract | Step 1 |
| One parallel subagent per independent source | Step 2 |
| Mechanical check of a harvest's shape | Step 3 |
| Observed facts kept apart from conclusions, plus a gap list | Step 4 |
| Verifying a claim by opening its source | Step 5 |
| An independent checker that reads sources only | Step 6 |

The gap list is the input for planning: rows marked `partly exists` need wiring, rows marked `missing` are the candidates for a spec. Continue with [Drive a Feature Spec-First with Plan Mode](lab-01-spec-driven-from-scratch.md) to take a gap row into a plan.
