# Converge a review loop with a stopping rule

A fix that one agent writes and one agent checks ships whatever both of them happened to notice, and a reviewer told to find problems never runs out of them. You end with a hardened write path, a read-only reviewer, a ledger of every finding and its verdict, and a rule that decides when the loop stops. The optional extension moves the same split into a script where the merge and the vote are plain code.

What you practice here: separate the agent that writes from the agent that judges, triage every finding against the project's real configuration, and stop the loop on a rule you fixed in advance.

Duration: about 90 minutes.

The teaching behind this lab is in [Orchestrate sub-agents with delegation, loops, and graphs](../../demos/06-subagents-agent-teams/04-orchestration/readme.md), and the same loop and graph are shown in [Converge a Fix Through Review Rounds](../../demos/06-subagents-agent-teams/04-orchestration/demo-review-loop.md) and [Run the Same Split as a Workflow Graph](../../demos/06-subagents-agent-teams/04-orchestration/demo-workflow-graph.md).

**What you need:** the .NET 10 SDK (`dotnet --version`) and Claude Code. The optional extension also needs the Workflow tool in your Claude Code build; if `/workflows` is not a command in your session, stop after Step 7.

**What it costs:** every review round is a fresh sub-agent that reads the service again. The loop is capped at two review rounds after the first fix to keep that bounded.

------

## Where to Open Claude Code

This lab builds its own agents, so open Claude Code inside your solution copy. Agents in `.claude/agents/` load from the folder the session was launched in, and a session opened at the repo root ignores the ones you write here. Step 0 creates the copy; run the second block once it exists, from the repo root.

```bash
cd labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-solution
claude
```

The same two commands work in PowerShell. Every path in the prompts below is relative to `catalog-service-cs-solution`.

---

## Step 0: Create Your Solution Folder

**Goal:** Give the loop a working copy so the checked-in starter stays pristine.

`catalog-service-cs` is the starter: the write path of `FoodController` accepts anything and answers 200 to most of it. Every agent edit, build output and database write lands in the copy. Run this once from the repo root, before you open Claude Code.

```bash
cp -r labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-solution
```

```powershell
Copy-Item -Recurse labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-solution
```

If the `-solution` folder already exists, both commands nest a second copy inside it. Delete the nested copy before you continue.

Confirm the service builds before any agent touches it:

```bash
dotnet build
```

Expected result: `Build succeeded` with `0 Error(s)`. A loop that starts from a broken build reports the old breakage as its own findings.

---

## Step 1: Fix the Contract Before Any Agent Starts

**Goal:** Pin the status codes in one file that the implementer builds against and the reviewer tries to disprove.

**Overview:** If the implementer and the reviewer each infer what "correct" means, the review measures their disagreement about the code. One contract file is the claim under test for every round.

**Discover:**

```text
Read Controllers/FoodController.cs, Domain/CatalogItem.cs and test-controllers.http in this folder.

For each of POST /food, PUT /food, DELETE /food/{id} and GET /food/{id}, tell me what
the endpoint returns today for a missing ID and for an invalid CatalogItem. List every
status code decision a client could not predict from the current code, and propose the
smallest set of rules that settles them. Do not edit anything.
```

**What to look for:** a per-endpoint list that includes the quiet defects beside the missing validation. Check that it notices `DeleteFood` calls `GetById(id)` without `await`, so `item` is a `Task` and never null. Push back if it proposes new endpoints, new fields or an error-handling middleware: the contract covers four existing routes.

**Recipe:**

Create `contract.md` in `catalog-service-cs-solution` with this content:

```markdown
# Catalog write-path contract

| Request | Condition | Response |
|---------|-----------|----------|
| POST /food | CatalogItem invalid | 400 with a ProblemDetails body |
| POST /food | CatalogItem valid | 201 with a Location header |
| PUT /food | CatalogItem invalid | 400 with a ProblemDetails body |
| PUT /food | ID does not exist | 404 |
| PUT /food | otherwise | 200 |
| DELETE /food/{id} | ID does not exist | 404 |
| DELETE /food/{id} | otherwise | 204 |
| GET /food/{id} | ID does not exist | 404 |

Invalid means Name is null, empty or whitespace, Price is negative, or InStock is negative.

GET /food stays untouched. The implementer owns Controllers/ and Shared/ and changes nothing else.
```

**Expected Outcome:** one new file, `contract.md`, with eight rows and no code. Before: four routes whose answers depend on who reads the controller. After: one table both agents will quote.

---

## Step 2: Build the Writer and the Read-Only Reviewer

**Goal:** Create two sub-agents whose tool lists enforce the split between writing and judging.

**Overview:** A reviewer that can edit will quietly repair what it finds and the round leaves no record. The reviewer's tool list is the control, so it contains no Edit, no Write and no Bash.

