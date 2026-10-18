# Fork a Skill into a Subagent

A code audit reads a dozen files, and every line it reads stays in your session until you clear it. By the third audit the conversation is mostly old evidence and the model has less room for the work you care about. You finish with two audit skills over the same project, one inline and one forked into an Explore subagent, and with `/context` numbers that show what each one costs your main session.

What you practice here: inject the evidence with `` !`command` `` and fork the reading into a subagent so only the verdict returns.

Duration: about 50 minutes.

------

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Recipe**: a complete prompt you paste into Claude Code
- **Expected Outcome**: observable artefacts that confirm success

The mechanics are settled, so the steps are recipe-only. The concepts live in [Topic 04](../../demos/03-skills/04-live-data-and-subagents/readme.md); the lab applies them and leaves the explanation there.

Work in the pristine starter [fork-skill/](fork-skill). It holds `ledger-service`, a small invoicing backend with eight files in `src/` and nine open `TODO` and `FIXME` markers. Their wording does not always match what they cost, which is what the audit has to see through.

---

## Where to Open Claude Code

Skills load from the `.claude/skills/` of the directory the session starts in, so open Claude Code inside the starter. Run this from the repo root; both lines work unchanged in PowerShell.

```bash
cd labs/03-skills/fork-skill
claude
```

If you use the VS Code extension, open `fork-skill` as the workspace folder (File > Open Folder) before starting a session. Every path below is relative to `labs/03-skills/fork-skill/`.

---

## Step 1: Build the Inline Audit Skill

**Overview:** The inline variant is the baseline. Its prompt arrives with the marker list and line counts already filled in, then Claude reads each flagged file in your session and ranks the markers.

**Recipe:**

````text
Create the file .claude/skills/ledger-audit-inline/SKILL.md in this folder with exactly this content, and write nothing else:

---
name: ledger-audit-inline
description: Audit the open TODO and FIXME markers in the ledger-service project and rank them by risk. Use when the user asks for a ledger audit, a risk ranking of the open markers, or which marker to fix first.
---

# ledger-audit-inline

## Open markers

!`grep -rn "TODO\|FIXME" ${CLAUDE_PROJECT_DIR}/src`

## Line counts

!`wc -l ${CLAUDE_PROJECT_DIR}/src/*.js`

## Task

Read every file named in the markers above and judge what each marker costs by reading the code around it. Treat the comment's wording as a hint at most.

Return a list ranked by risk, highest first, one line per marker:

<file>:<line> | <impact if left unfixed> | <effort>

Close with one sentence naming what to fix first. Return nothing else: no preamble, no file summaries, no restatement of the markers.
````

**Expected Outcome:** `.claude/skills/ledger-audit-inline/SKILL.md` exists and is the only new file. Type `/` in the prompt and `ledger-audit-inline` appears in the list. The two `` !`command` `` lines are still literal text in the file; they turn into real output only when the skill is invoked.

---

## Step 2: Run It and Measure What It Leaves Behind

**Overview:** The cost of a skill is the tokens it leaves in your session. Measure a clean session first, run the inline audit, then measure again.

**Recipe:**

```text
/clear
```

```text
/context
```

Note the tokens on the Messages row. Then run the skill and read the context again:

```text
/ledger-audit-inline
```

```text
/context
```

**Expected Outcome:** The audit returns nine lines in the form `<file>:<line> | <impact> | <effort>` and a closing sentence. The first line is `payments.js:15`, the refund that is recorded before the gateway confirms it, because a declined refund still lowers the customer's balance. Cosmetic markers such as `payments.js:21` (gateway latency logging) and `invoices.js:17` (tax split in the PDF) rank last.

The transcript above the answer shows several `Read` calls, one per flagged file. The Messages row after the run is clearly larger than before it; write both numbers into this table, which you complete in Step 4:

| Variant | Messages before | Messages after | Difference |
|---------|-----------------|----------------|------------|
| Inline  |                 |                |            |
| Fork    |                 |                |            |

---

## Step 3: Fork the Same Audit into an Explore Subagent

**Overview:** Copy the skill and change only the frontmatter. `context: fork` turns the rendered file into the prompt of a subagent, and `agent: Explore` gives that subagent a read-only toolset. `background: false` makes the turn wait for the verdict.

**Recipe:**

````text
Create the file .claude/skills/ledger-audit-fork/SKILL.md in this folder with exactly this content, and write nothing else:

---
name: ledger-audit-fork
description: Audit the open TODO and FIXME markers in the ledger-service project in an isolated subagent and return only the ranking. Use when the user asks for a forked ledger audit, a quiet risk ranking, or an audit that must not fill the main session.
context: fork
agent: Explore
background: false
---

