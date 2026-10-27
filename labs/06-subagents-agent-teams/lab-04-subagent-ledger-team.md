# Coordinate a team of subagents through a shared ledger

Two subagents that never see each other's conversation can still work as a team when they share one file. You build a tester that records every failing test as a row in `ledger.md` and a fixer that repairs the code from those rows alone, and you never pass a defect between them yourself. The tester then verifies each fix and closes its row.

What you practice here: give each subagent one job and one set of files, let a shared ledger carry the handoff, and check what crossed which context boundary.

Duration: about 50 minutes.

The teaching behind this lab is in [Unit-test your agent's performance](../../demos/06-subagents-agent-teams/03-testing-agent-performace/readme.md), whose shared ledger section this lab puts to work, and in [Orchestrate sub-agents with delegation, loops, and graphs](../../demos/06-subagents-agent-teams/04-orchestration/readme.md).

**What you need:** the .NET 10 SDK (`dotnet --version`), network access for the xUnit and EF Core packages, and Claude Code.

**What it costs:** three subagent runs on Sonnet, each of which reads the service once.

------

## Where to Open Claude Code

This lab builds its own agents, so open Claude Code inside your solution copy. Agents in `.claude/agents/` load from the folder the session was launched in, and a session opened at the repo root ignores the ones you write here. Step 0 creates the copy; run the second block once it exists, from the repo root.

```bash
cd labs/06-subagents-agent-teams/04-ledger-team/catalog-team-solution
claude
```

The same two commands work in PowerShell. Every path in the prompts below is relative to `catalog-team-solution`.

---

## Step 0: Create Your Solution Folder

**Goal:** Give the team a working copy so the checked-in starter stays pristine.

`catalog-team` holds one service, `catalog-service-cs`, with a defect in `DeleteFood` that no test covers yet. Run this once from the repo root, before you open Claude Code.

```bash
cp -r labs/06-subagents-agent-teams/04-ledger-team/catalog-team labs/06-subagents-agent-teams/04-ledger-team/catalog-team-solution
```

```powershell
Copy-Item -Recurse labs/06-subagents-agent-teams/04-ledger-team/catalog-team labs/06-subagents-agent-teams/04-ledger-team/catalog-team-solution
```

If the `-solution` folder already exists, both commands nest a second copy inside it. Delete the nested copy before you continue.

Confirm the service builds, from inside `catalog-team-solution`:

```bash
dotnet build catalog-service-cs
```

Expected result: `Build succeeded` with `0 Error(s)`.

---

## Step 1: Design the Ledger

**Goal:** Agree on one file both subagents read and write, so a defect can reach the fixer without you.

**Overview:** Each subagent starts with a clean context and returns only its final message to your session. A row in a shared file outlives that context, so the fixer can act on a defect it never saw found.

**Discover:**

```text
Two subagents will work on catalog-service-cs in this folder. One writes and runs xUnit
tests, the other fixes the service. They never see each other's conversation, and I will
not pass findings between them. Propose the columns of one Markdown table both of them
read and write, so the fixer can act on a row with no other input and the tester can
later confirm the fix. Say which agent may change which column. Do not create anything.
```

**What to look for:** a stable row ID, the failing test, the defect stated as observed and expected behavior, the file and member, and a status that moves from open to fixed to verified. Push back on a free-text notes column: a row the fixer has to interpret is a row it can misread. Each column should have exactly one writer.

The lab settles on this header, which Step 2 hands to the tester:

```markdown
| ID | Test | Defect | File | Status | Fixed by | Verified by |
|----|------|--------|------|--------|----------|-------------|
```

Do not create `ledger.md` from your session. Claude Code watches every file your session has read or written and shows it each later change, so a ledger your session created would carry every defect back to you and the handoff would run through you again. The tester creates it on its first run.

**Expected Outcome:** a proposed table and nothing on disk. Before: nowhere for a finding to live outside a conversation. After: one header with one writer per column.

---

## Step 2: Build the Tester and the Fixer

**Goal:** Create two subagents whose bodies split the files between them.

**Overview:** Both agents run `dotnet`, so their tool lists overlap and the split lives in each body: the tester owns the test project and adds rows, the fixer owns the service and marks rows fixed. Neither body names the other agent; the ledger is their only contract.

**Recipe:**

```text
Create two subagent files in .claude/agents/ of this folder.

1. catalog-tester.md. Frontmatter: name catalog-tester, a description saying it writes
   and runs xUnit tests for catalog-service-cs and records failing tests in ledger.md,
   model sonnet, tools Read, Write, Edit, Glob, Grep, Bash. Body:
   - Change only catalog-service-cs.Tests/ and ledger.md. Never edit catalog-service-cs/.
   - If ledger.md is missing, create it with the title "# Catalog defect ledger", the
     header | ID | Test | Defect | File | Status | Fixed by | Verified by | with its
     separator row, and this rule under the table: Status moves open, fixed, verified;
     catalog-tester adds rows and sets verified or open; catalog-fixer sets fixed and
     fills Fixed by; nobody deletes a row.
   - If catalog-service-cs.Tests/ is missing, create it with dotnet new xunit, reference
     ../catalog-service-cs/catalog-service.csproj, and use
     Microsoft.EntityFrameworkCore.InMemory at the EF Core version catalog-service.csproj uses.
   - Test mode: write the tests you are asked for, run dotnet test, and append one ledger
     row per failing test with the next ID (D1, D2, ...), status open, and the defect
     stated as observed versus expected behavior.
   - Verify mode: run dotnet test, set every fixed row whose test passes to verified with
     Verified by catalog-tester, and set a row whose test still fails back to open.
   - Return only JSON: { "mode", "testsPassed", "testsFailed", "rowsAdded": [ids],
     "rowsVerified": [ids], "rowsReopened": [ids] }. Put no defect text in it.

2. catalog-fixer.md. Frontmatter: name catalog-fixer, a description saying it fixes the
   open defects listed in ledger.md in catalog-service-cs, model sonnet, tools Read, Edit,
   Glob, Grep, Bash. Body:
   - Read ledger.md first and work only on rows with status open.
   - Change only files under catalog-service-cs/. Never edit catalog-service-cs.Tests/
     and never add or delete a row.
   - For each open row, fix the defect it states, run dotnet build on
     catalog-service-cs, then set Status to fixed and Fixed by to catalog-fixer.
   - Return only JSON: { "rowsFixed": [ids], "filesChanged": [paths], "build" }.
     Put no defect text in it.
```

Restart Claude Code with `/exit` then `claude` so the new agents load.

**Expected Outcome:** two files in `.claude/agents/`, and typing `@` in the prompt lists both `catalog-tester` and `catalog-fixer` in the typeahead. Before: one session that would do everything itself. After: two specialists that share only a file.

---

## Step 3: Round 1, the Tester Finds the Defects

**Goal:** Turn the service's behavior into ledger rows.

**Overview:** The tester sees its body and your one prompt. Everything it learns about the service ends up in two places: tests on disk and rows in the ledger.

**Recipe:**

```text
Use the catalog-tester subagent in test mode. Task: write xUnit tests for every public
method of catalog-service-cs/Controllers/FoodController.cs, one happy path and one edge
case each, run dotnet test, and record every failing test in ledger.md.
Show me its JSON unedited.
```

**Expected Outcome:** JSON with `"mode": "test"`, `testsFailed` of at least 1, and `rowsAdded` listing the new IDs. The tester created `ledger.md`, and it holds at least one open row; one of them names `DeleteFood`: it calls `GetById(id)` without `await`, so `item` is a `Task` and `ctx.Remove(item)` throws. Your row count may differ; the `DeleteFood` row is the one every run finds. Confirm the controller is untouched:

```bash
git diff --no-index --stat -- ../catalog-team/catalog-service-cs/Controllers catalog-service-cs/Controllers
```

Expected result: no output, because the tester wrote only tests and rows.

---

## Step 4: Round 2, the Fixer Works From the Ledger Alone

**Goal:** Fix every open row without telling the fixer what is wrong.

**Overview:** This is the handoff the ledger exists for. Your prompt names no defect, so everything the fixer knows about the bug comes from the row the tester wrote.

**Recipe:**

```text
Use the catalog-fixer subagent. Give it exactly this task and add nothing about the
defects yourself: fix the open rows in ledger.md. Show me its JSON unedited.
```

**Expected Outcome:** JSON whose `rowsFixed` lists every open ID, whose `filesChanged` stays inside `catalog-service-cs/`, and whose `build` reports success. In `ledger.md` those rows now read `fixed` with `catalog-fixer` in Fixed by. Run the diff again:

```bash
git diff --no-index --stat -- ../catalog-team/catalog-service-cs/Controllers catalog-service-cs/Controllers
```

Expected result: `FoodController.cs` with a few changed lines.

---

## Step 5: Round 3, the Tester Verifies Every Row

**Goal:** Close the loop with the agent that found the defects.

**Overview:** The fixer's `fixed` is a claim. The tester reruns the same tests and is the only agent allowed to write `verified`.

**Recipe:**

```text
Use the catalog-tester subagent in verify mode: run dotnet test and update every fixed
row in ledger.md. Show me its JSON unedited.
```

**Expected Outcome:** JSON with `"mode": "verify"`, `testsFailed` of 0, and `rowsVerified` listing every ID. Every row in `ledger.md` reads `verified`. A row set back to `open` goes to the fixer again with the Step 4 prompt, then back here.

---

## Step 6: Check What Crossed Which Boundary

**Goal:** Prove that the ledger carried the defect from one subagent to the other, and your session did not.

**Overview:** Both agents returned IDs and counts, never defect text. If your main session can explain the defect without reading the ledger, the handoff leaked through you.

**Discover:**

```text
Without opening ledger.md or any other file, tell me what defect D1 was and how it was
fixed. Then say where in this conversation you learned each part of your answer.
```

**What to look for:** an answer that cites only the IDs and counts in the agents' JSON and says it cannot name the defect. Push back if it describes the `DeleteFood` defect: ask which message contained that text. A notice that `ledger.md` changed on disk means your session read or wrote the ledger earlier, and the run has to start again from Step 0.

Then confirm the result yourself, in a terminal, so your Claude Code session never reads the ledger:

```bash
dotnet test catalog-service-cs.Tests
cat ledger.md
```

**Expected Outcome:** `Passed!` with `Failed: 0`, and a ledger in which every row names the test that found it, the agent that fixed it and the agent that verified it.

You now hold two subagents that share nothing but `ledger.md`, a test project, a fixed `DeleteFood`, and a record of the whole handoff. The finished reference is the `catalog-team-solution` folder.