**Recipe:**

```text
Create two sub-agent files in .claude/agents/ of this project.

1. write-path-implementer.md. Frontmatter: name write-path-implementer, a description
   saying it implements an agreed API contract in a .NET controller, model sonnet,
   tools Read, Write, Edit, Bash, Glob, Grep. Body: read contract.md first, change only
   the files the contract says it owns, run dotnet build before reporting, and return
   the changed files and the build result.

2. contract-reviewer.md. Frontmatter: name contract-reviewer, a description saying it
   is a read-only reviewer that tries to disprove a stated contract, model sonnet,
   tools Read, Grep, Glob and nothing else. Body: treat the contract as a claim to
   REFUTE, report when uncertain, ignore style, and return only JSON in this shape:
   { "findings": [ { "id", "file", "symbol", "claim", "severity" } ], "dry": true | false, "summary" }
   where id is a stable kebab-case name built from the symbol and the defect, and dry
   is true only when no finding is new.
```

Restart with `/exit` then `claude`, then run `/agents`.

**Expected Outcome:** both names appear under project agents. Open `contract-reviewer` and read its tools line: `Read, Grep, Glob`. Before: no reviewer that is unable to fix. After: a reviewer that can only report.

---

## Step 3: Round 1, Implement the Contract

**Goal:** Let the writer harden the write path against `contract.md`, and nothing else.

**Overview:** The loop needs a first draft to attack. The writer gets the contract and a file boundary so the review has a bounded surface.

**Recipe:**

```text
Round 1. Use the write-path-implementer sub-agent in this folder only.
Implement every row of contract.md in Controllers/FoodController.cs, with any shared
validation in Shared/. Keep GET /food untouched. Run dotnet build and confirm zero errors.
Return the changed files and the build result.
```

**Expected Outcome:** the sub-agent reports its changed files, all inside `Controllers/` and `Shared/`, and a build with `0 Error(s)`. `test-controllers.http` is unchanged, which means nothing in the repo exercises the new branches yet. That gap is what Round 2 is likely to find.

---

## Step 4: Round 2, Review With No Write Tools

**Goal:** Collect a JSON record of everything the reviewer can prove wrong.

**Overview:** The reviewer gets the same contract as the claim and the files that decide the outcome. Because it has no write tools, every finding survives as a record you triage.

**Recipe:**

```text
Round 2. Use the contract-reviewer sub-agent. Give it contract.md as the claim under
test and let it read Controllers/FoodController.cs, Domain/CatalogItem.cs,
Infrastructure/FoodDBContext.cs and test-controllers.http. Tell it to refute the claim,
default to reporting when uncertain, and ignore style. Show me the JSON it returns
unedited.
```

**Expected Outcome:** a JSON object with a `findings` array, each entry carrying `id`, `file`, `symbol`, `claim` and `severity`, plus `dry` set to `false` and a `summary`. No file changed during this round, because the reviewer holds no write tool. The reference run in the demo returned 12 findings against the one changed file, ranging from a real partial-update overwrite to a claim about a service that is in fact registered. Expect a mix of real and false findings.

---

## Step 5: Triage Against the Project's Real Configuration

**Goal:** Sort every finding into accept, reject or defer, and write the verdicts into a ledger the later rounds read.

**Overview:** An under-briefed reviewer inflates a round with findings the project's own configuration already answers. Triage is the coordinator's job, and it is what lets the loop converge.

**Discover:**

```text
Here are the findings from the review round. For each one, check it against the project
by reading catalog-service.csproj, Common/AppBuilder.cs and
appsettings.json before deciding. Sort them into accept, reject and defer. For every
reject, name the file that settles it. Do not fix anything yet.
```

**What to look for:** each reject cites a file and a line, for example a nullable-annotation finding settled by a csproj that does not enable `Nullable`, or an unregistered-service finding settled by `AddSingleton<AILogger>()` in `AppBuilder.cs`. Push back on any accept that rests on the reviewer's confidence alone and ask which file supports it. A reject without a named file goes back to defer.

**Recipe:**

```text
Write review-ledger.json in this folder with three keys:
  "facts": the project facts you verified while triaging, one string each, each naming
    its source file (for example whether Nullable is enabled, whether TreatWarningsAsErrors
    is set, which database is used, what is registered in AppBuilder.cs);
  "seen": an object keyed by finding id, one entry per id from Round 2, each with "verdict"
    (accept, reject or defer) and "reason" naming the file that settles it;
  "rounds": [ { "round": 2, "findings": <count>, "dry": false } ].
Use the finding ids exactly as the reviewer returned them. Do not fix anything.
```

**Expected Outcome:** `review-ledger.json` exists with a `seen` entry for every finding id and a `facts` list. Before: a pile of claims. After: each claim carries a verdict and the file that decided it. The demo run turned 12 findings into five accepted, six rejected and one deferred; yours will differ in count.