# ledger-audit-fork

## Open markers

!`grep -rn "TODO\|FIXME" ${CLAUDE_PROJECT_DIR}/src`

## Line counts

!`wc -l ${CLAUDE_PROJECT_DIR}/src/*.js`

## Task

Read every file named in the markers above and judge what each marker costs by reading the code around it. Treat the comment's wording as a hint at most.

Return a list ranked by risk, highest first, one line per marker:

<file>:<line> | <impact if left unfixed> | <effort>

Close with one sentence naming what to fix first. Return nothing else: no preamble, no file summaries, no restatement of the markers.
````

**Expected Outcome:** `.claude/skills/ledger-audit-fork/SKILL.md` exists. Compare it with the inline file: the name, description and heading lines differ, the rest of the body is identical, and the frontmatter gained three lines. Those three lines are the whole difference between a skill that fills your session and one that does not.

---

## Step 4: Run the Fork and Compare

**Overview:** Run the forked audit from a clean session, measure it the same way, and put the two variants side by side.

**Recipe:**

```text
/clear
```

```text
/context
```

```text
/ledger-audit-fork
```

```text
/context
```

**Expected Outcome:** The turn waits, then returns the same kind of answer as Step 2: nine ranked lines and one closing sentence, with `payments.js:15` first. This time the transcript contains no `Read` calls from your session; the subagent made them in its own context and discarded them.

The Messages row grew by roughly the size of the verdict, a fraction of the inline growth. Fill in the Fork row of the table from Step 2. The two rankings may order the middle markers differently, since each run is a fresh judgement; the top and bottom should agree.

---

## Step 5: Change the Data and Rerun Without Touching the Skill

**Overview:** Injection runs at invocation, so the skill always reflects the project as it is now. Add a marker to the code and watch it appear in the verdict with no edit to the skill.

**Recipe:**

```text
Add this comment on its own line directly above the toCsv function in src/export.js and change nothing else:

// FIXME: toCsv writes customer text unescaped, a cell starting with = runs as a formula in Excel
```

```text
/clear
```

```text
/ledger-audit-fork
```

**Expected Outcome:** The verdict now has ten lines, including an `export.js:` entry for the CSV formula risk; it ranks high because spreadsheet formulas run on the machine of whoever opens the export. The skill file did not change between the two runs, so the new line can only have come from the grep that ran before Claude saw the prompt.

---

## Step 6: Repeat the Audit and Watch the Costs Diverge

**Overview:** One run hides the real difference. An audit you run every day shows it, because inline evidence accumulates and the fork's does not.

**Recipe:**

```text
/clear
```

```text
/context
```

Run the inline audit twice, reading the context after each run:

```text
/ledger-audit-inline
```

```text
/context
```

```text
/ledger-audit-inline
```

```text
/context
```

Clear, then repeat the same sequence with the forked skill:

```text
/clear
```

```text
/ledger-audit-fork
```

```text
/context
```

```text
/ledger-audit-fork
```

```text
/context
```

**Expected Outcome:** After two inline runs the Messages row has grown by the full evidence cost twice, plus the verdicts. After two forked runs it has grown by two verdicts, roughly a thousand tokens each. Each `/context` table is also kept in the session, so a later reading carries the earlier tables and rises more than the runs alone. Extend the table from Step 2 with the two new readings per variant; the gap between the rows widens with every run.

---

## Verify

Confirm that the two files differ only in the fork lines. Run this from `fork-skill/`.

```bash
diff .claude/skills/ledger-audit-inline/SKILL.md .claude/skills/ledger-audit-fork/SKILL.md
```

```powershell
Compare-Object (Get-Content .claude\skills\ledger-audit-inline\SKILL.md) (Get-Content .claude\skills\ledger-audit-fork\SKILL.md)
```

The output lists the changed `name`, `description` and heading lines and the three added lines `context: fork`, `agent: Explore` and `background: false`. The body differs only in its `#` heading line.

The injected commands run through Bash. On a machine without Git Bash, add `shell: powershell` to the frontmatter and use these twins:

```powershell
Select-String -Path "$env:CLAUDE_PROJECT_DIR\src\*.js" -Pattern "TODO|FIXME"
Get-ChildItem "$env:CLAUDE_PROJECT_DIR\src\*.js" | ForEach-Object { "$($_.Name) $((Get-Content $_).Count)" }
```

To undo the lab, delete `.claude/skills/` and remove the FIXME line from Step 5 in `src/export.js`; the other starter files stay as they were.
