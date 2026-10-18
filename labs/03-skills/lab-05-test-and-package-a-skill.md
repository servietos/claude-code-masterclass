# Test a Skill Until It Is Safe to Hand Over and Package It

A skill you wrote works for you, because you know the words that make it load. A teammate phrases the request differently, the skill stays silent, and the work falls back to a plain answer nobody notices is worse. This lab proves a release-notes skill fires when it should and stays quiet when it should not, grades what it writes against a planted set of defects, patches each failure in the layer that owns it, and ends with a folder and an archive another person can install.

What you practice here: a trigger matrix and a functional check run headlessly with `claude -p` and `--disallowedTools`, one patch per recorded failure, and a package that holds the skill and nothing else.

Duration: about 90 minutes.

------

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research**: an open prompt to reason through the problem (decision steps only)
- **Finding**: what to read and judge in Claude's response (decision steps only)
- **Recipe**: a complete prompt or command you paste
- **Expected Outcome**: observable artefacts that confirm success

Steps that are settled mechanics keep only the Overview, the Recipe and the Expected Outcome. The concepts live in [Topic 05](../../demos/03-skills/05-test-and-package/readme.md); the lab applies them and leaves the explanation there.

Work in the pristine starter [release-bench/](release-bench). It holds `orders-cli` at version 2.4.0, a list of twelve commits in `data/commits.txt`, the skill under test in `.claude/skills/release-notes/SKILL.md`, and four runner scripts. The skill is deliberately weak: a one-line description and a three-line body. Every file you create lands in `tests/` or `dist/`, which the starter does not contain.

---

## Where to Open Claude Code

Skills load from the `.claude/skills/` of the directory the session starts in, so open Claude Code inside the starter. Run this from the repo root; both lines work unchanged in PowerShell.

```bash
cd labs/03-skills/release-bench
claude
```

If you use the VS Code extension, open `release-bench` as the workspace folder (File > Open Folder) before starting a session. Keep this interactive session for authoring. Open a second terminal in the same folder for the sweeps, because each one runs several minutes. Every path below is relative to `labs/03-skills/release-bench/`.

---

## Step 1: Read What Claude Sees Before a Skill Loads

**Overview:** Before any test, find out which part of the skill takes part in the loading decision. That one part is what the trigger matrix measures, and the other parts are what the functional check measures later.

**Recipe:**

```text
Read .claude/skills/release-notes/SKILL.md, data/commits.txt and package.json. Do not change anything.
1. Quote the one frontmatter field that is in context before this skill loads, and say why the body is not.
2. List the three layers of this skill: the description, the workflow steps, the output format. For each,
   name one thing it controls and one failure it would cause if it were wrong.
3. Count the commits in data/commits.txt that a customer would care about, and the ones that are internal.
Answer in a table for item 2 and one line each for items 1 and 3.
```

**Expected Outcome:** The quoted field is `description: Handles releases, versions and changelogs for the project.` and the answer states that the body only enters context after the decision is made. The table names a description failure (never fires, or fires on unrelated work), a workflow failure (an input never read) and a format failure (the output cannot be used as it is). Your count of customer-facing commits is six, counting the `feat!` line, and the six internal ones are the `chore`, `ci`, `docs`, `refactor` and `test` lines.

---

## Step 2: Write the Trigger Matrix

**Overview:** A trigger matrix is a file of prompts, each with the outcome you expect: fire or no-fire. Both directions matter, because a skill that fires on version bumps and tag questions gets switched off as fast as one that never fires. The matrix is the first deliverable of the lab.

**Recipe:**

````text
Create the file tests/trigger-prompts.tsv with exactly this content, tab-separated, one row per line, and write nothing else:

fire	Write the release notes for this version from the commit list.
fire	What should I tell our users about what shipped since the last release?
fire	Turn data/commits.txt into a changelog entry for customers.
fire	Draft the announcement of what changed in this version for the customer newsletter.
no-fire	Bump the version in package.json to 2.5.0.
no-fire	Explain what semantic versioning means for the major number of this package.
no-fire	Write a one-line commit message for a fix to the CSV export.
no-fire	Explain the difference between a git tag and a git branch.
````