---

## Step 6: Fix, Review Again, and Stop on the Rule

**Goal:** Apply only the accepted findings, run one more review round with the seen list, and stop when the rule says so.

**Overview:** A fix creates surface the first reviewer never saw, so the second review round is the one that pays. The stopping rule is what ends the loop: stop when a round comes back dry, or after this second review round either way.

**Recipe:**

```text
Round 3. Use the write-path-implementer sub-agent to fix exactly the findings marked
accept in review-ledger.json and nothing else. Pass it every string in the ledger's
"facts" so it does not re-litigate them. Run dotnet build and confirm zero errors.

Round 4. Use the contract-reviewer sub-agent again with the same contract.md claim.
Pass it every id in the ledger's "seen" list, accepted and rejected alike, and tell it
to report only findings that are new and differ in substance from every seen one. It returns the
same JSON shape. Then update review-ledger.json: append the new findings to "seen"
with a verdict and a reason, and append { "round": 4, "findings": <count>, "dry": <value> }
to "rounds". Stop after this round whether or not it is dry.
```

**Expected Outcome:** the build shows `0 Error(s)`, the ledger has a round 4 entry, and the loop has stopped. Two outcomes are valid: `"dry": true` with an empty `findings` array, or `"dry": false` with a few new findings. In the reference run round 4 returned three new findings, two of them created by round 3's own fix, and the loop stopped on the cap. Dedupe against everything seen, because a rejected finding left off the list comes back every round and the loop never converges.

---

## Step 7: Prove the Contract Against the Running Service

**Goal:** Confirm the status codes with real requests.

**Overview:** A dry review round says the reviewer ran out of arguments. Requests against the running service say whether the contract holds.

Start the service in a second terminal, in `catalog-service-cs-solution`:

```bash
dotnet run
```

It listens on `http://localhost:5000`. In the first terminal, send the probes.

```bash
B=http://localhost:5000
curl -s -o /dev/null -w "POST invalid    %{http_code}\n" -X POST $B/food -H "Content-Type: application/json" -d '{"name":"","price":-1,"inStock":-1}'
curl -s -o /dev/null -w "POST valid      %{http_code}\n" -X POST $B/food -H "Content-Type: application/json" -d '{"name":"Probe","price":5,"inStock":1}'
curl -s -o /dev/null -w "PUT invalid     %{http_code}\n" -X PUT $B/food -H "Content-Type: application/json" -d '{"id":1,"name":"","price":1,"inStock":1}'
curl -s -o /dev/null -w "PUT missing     %{http_code}\n" -X PUT $B/food -H "Content-Type: application/json" -d '{"id":999,"name":"Ghost","price":1,"inStock":1}'
curl -s -o /dev/null -w "PUT valid       %{http_code}\n" -X PUT $B/food -H "Content-Type: application/json" -d '{"id":1,"name":"Hand pulled Noodles","price":17,"inStock":9}'
curl -s -o /dev/null -w "DELETE missing  %{http_code}\n" -X DELETE $B/food/999
curl -s -o /dev/null -w "DELETE existing %{http_code}\n" -X DELETE $B/food/5
curl -s -o /dev/null -w "GET missing     %{http_code}\n" $B/food/999
```

```powershell
$b = "http://localhost:5000"
function Probe($label, $method, $path, $body) {
    $r = Invoke-WebRequest -SkipHttpErrorCheck -Method $method -Uri "$b$path" -ContentType "application/json" -Body $body
    "{0,-16} {1}" -f $label, [int]$r.StatusCode
}
Probe "POST invalid" Post "/food" '{"name":"","price":-1,"inStock":-1}'
Probe "POST valid" Post "/food" '{"name":"Probe","price":5,"inStock":1}'
Probe "PUT invalid" Put "/food" '{"id":1,"name":"","price":1,"inStock":1}'
Probe "PUT missing" Put "/food" '{"id":999,"name":"Ghost","price":1,"inStock":1}'
Probe "PUT valid" Put "/food" '{"id":1,"name":"Hand pulled Noodles","price":17,"inStock":9}'
Probe "DELETE missing" Delete "/food/999" $null
Probe "DELETE existing" Delete "/food/5" $null
Probe "GET missing" Get "/food/999" $null
```

**Expected Outcome:** eight lines, in this order: `400`, `201`, `400`, `404`, `200`, `404`, `204`, `404`. The second run of `DELETE existing` prints `404` because ID 5 is gone, which is the contract working. Any other code is a defect the reviewer missed: add its id to `review-ledger.json` with verdict accept and the request that proved it. Stop the service with Ctrl+C in the second terminal.

You now hold a hardened write path, `contract.md`, two agents, and `review-ledger.json` showing every finding, its verdict and why the loop stopped. The core lab ends here; the extension below is optional.

