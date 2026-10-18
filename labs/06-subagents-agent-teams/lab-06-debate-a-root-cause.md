# Debate a root cause with a team

An agent that finds one plausible cause for a bug stops looking, and you cannot tell a confirmed theory from an unchallenged one. You end with a `findings.md` written by five teammates who each defended a different cause, ran a one-variable control experiment outside your project, and recorded exactly what killed every theory that did not survive.

What you practice here: give each teammate one hypothesis, make it falsify the others with before and after control runs, and accept only the explanation that survived the attack.

Duration: about 80 minutes.

The teaching behind this lab is in [Make teammates argue, and gate what they ship](../../demos/06-subagents-agent-teams/07-debate-and-control/readme.md), and the same debate is shown in [Find a root cause by making five agents argue](../../demos/06-subagents-agent-teams/07-debate-and-control/demo-competing-hypotheses.md). Plan approval from the same topic is practised in [Spawn a review team and steer it](lab-04-spawn-a-review-team.md); this lab covers the competing-hypotheses capability.

**What you need:** Python 3.10 or newer on PATH, and Claude Code 2.1.178 or newer. Agent teams are experimental, so `claude --version` below that stops the lab.

**What it costs:** five teammates are five separate Claude instances, so this run bills roughly five times a single-session investigation. The lab teaches you to judge when that is worth paying.

------

## Where to Open Claude Code

Open Claude Code inside your solution copy. Teammates inherit the lead's working directory, so the folder you launch from is the project the team investigates and the place `findings.md` lands. Step 0 creates the copy; run this from the repo root once it exists.

```bash
cd labs/06-subagents-agent-teams/06-debate-a-root-cause/invoice-totals-py-solution
claude
```

The same two commands work in PowerShell. Every path in the prompts below is relative to `invoice-totals-py-solution`, and control experiments run in a scratch copy outside it.

---

## Step 0: Create Your Solution Folder

**Goal:** Give the team a working copy so the checked-in starter stays pristine.

`invoice-totals-py` is the starter: a script that totals orders per customer and checks them against a finance sheet. The team writes `findings.md` into the copy, and the control experiments never touch either folder. Run the copy once from the repo root, before you open Claude Code.

```bash
cp -r labs/06-subagents-agent-teams/06-debate-a-root-cause/invoice-totals-py labs/06-subagents-agent-teams/06-debate-a-root-cause/invoice-totals-py-solution
```

```powershell
Copy-Item -Recurse labs/06-subagents-agent-teams/06-debate-a-root-cause/invoice-totals-py labs/06-subagents-agent-teams/06-debate-a-root-cause/invoice-totals-py-solution
```

If the `-solution` folder already exists, both commands nest a second copy inside it. Delete the nested copy before you continue.

Expected result: `invoice-totals-py-solution` holds the same files as the starter, and `findings.md` is not one of them.

---

## Step 1: Reproduce the Bug Yourself

**Goal:** See the symptom with your own eyes before any agent explains it to you.

**Overview:** A debate needs a fixed symptom every teammate argues about. If you have not run the script, you cannot judge whether a teammate's evidence describes the same failure.

**Recipe:**

```bash
python invoice_totals.py
```

**Expected Outcome:** three lines, one per customer, with Globex marked `ok` and the other two marked `MISMATCH`:

```text
Globex      74.40 EUR  finance    74.40  ok
Acme       178.80 EUR  finance   202.80  MISMATCH
Initech     27.00 EUR  finance    29.40  MISMATCH
```

Acme is 24.00 short and Initech is 2.40 short. Both gaps are far larger than a rounding cent, which is a fact the team will have to account for.

---

## Step 2: Turn Agent Teams On

**Goal:** Enable the experimental flag and prove it took effect.

**Overview:** Agent teams are off by default. With the flag unset, Claude spawns sub-agents, and sub-agents cannot message each other, so the debate never happens and you still get a plausible answer.

**Recipe:**

