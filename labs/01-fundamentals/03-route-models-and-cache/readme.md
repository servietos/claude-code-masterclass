# Route Models and Keep the Cache Warm

Most developers pick one model and keep it for everything, then wonder why a long session gets slow and expensive. You will run the same three tasks on Haiku, Sonnet and Opus, measure each run, and end with a routing policy in `CLAUDE.md` that rests on your own numbers. You will also log what the prompt cache does across warm turns, a `/model` switch and a mid-session `CLAUDE.md` edit.

What you practice here: measure first with `/usage` and `/context`, then write the rule.

Duration: about 70 minutes.

Teaching for this lab lives in [Select the Right Model and Keep the Prompt Cache Warm](../../../demos/01-fundamentals/04-model-selection/readme.md); the cache mechanics are under [Keep the Prompt Cache Warm](../../../demos/01-fundamentals/04-model-selection/readme.md#keep-the-prompt-cache-warm).

Each step contains:

- **Goal**: what you are building
- **Prompt**: paste this into Claude Code
- **Expected result**: what the outcome looks like

You build three files in the starter folder: `ROUTING-NOTES.md` (one measured row per run), a `## Model routing` section in `CLAUDE.md`, and `CACHE-NOTES.md` (one row per cache reading).

## Where to Open Claude Code

The starter is a small Python quoting library for parcel shipping with a `CLAUDE.md` and four passing tests. Open Claude Code inside the starter folder, because `CLAUDE.md` loads from the directory the session starts in and Steps 5 and 8 depend on that. Run this from the repo root.

```bash
cd labs/01-fundamentals/03-route-models-and-cache/starter && claude
```

```powershell
cd labs/01-fundamentals/03-route-models-and-cache/starter; claude
```

Other instruction files load alongside the starter's `CLAUDE.md`: any `CLAUDE.md` in a parent folder and your user-level one. Every context reading in this lab is therefore larger than a standalone project would show. The comparison between models stays valid because every run carries the same overhead.

## How to Take a Reading

Two commands produce all the numbers in this lab. `/usage` reports session totals per model: input tokens, output tokens, cache read, cache write and cost. `/context` reports how full the window is and which part of it is the largest.

The totals only grow, so a run is measured as the difference between two readings. For every run in Steps 2 to 4 you do the same five actions:

1. `/clear` to start from an empty conversation.
2. `/model <tier>` to select the model under test.
3. `/usage` and copy the line for that model (the reading before).
4. Paste the task prompt.
5. `/usage` and `/context` again (the reading after), then record the row.

The task prompts never ask Claude to edit a file. Each one asks for a reply only, so every run starts from the same untouched code and the only variable is the model.

---

## Step 1: Create the Notes Files

**Goal:** Start with two empty tables so every later step has a place to record into.

**Prompt:**

```text
Create two files in this folder.

ROUTING-NOTES.md: a heading "# Routing notes" and a Markdown table with the columns
Task | Model | Input | Output | Cache write | Cache read | Context used | Verdict
and no rows yet.

CACHE-NOTES.md: a heading "# Cache notes" and a Markdown table with the columns
Turn | Action | Cache write | Cache read | What I expected | What happened
and no rows yet.

Change nothing else.
```

**Expected result:** two files, each holding a heading and an empty table. Run `python -m unittest discover -s tests` in a second terminal if you want to see the starter's four tests pass before you begin.

---

## Step 2: Run Task A, a Mechanical Rename, on All Three Tiers

**Goal:** Learn what a task with one correct answer costs on each tier.

Task A is fully specified and checkable. Pass means the diff touches exactly three files (`shipping/rates.py`, `shipping/quotes.py`, `tests/test_quotes.py`) and changes nothing except the function name.

Run it three times, once per tier, using the five actions from [How to Take a Reading](#how-to-take-a-reading). The model line is `/model haiku`, then `/model sonnet`, then `/model opus`.

**Prompt:**

```text
Rename parcel_price_cents to price_parcel_cents everywhere it is defined or used in this project. Do not edit any file. Reply with one unified diff and nothing else.
```

After each run, record the row:

```text
Add a row to ROUTING-NOTES.md for task A on <tier>. Usage before: <paste>. Usage after: <paste>. Context used: <paste>. Compute Input, Output, Cache write and Cache read as after minus before. Set Verdict to pass or fail, with a reason of at most ten words, based on whether the diff touches exactly rates.py, quotes.py and tests/test_quotes.py and nothing else.
```

**Expected result:** three rows for task A. On a task this mechanical the diffs usually match across tiers, and Haiku shows the smallest output and cost. If one tier misses the test file or rewrites more than the name, that row is a fail, and the reason is the first evidence for your policy.

---

## Step 3: Run Task B, a Diagnosis, on All Three Tiers

**Goal:** Find out whether finding a bug needs a stronger tier than renaming does.

The starter hides one defect: `billable_kg` in `shipping/rates.py` uses floor division, so 1500 g bills as 1 kg and anything under 1000 g bills as 0 kg. Pass means the reply names `billable_kg` and floor division as the cause and proposes rounding up.

Repeat the five actions for `/model haiku`, `/model sonnet` and `/model opus`.

**Prompt:**

```text
Customers report that a 1.5 kg parcel to Germany costs exactly the same as a 1.0 kg parcel, and a 900 g parcel is sometimes cheaper than the base rate suggests. Find the cause in this codebase. Do not edit any file. Reply with the cause in two sentences and the one-line fix.
```

Record each row with the same pattern as Step 2:

```text
Add a row to ROUTING-NOTES.md for task B on <tier>. Usage before: <paste>. Usage after: <paste>. Context used: <paste>. Compute Input, Output, Cache write and Cache read as after minus before. Set Verdict to pass or fail, with a reason of at most ten words, based on whether the reply names billable_kg and floor division and proposes rounding up.
```

**Expected result:** three more rows. Expect the cheaper tiers to find this bug, because the code is small and the symptom points at weight. The interesting rows are the ones where a tier reads more files than it needs, which shows up as a larger Input and a larger Context used.

---

## Step 4: Run Task C, a Design Decision, on All Three Tiers

**Goal:** See where the strongest tier earns its cost.

Task C has several defensible answers and an expensive wrong one. Pass means three designs that differ in structure (three spellings of one idea fail), each naming the files it would change, plus a pick that gives a concrete reason for rejecting at least one alternative.

Repeat the five actions for `/model haiku`, `/model sonnet` and `/model opus`.

**Prompt:**

```text
We are adding a second carrier with its own zone table, its own per-kilo rates and a 12 percent fuel surcharge. Propose three different designs for this in the current codebase. For each, name the files it changes and its main risk. Then pick one and say which of the other two you rejected and why. Do not edit any file.
```

Record each row:

```text
Add a row to ROUTING-NOTES.md for task C on <tier>. Usage before: <paste>. Usage after: <paste>. Context used: <paste>. Compute Input, Output, Cache write and Cache read as after minus before. Set Verdict to pass or fail, with a reason of at most ten words, based on whether the three designs differ in structure, name their files, and the pick rejects one alternative with a concrete reason.
```

**Expected result:** nine rows in total. Compare the answers side by side: the strongest tier tends to produce the sharper rejection reasoning, and the cheapest tier tends to produce designs that are variations on one idea. Model output varies from run to run, so confirm the tendency in your own table.

---

## Step 5: Write the Routing Policy

**Goal:** Turn the nine rows into rules that live where the next session will read them.

**Prompt:**

```text
Read ROUTING-NOTES.md. Append a section titled "## Model routing" to CLAUDE.md with one line per task class: mechanical edits, diagnosis, and design decisions. Each line names the cheapest tier whose verdict was pass in my table, and quotes that tier's Output and Context used figures as evidence. Add one final line: if a run fails its check, retry once one tier up before changing the prompt. Use only numbers that appear in ROUTING-NOTES.md and change nothing else in CLAUDE.md.
```

**Expected result:** a `## Model routing` section with four lines at the end of `CLAUDE.md`. Check every figure against `ROUTING-NOTES.md` yourself. A line that cites a number your table does not contain is the failure to catch here.

---

## Step 6: Log Cache Behaviour Across Warm Turns

**Goal:** Watch the prompt cache fill and then get read, on a session that keeps one model.

Start clean on a single model. Each turn below adds to the same conversation, so the earlier prefix should come from cache. After every turn run `/usage` and note the totals for Sonnet.

```text
/clear
/model sonnet
```

Turn 1:

```text
@shipping/zones.py @shipping/rates.py

Summarize how a country becomes a price. Five sentences at most.
```

Turn 2:

```text
@shipping/parcels.py @shipping/quotes.py

How does chargeable weight reach the final price? Five sentences at most.
```

Turn 3 reads no new file:

```text
Without reading any new files: if the volumetric divisor changed from 5000 to 6000, which function changes and which existing test would notice?
```

Turn 4:

```text
@tests/test_quotes.py

Which assertion in this file would break if FUEL_SURCHARGE_PERCENT became 9?
```

After each turn, record it:

```text
Add a row to CACHE-NOTES.md for turn <n>, action "warm turn". Usage before: <paste>. Usage after: <paste>. Compute Cache write and Cache read as after minus before. In "What I expected" write what the topic readme predicts for this turn, in one sentence. In "What happened" write whether write or read dominated.
```

**Expected result:** four rows. Cache read grows turn by turn because each turn re-reads a longer prefix from cache, and cache write stays small after the first turn because only the new messages are written. Turn 1 typically carries the largest write since your `CLAUDE.md` changed in Step 5. If turn 1 shows a small write, an earlier run in this directory kept that prefix warm, and the pattern from turn 2 onward is still the signal.

---

## Step 7: Switch Models and Log the Cost

**Goal:** Put a number on what a `/model` switch costs in a conversation that is already long.

Stay in the same session. Switch to Opus, then ask a question that needs no files and almost no output:

```text
/model opus
```

```text
Without reading any files, restate in two sentences what you said about chargeable weight earlier.
```

Then run `/usage` and record it:

```text
Add a row to CACHE-NOTES.md for turn 5, action "/model switch to opus". Usage before: <paste the sonnet and opus lines from turn 4>. Usage after: <paste the sonnet and opus lines now>. Compute Cache write and Cache read for the opus line only. In "What I expected" write what the topic readme says a model switch does. In "What happened" compare the opus write figure with the largest write in the earlier rows.
```

**Expected result:** a fifth row where Opus shows a cache write close to the size of the whole conversation so far and almost no cache read, on a turn that produced two sentences. Each model owns its own cache, so the switch rebuilt the entire history. This is the reason to apply the Step 5 policy at the start of a session.

---

## Step 8: Prove a Mid-Session CLAUDE.md Edit Stays Inert

**Goal:** See for yourself that editing the routing policy during a session changes nothing until `/clear`.

Stay in the same session. Open `CLAUDE.md` in your editor, find the line in `## Model routing` that routes mechanical edits, change the tier name on that line to `opus`, and save. Make the edit outside Claude Code, so it never appears as a tool call in the conversation.

Back in the session, switch to Sonnet and ask:

```text
/model sonnet
```

```text
Quote the line in the Model routing section of CLAUDE.md that routes mechanical edits, exactly as it reads.
```

Run `/usage`, then record it:

```text
Add a row to CACHE-NOTES.md for turn 6, action "CLAUDE.md edited mid-session". Usage before: <paste>. Usage after: <paste>. Compute Cache write and Cache read as after minus before. In "What I expected" write what the topic readme says about editing CLAUDE.md mid-session. In "What happened" write which tier name Claude quoted.
```

Now load the edit:

```text
/clear
```

```text
Quote the line in the Model routing section of CLAUDE.md that routes mechanical edits, exactly as it reads.
```

Run `/usage` once more and record it as turn 7 with the action "after /clear".

**Expected result:** two rows. Before `/clear`, Claude quotes the original tier name, because the file was read once at session start; after `/clear`, it quotes `opus`. The silent part is the lesson: no warning appeared that your edit was ignored. If your version of Claude Code quotes the new tier before `/clear`, record that in the "What happened" cell, since this behaviour can change between releases.

Finish by restoring the line to the tier your measurements chose, by hand, so the policy matches `ROUTING-NOTES.md` again.

---

## Step 9: Test the Policy and Write the Cache Rules

**Goal:** Check that the policy routes tasks you did not measure, and keep the cache findings in one place.

Start a fresh session so the restored `CLAUDE.md` loads:

```text
/clear
```

**Prompt:**

```text
Using only the Model routing section of CLAUDE.md, assign a tier to each task and quote the line that decided it:
1. Change FUEL_SURCHARGE_PERCENT from 8 to 9.
2. A 12 kg parcel to Japan quotes 40 cents too low; find out why.
3. Design how returns and refunds should be quoted.
Do not edit any file.
```

Then ask for the rules:

```text
Read CACHE-NOTES.md. Append a section "## Rules" with three lines, each starting with a verb, that follow from my rows: when to choose a model, what a /model switch costs, and when a CLAUDE.md edit takes effect. Use only figures that appear in the table.
```

**Expected result:** three assignments that match your Step 5 lines (typically the cheap tier for the constant change, a middle or cheap tier for the diagnosis, the strongest tier for the design), each with a quoted line. `CACHE-NOTES.md` ends with a `## Rules` section of three lines, each backed by a row you measured. Your deliverables are `ROUTING-NOTES.md`, the `## Model routing` section in `CLAUDE.md`, and `CACHE-NOTES.md`.