---

## Step 8: Extension, Map the Edges Before Writing the Graph

**Goal:** Decide which dependencies between the work units carry data, so the script fans out only where nothing has to wait.

**Overview:** Every edge you delete is work that can run at the same time. Start from a fresh copy so the graph hardens the same unhardened starter the loop did, and the two results compare.

Run this once from the repo root, copy the agents and the contract across, then open Claude Code in the new folder:

```bash
cp -r labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-graph-solution
cp -r labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-solution/.claude labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-graph-solution/.claude
cp labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-solution/contract.md labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-graph-solution/contract.md
cd labs/06-subagents-agent-teams/05-converge-review-loop/catalog-service-cs-graph-solution
claude
```

```powershell
$lab = "labs/06-subagents-agent-teams/05-converge-review-loop"
Copy-Item -Recurse "$lab/catalog-service-cs" "$lab/catalog-service-cs-graph-solution"
Copy-Item -Recurse "$lab/catalog-service-cs-solution/.claude" "$lab/catalog-service-cs-graph-solution/.claude"
Copy-Item "$lab/catalog-service-cs-solution/contract.md" "$lab/catalog-service-cs-graph-solution/contract.md"
Set-Location "$lab/catalog-service-cs-graph-solution"
claude
```

**Discover:**

```text
Two units of work harden the write path of this API, against contract.md:
  A  implements the contract in Controllers/ and Shared/
  B  appends one request per status code to test-controllers.http
A third unit checks that the merged result is correct.
Model this as a directed graph. For each pair, say whether an edge exists and name the
specific data that crosses it. Where the only reason is "this has to happen after that",
mark it as ordering. Then list every step above that is plain code and takes no
agent. Do not edit anything.
```

**What to look for:** two data edges, both into verification, and no edge between A and B. Push back if it draws A to B because the requests need endpoints first: ask what data would cross it, since B only needs the contract. The plain-code list should include the merge of the changed-file lists and the vote count.

**Expected Outcome:** a graph with A and B side by side and one verification node downstream of both, plus a code-only list. Nothing on disk changed.

---

## Step 9: Extension, Write the Graph as a Script

**Goal:** Turn the map into a workflow whose fan-out, merge and vote are code.

**Overview:** The decomposition is identical on every run because it is a script, and the harness forces each node through a structured-output tool and retries on a schema mismatch.

**Recipe:**

```text
Write and run a workflow for hardening the write path of this API against contract.md.
Structure:
  - meta with name, description and two phases: Implement and Verify
  - a shared schema requiring status, filesChanged (array of strings) and summary
  - parallel() over two nodes in Implement, both returning that schema:
      node 1, agentType write-path-implementer, owns Controllers/ and Shared/
      node 2 owns test-controllers.http only, appends one request per status code in
      contract.md, and must not open Controllers/FoodController.cs
  - merge the filesChanged arrays in the script body
  - three Verify nodes over the lenses correctness, security and reproduction, each
    prompted to REFUTE the claim that contract.md is correctly implemented and to
    default to refuted when uncertain, each returning { lens, refuted, why, evidence }
  - the feature passes only if at least two of three fail to refute; count that in
    the script body and log every dissenting lens
Filter out null results before merging, since a failed node resolves to null.
```

**Expected Outcome:** `/workflows` shows two node boxes running together under Implement, then three under Verify. The vote is arithmetic in the script body, along the lines of:

```javascript
const survived = verdicts.filter(v => !v.refuted).length
const passes = survived >= 2
verdicts.filter(v => v.refuted).forEach(v => log(`dissent (${v.lens}): ${v.why}`))
```

---

## Step 10: Extension, Read the Split Vote

**Goal:** Read a verdict that three lenses can disagree on, and trace each dissent to the node that could have prevented it.

**Overview:** A single verifier produces a single opinion, and a confident wrong one passes straight through. Three lenses disagree in public, and the dissent is the part worth reading.

**Recipe:**

```text
Report the workflow's verdict field by field:
  - the vote, as survived over total
  - for each lens: refuted true or false, its why, and its evidence line
  - for each dissent, which of the two implement nodes could have caught it on its own,
    given that node 1 never opened test-controllers.http and node 2 never opened
    FoodController.cs
Do not fix anything yet.
```

**Expected Outcome:** a vote such as `2/3` or `3/3` with one line per lens. A defect that only exists in the merged result, such as a request in `test-controllers.http` that depends on a record an earlier request deleted, is invisible to both implement nodes and is exactly what the verify edge exists to catch. Compare this verdict with `review-ledger.json`: the loop found its defects round by round and the graph counted them in one pass.

The finished reference for the core lab is the `catalog-service-cs-solution` folder you built, and for the extension `catalog-service-cs-graph-solution`.