If you finished Lab 04 the flag is already set. Otherwise add this to `~/.claude/settings.json` (on Windows `$HOME\.claude\settings.json`), keep everything already in the file, then restart with `/exit` and `claude`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**Expected Outcome:** with the session running, `~/.claude/teams/` contains a `session-XXXXXXXX` folder whose `config.json` lists one member, the lead. If the folder is missing, the flag did not apply and every later step runs as sub-agents.

---

## Step 3: Choose Five Hypotheses That Can Each Win

**Goal:** Split the search by layer, so the five theories cannot all be the same theory.

**Overview:** Five teammates holding the same suspicion are one investigator with a larger bill. The split must cover genuinely different layers, and each theory must be able to produce the symptom on its own, otherwise a refutation proves nothing.

**Research / Planning / Discussion:**

```text
Read every .py file, config.json, orders.csv and finance.csv in this folder, and
run python invoice_totals.py once. Finance says two invoices are wrong by far
more than a cent.

Propose five distinct root-cause hypotheses at five different layers of this
script. For each one, state the file it lives in, why it could produce this exact
symptom, and the single variable you would change in a copy of the project to
kill it. Tell me which two hypotheses you find most convincing and why that is a
reason to be suspicious of them.
```

**Finding:** five rows at five layers, such as input reading, price calculation, tax and rounding, customer grouping, and settings, each with a one-variable test. Push back on any hypothesis whose test changes two things at once, because a two-variable result cannot refute anything. Also push back if the answer commits to one cause already; the point of the step is to keep five alive.

**Recipe:**

```text
Use these five hypotheses, one per teammate, named rounding, parsing, tax,
grouping and pricing:
- rounding: floating point arithmetic or per-line rounding drifts the totals
- parsing: loader.py drops or mangles rows from orders.csv
- tax: the tax rate or its application is wrong
- grouping: customer names are split or merged wrongly in grouping.py
- pricing: pricing.py charges the wrong unit price for some lines
```

**Expected Outcome:** a list of five named hypotheses you can paste into the next step. Your own Research answer may order the layers differently; the five names are what the later prompts depend on.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 4: Spawn the Five Debaters

**Goal:** Get five named teammates, each loyal to one theory and told to attack the others.

**Overview:** The instruction to argue is the mechanism. A prompt that only assigns hypotheses produces five parallel monologues, while one that tells teammates to disprove each other produces a debate whose survivor is worth acting on.

**Recipe:**

```text
Spawn 5 agent team teammates (sub-agents cannot message each other) named rounding, parsing, tax,
grouping and pricing. Each defends exactly one hypothesis:
- rounding: floating point arithmetic or per-line rounding drifts the totals
- parsing: loader.py drops or mangles rows from orders.csv
- tax: the tax rate or its application is wrong
- grouping: customer names are split or merged wrongly in grouping.py
- pricing: pricing.py charges the wrong unit price for some lines

The symptom: python invoice_totals.py reports Acme and Initech as MISMATCH
against finance.csv while Globex is ok.

Each teammate defends its own hypothesis and tries to falsify the other four. Have
them message each other by name to attack each other's theories, like a scientific
debate. Do not change any source file in this folder.
```

**Expected Outcome:** five rows in the agent panel below the prompt input, one per name. The panel also lists sub-agents, so confirm with the team config: `~/.claude/teams/session-XXXXXXXX/config.json` now lists six members, the lead and the five teammates.

---

## Step 5: Demand a Control Experiment from Each

**Goal:** Make every teammate prove its position with a before run and an after run that differ by one variable.

**Overview:** A theory that explains the symptom has not yet been tested. A control experiment changes one thing in a copy and compares the two runs, and it is the only evidence a rival teammate cannot wave away.

**Recipe:**

```text
Before anyone writes a conclusion: every teammate must produce a control
experiment for its own hypothesis. Copy this project to a scratch folder outside
this folder, in the operating system's temp directory. Change exactly one thing
there and report the output of the run before the change and the run after it.
A hypothesis with no control experiment is rejected by default. Never run an
experiment inside this folder.
```