**Expected Outcome:** `tests/trigger-prompts.tsv` exists with eight lines, four starting with `fire` and four with `no-fire`, and the separator after each outcome word is a tab. Check it:

```bash
awk -F'\t' '{print NF, $1}' tests/trigger-prompts.tsv
```

```powershell
Get-Content tests\trigger-prompts.tsv | ForEach-Object { "$(($_ -split "`t").Count) $(($_ -split "`t")[0])" }
```

Every line prints `2` followed by its outcome word. A line that prints `1` has spaces where the tab belongs.

---

## Step 3: Predict Before You Measure

**Overview:** Predicting a row from the description alone is a reasonable first pass and a poor test. Writing the predictions down first gives you something to be wrong about, which shows where your own reading of a description is unreliable.

**Research:**

```text
Read the description in .claude/skills/release-notes/SKILL.md and each row of tests/trigger-prompts.tsv.
For every row, predict whether a fresh session would load the skill, and give one sentence of reasoning
that quotes words from the description. Mark the rows where you are least sure. Save nothing yet.
```

**Finding:** A good answer quotes the description for every row and admits doubt on the version rows: the description says "versions", so `Bump the version in package.json` and the semantic-versioning question are plausible false fires. It should also doubt the two fire rows that never use the word "release" (the "what shipped" row and the newsletter row). If Claude predicts a clean pass on every row, push back and ask which words in the description would make it load for a bump request.

**Recipe:**

```text
Create tests/predictions.md with a table of the columns Row, Expected, Predicted, Confidence, Reason, one line per row of tests/trigger-prompts.tsv, using the predictions from this conversation. Write nothing else.
```

**Expected Outcome:** `tests/predictions.md` holds eight table rows. Keep it closed until Step 4 is done; the measurement is the answer and this file is the guess it is compared with.

---

## Step 4: Run the Trigger Sweep

**Overview:** Run every prompt as its own headless session, three times each, and count how often the transcript contains a call to the `Skill` tool that names `release-notes`. The scripts pass `--strict-mcp-config` so no MCP server dominates the wall time, and `--disallowedTools Edit Write NotebookEdit Bash PowerShell` so a measurement cannot modify the project. `--allowedTools` is an auto-approve list and does not restrict anything, so only `--disallowedTools` is used.

**Recipe:** In the second terminal, in `release-bench/`:

```bash
bash run-triggers.sh tests/trigger-prompts.tsv | tee tests/trigger-cases.md
```

```powershell
.\run-triggers.ps1 tests\trigger-prompts.tsv | Tee-Object tests\trigger-cases.md
```

**Expected Outcome:** After 24 sessions (allow five to ten minutes) the terminal prints a table with one row per prompt:

```text
| # | Expected | Fires | Observed | Verdict | Prompt |
|---|---|---|---|---|---|
| 1 | fire | 3/3 | fire | pass | Write the release notes for this version ... |
```

The Fires column is a count out of three, and `tests/trigger-cases.md` holds the same table. Expect the rows to differ from your predictions in at least one place. A row at 2/3 or 1/3 is a finding in its own right, because loading is a model decision and the same prompt can load on one run and skip it on the next.

Compare the table with `tests/predictions.md` and note where you were wrong. If every row passes, the description is not your weakest layer: record that and go straight to Step 6 to confirm it on unseen rows.

---

## Step 5: Patch the Description for Each Failure

**Overview:** A failure in this table belongs to the description and to nothing else. Adding trigger words to the body changes nothing, because the body is read only after the decision has been made. Patch only the rows that failed, and keep a log of what changed so the delta stays readable.

**Research:**