**Expected Outcome:** each teammate reports two runs of `python invoice_totals.py`, side by side, and names the single thing it changed. The scratch folders appear outside the repo, and `git status` in your solution folder shows no changes to any `.py`, `.csv` or `.json` file. A report that changed two variables at once is a defect, so send it back.

---

## Step 6: Watch the Argument and Steer It

**Goal:** Read the traffic between teammates, and step in where one of them is anchoring.

**Overview:** The value of the run is in the messages between teammates, and the lead's summary hides them. Reading them tells you whether a refutation was earned or conceded without proof.

**Recipe:**

Press Ctrl+T to toggle the shared task list. Select one teammate in the agent panel with the up and down arrows, press Enter to open its transcript, and read what it received from the others.

If a teammate has stopped defending its theory without evidence, message it directly from its transcript:

```text
Do not concede yet. State which single-variable result of another teammate
refuted your hypothesis, and quote the two runs. If you cannot quote them, keep
defending.
```

**Expected Outcome:** the task list shows each teammate's work moving from pending to in progress to completed with the teammate named as owner. In the transcripts, look for one message where a teammate accepts another's proof, such as `rounding` conceding after reading a result that left the 24.00 gap unchanged. A concession that quotes no run is the signal to send the message above.

---

## Step 7: Write the Consensus Down

**Goal:** Produce one shared file that names the survivor and records every refuted theory.

**Overview:** The deliverable is the record of what was killed and by what. A bare conclusion cannot be checked later, while a refutation table can.

**Recipe:**

```text
When a consensus emerges, write findings.md in this folder with:
- The surviving explanation, with file and line references.
- The evidence: the failing run as shipped, and the single-variable control run
  that closes the gap to finance.csv.
- A table with one row per rejected hypothesis: the teammate, the one variable it
  changed, and the result that refuted it.
- A section for anything the team noticed that is not the reported bug.
Do not change any source file in this folder.
```

**Expected Outcome:** `findings.md` exists in `invoice-totals-py-solution` with a survivor, a before and after pair, and a refutation table of four rows. Each row names a teammate, its one change and the run that refuted it, for example `tax | set tax_rate to 0 in the copy | every total dropped and the gap to finance stayed`. Every `.py` file is still byte-identical to the starter.

---

## Step 8: Check the Verdict by Hand

**Goal:** Reproduce the survivor's control experiment yourself before you believe it.

**Overview:** Five agents agreeing is a claim, and the table is only as good as the runs behind it. One control you run yourself tells you whether the team's evidence is real.

**Recipe:**

Read the single-variable control in `findings.md`, copy the project to a scratch folder outside the repo, and apply that one change there. Run the script in the scratch copy:

```bash
python invoice_totals.py
```

Then confirm your solution folder was never edited. Run this from the repo root:

```bash
git status --short labs/06-subagents-agent-teams/06-debate-a-root-cause
```

**Expected Outcome:** in the scratch copy all three lines read `ok`, so that one change closes the gap to `finance.csv`. The `git status` output lists the new folders as untracked and no modified files, so the investigation changed no source. If your run still shows a `MISMATCH`, the survivor is unproven, and you send the team back to Step 5.

---

## Step 9: Close the Team Down

**Goal:** End the run deliberately and know what survives it.

**Recipe:**

```text
Ask each teammate to shut down.
```

**Expected Outcome:** the lead sends a shutdown request to each teammate and each can approve it or reject it with a reason; a teammate finishes its current tool call first, so shutdown is not instant. The team's shared directories are removed when the session ends, and the task list under `~/.claude/tasks/` persists locally until `cleanupPeriodDays` ages it out.

You now hold `findings.md`: one explanation that survived four attacks, the control run that proves it, and a refutation for each of the four theories that did not.