```text
Read tests/trigger-cases.md and .claude/skills/release-notes/SKILL.md. For each FAIL row, say whether the skill failed to load (a missed fire) or loaded when it should not have (a false fire), and which words of the current description caused it. Then propose the smallest rewrite of the description that fixes those rows without losing the ones that pass. Do not edit anything.
```

**Finding:** A good answer separates the two failure directions, because they need opposite edits: a missed fire needs the user's own phrasing in the description, and a false fire needs a clause that names what the skill is not for. Push back on any proposal that adds a long keyword list; the description should say what the skill produces and when, in one or two sentences, under the 1024 character frontmatter limit. Push back too if the rewrite touches the body, since no row of the matrix tests it.

**Recipe:**

```text
Edit only the description line in .claude/skills/release-notes/SKILL.md to close the FAIL rows in tests/trigger-cases.md.
- For every missed fire, add the user's phrasing from that row.
- For every false fire, add one clause that says what the skill is not for.
- Keep it under 1024 characters. Change nothing in the body.
If tests/trigger-cases.md has no FAIL row, change nothing and say so.
Then create tests/patches.md with a heading "Description" and the old and new description line, each in a text fence.
```

**Expected Outcome:** `SKILL.md` differs from the starter in the `description` line only, and `tests/patches.md` shows the old and new line. A typical new description names the output ("release notes or a changelog entry for customers, written from the commit list") and ends with a clause such as "Not for bumping versions, tagging or explaining versioning". If Claude found no FAIL row, the file is unchanged and `tests/patches.md` says so.

---

## Step 6: Re-Run the Sweep and Add Rows You Did Not Tune On

**Overview:** Re-running the rows you just fixed proves only that the patch fits those rows. A second file of unseen prompts tells you whether the description generalised, which is the case a stranger will test.

**Recipe:**

````text
Create the file tests/trigger-prompts-holdout.tsv with exactly this content, tab-separated, and write nothing else:

fire	Give me the what's-new text for 2.4.0 based on the commits.
fire	Summarise the user-visible changes in this version as bullet points for the website.
no-fire	Tag the current commit as v2.4.0 and push the tag.
no-fire	What are the steps to roll back a release if the deploy fails?
````

Then, in the second terminal:

```bash
bash run-triggers.sh tests/trigger-prompts.tsv | tee tests/trigger-cases-after.md
bash run-triggers.sh tests/trigger-prompts-holdout.tsv | tee tests/trigger-cases-holdout.md
```

```powershell
.\run-triggers.ps1 tests\trigger-prompts.tsv | Tee-Object tests\trigger-cases-after.md
.\run-triggers.ps1 tests\trigger-prompts-holdout.tsv | Tee-Object tests\trigger-cases-holdout.md
```

**Expected Outcome:** `tests/trigger-cases-after.md` holds the first eight rows again, and the rows that failed in Step 4 now read pass or show a higher count; `tests/trigger-cases-holdout.md` holds four new rows.

Keep `tests/trigger-cases.md` unchanged beside them so the before and after tables can be compared line by line. A holdout row that fails is a new finding: patch the description again with Step 5's recipe and re-run only the holdout file. Leave a failing holdout row where it is, because moving it into the main file to tidy the table hides the result.

---

## Step 7: Run the Functional Test

**Overview:** Loading is half the claim. Once the skill is loaded, does it produce what it promised? Run one firing prompt headlessly and save the answer, so you grade a file and not a memory.

**Recipe:**

```bash
bash run-functional.sh "Write the release notes for this version from the commit list."
```

```powershell
.\run-functional.ps1 -Prompt "Write the release notes for this version from the commit list."
```

**Expected Outcome:** The answer prints in the terminal and is saved as `tests/functional-run.md`. It is a list of release-note bullets derived from `data/commits.txt`. With the starter's three-line body the heading is typically a bare "Release notes" with no version, and the list contains internal commits such as the eslint bump and the lockfile update. The wording varies from run to run; what you do with it is the next step.

---

## Step 8: Grade the Output Against Five Properties

**Overview:** A skill that only says "looks good" passes every test on clean input, so grade the output against properties the fixture was built to expose. The five properties below each map to a different part of the skill, which tells you where the patch goes.

**Research:**

```text
Read tests/functional-run.md, data/commits.txt and package.json. Grade the output against these five properties and quote the line that proves each verdict:
P1 The heading carries the version from package.json.
P2 User-facing commits are grouped under separate headings for features and fixes.
P3 No chore, ci, docs, test or refactor commit appears.
P4 The breaking change (Node 16 no longer supported) has its own section that tells the reader what to do.
P5 Every customer-facing commit appears once and nothing is invented.
For each failed property, name the layer of the skill that owns it: description, workflow steps (what gets read), rules (what gets included), or output format (how it is laid out). Do not edit anything.
```

**Finding:** A good grade quotes a line for every verdict, or says "absent" for a property with no matching line. Typical owners: P1 belongs to the workflow steps, because the skill never reads `package.json`; P3 belongs to the rules, because nothing says which commits to leave out; P2 and P4 belong to the output format. A model grade is a judgement, so verify one verdict yourself: open `tests/functional-run.md` and look for the line Claude quoted. If Claude says P1 passed with a version in the heading, check that the version matches `package.json` and was not guessed.

**Recipe:**

```text
Create tests/functional-cases.md with a table of the columns Property, Verdict, Evidence, Owning layer, one line per property P1 to P5, using the grades from this conversation. Write nothing else.
```

**Expected Outcome:** `tests/functional-cases.md` holds five rows. At least P1, P3 and P4 are marked fail for the starter's skill. Only the failures recorded here are patched in the next step.

---

## Step 9: Patch the Layer That Owns Each Failure and Re-Run

**Overview:** Editing the wrong layer produces a change that feels productive and fixes nothing. Use the Owning layer column to decide where each edit goes, change nothing no property flagged, and run the same prompt again.

**Recipe:**

```text
Edit .claude/skills/release-notes/SKILL.md to close only the failed properties in tests/functional-cases.md.
- A failure owned by the workflow steps gets a new numbered step that reads the missing input.
- A failure owned by the rules gets one rule line that says what to leave out.
- A failure owned by the output format gets a description of the sections, in order.
Do not touch the description line. Keep the three-part structure of the file and keep it under 40 lines.
Then append a heading "Body" to tests/patches.md with one line per edit naming the property it closes.
```

Then run the same prompt as in Step 7, saving to a new file:

```bash
bash run-functional.sh "Write the release notes for this version from the commit list." tests/functional-run-after.md
```

```powershell
.\run-functional.ps1 -Prompt "Write the release notes for this version from the commit list." -Out tests\functional-run-after.md
```

Finally, back in the interactive session:

```text
Read tests/functional-run-after.md, data/commits.txt and package.json and grade the five properties P1 to P5 again, quoting the line that proves each verdict. Append the result to tests/functional-cases.md under a heading "After the patch", leaving the first table in place.
```

**Expected Outcome:** The skill file gained a step that reads `package.json`, a rule that leaves out internal commit types, and a layout with a features section, a fixes section and a breaking-change section. `tests/functional-run-after.md` shows a heading with `2.4.0`, two features, three fixes, and a breaking-change entry about Node 16 with an action for the reader; the exact wording varies. The second table in `tests/functional-cases.md` shows the earlier failures as pass. A property that still fails means the patch did not reach its layer: read the evidence line and edit again.

---

## Step 10: Package the Skill for Another Person

**Overview:** A skill becomes a product the moment someone else has to install it. The package is the skill folder and nothing else: the matrix, the fixtures and the run records are how you built confidence, and none of them belong in the archive. The install README sits one level up, because a README inside a skill folder only adds tokens to what Claude loads.

**Recipe:**

```text
Package the release-notes skill for another team.
1. Create dist/release-notes/ holding the patched SKILL.md and nothing else.
2. Check that SKILL.md contains no absolute path and no folder name from this lab (release-bench, labs, tests). List every replacement you made, or say there were none.
3. Write dist/README.md for a human who has never seen this repository: two sentences on what the skill produces, install steps for Claude Code (copy the folder to .claude/skills/ in the project, or to ~/.claude/skills/ for all projects) and for Claude.ai (zip the folder and upload it under Settings > Capabilities > Skills), the input the skill expects (data/commits.txt and package.json in the project), one worked example prompt, and the trigger results from tests/trigger-cases-after.md and tests/trigger-cases-holdout.md as pass counts. Quote only figures that exist in those files.
4. Build dist/release-notes.zip with whatever zip tool this machine has, run from inside dist/ so the archive is rooted at release-notes/. Print the list of archive entries.
```

**Expected Outcome:** `dist/` holds `release-notes/SKILL.md`, `README.md` and `release-notes.zip`. The printed entry list shows `release-notes/SKILL.md` and nothing else (a bare `release-notes/` directory entry may appear too), and no entry begins with `tests/`. The README opens on what a reader gets and ends with the results, each copied from a table you generated.

---

## Step 11: Install From the Archive and Prove It Fires

**Overview:** A package you have not installed is a package you have not tested. Unpack the archive into an empty folder outside the project, start a headless session there and look for the load. This catches a skill that only worked because it sat next to your fixtures.

**Recipe:**

```bash
SCRATCH="$(mktemp -d)"
mkdir -p "$SCRATCH/.claude/skills"
unzip dist/release-notes.zip -d "$SCRATCH/.claude/skills"
(cd "$SCRATCH" && claude -p "What should I tell our users about what shipped since the last release?" \
  --output-format stream-json --verbose --strict-mcp-config \
  --disallowedTools Edit Write NotebookEdit Bash PowerShell < /dev/null) | grep -c '"skill":"release-notes"'
rm -rf "$SCRATCH"
```

```powershell
$scratch = Join-Path ([IO.Path]::GetTempPath()) ([guid]::NewGuid())
New-Item -ItemType Directory "$scratch\.claude\skills" | Out-Null
Expand-Archive dist\release-notes.zip -DestinationPath "$scratch\.claude\skills"
Push-Location $scratch
$out = $null | claude -p "What should I tell our users about what shipped since the last release?" --output-format stream-json --verbose --strict-mcp-config --disallowedTools Edit Write NotebookEdit Bash PowerShell | Out-String
Pop-Location
([regex]::Matches($out, '"skill":"release-notes"')).Count
Remove-Item -Recurse -Force $scratch
```

**Expected Outcome:** The command prints a number of 1 or higher: the installed copy loaded in a folder that holds no `data/` and no tests. The session may then say it cannot find a commit list, which is correct, since only the loading is being checked. A 0 is one failed sample, so run the command once more before you conclude anything; two zeros in a row mean the archive layout is wrong, and the entry list from Step 10 shows why.

---

## Verify

List what the lab produced. Run this from `release-bench/`.

```bash
ls tests dist dist/release-notes
```

```powershell
Get-ChildItem tests, dist, dist\release-notes -Name
```

`tests/` holds `trigger-prompts.tsv`, `trigger-prompts-holdout.tsv`, `predictions.md`, `trigger-cases.md`, `trigger-cases-after.md`, `trigger-cases-holdout.md`, `patches.md`, `functional-run.md`, `functional-run-after.md` and `functional-cases.md`. `dist/` holds `README.md`, `release-notes.zip` and the `release-notes/` folder, and that folder holds `SKILL.md` and no other file.

Confirm the skill changed in exactly the places you patched:

```bash
git diff --stat -- .claude/skills/release-notes/SKILL.md
```

```powershell
git diff --stat -- .claude\skills\release-notes\SKILL.md
```

The diff reports one file changed, with the description line and the body steps altered and the frontmatter name untouched. To undo the lab, delete `tests/` and `dist/` and revert your edits to `SKILL.md`; the other starter files stay as they were.
