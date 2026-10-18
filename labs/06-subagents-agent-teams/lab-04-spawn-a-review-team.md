# Spawn a review team and steer it

Put three independent reviewers on one unreviewed service, watch them coordinate through a shared task list instead of through you, and end with a single ranked findings file that no one reviewer could have written alone.

Each step follows the same pattern:

- **Goal** - what this step achieves
- **Discover** - an open conversation prompt to reason through design decisions
- **What to look for** - what to read and evaluate before moving on
- **Recipe** - a complete implementation prompt you can use as-is or adapt from your own findings

**What you need:** Python 3.10 or newer on PATH, and Claude Code 2.1.178 or newer. Agent teams are experimental, so `claude --version` below that is the one prerequisite that stops this lab.

**What it costs:** three teammates are three separate Claude instances, so this lab bills roughly three times a single-session review of the same code. That is the trade the lab is teaching you to judge.

## Where to Open Claude Code

Open Claude Code inside your solution copy, so the team reviews that tree and writes its findings there. This lab writes nothing into the project's `.claude/`: the one setting it needs is the agent-teams flag, and that lives in your global harness at `~/.claude/settings.json`.

The solution copy is the tree the team works in, not the checked-in starter: Step 0 below scaffolds it; start the session there once it exists. Run this from the repo root; both commands work unchanged in PowerShell.

```bash
cd labs/06-subagents-agent-teams/04-review/notes-api-py-solution
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `notes-api-py-solution` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere in the repo:

```text
In labs/06-subagents-agent-teams/04-review/notes-api-py-solution spawn three teammates named security, perf and tests ....
```

That works for any step whose result is just files, such as the merged `review-findings.md` in Step 6. It does not work for the team itself: teammates inherit the lead's working directory, so a session opened at the repo root puts three reviewers on the whole course repository and writes the findings file at the root. The agent-teams flag is the one piece that is immune, because it lives in your global `~/.claude/settings.json` rather than in the project. Launch inside the solution copy from Step 1 onward.

Restart the session with `/exit` then `claude` after editing that file, because settings are read at startup.

Launching inside the solution copy is what makes the repository a monorepo to this lab rather than the project: the repo's own `/CLAUDE.md`, `/.claude/` and `/.mcp.json` stay out of the session, and you read them from the repo root without ever writing into them. Every path in the prompts below is relative to the lab folder.

---

## Step 0: Create Your Solution Folder

**Goal:** Give the team a working copy so the checked-in starter stays pristine.

`notes-api-py` is a starter: no build output, no installed packages, nothing generated. The team you are about to spawn writes a findings file and, in Step 5, one source edit. Run the copy from a shell at the repository root, before you open Claude Code.

```bash
cp -r labs/06-subagents-agent-teams/04-review/notes-api-py labs/06-subagents-agent-teams/04-review/notes-api-py-solution
```

```powershell
Copy-Item -Recurse labs/06-subagents-agent-teams/04-review/notes-api-py labs/06-subagents-agent-teams/04-review/notes-api-py-solution
```

Run the copy once. If the `-solution` folder already exists, both commands nest a second copy inside it instead of overwriting, and the team then reviews the wrong tree.

Confirm the service runs before anyone reviews it:

```bash
python notes_api.py
```

Stop it with Ctrl+C. A review of code nobody has run is a review of your reading, not of the service.

---

## Step 1: Turn Agent Teams On

**Goal:** Enable the experimental flag in your global harness, and prove it took effect.

Agent teams are off by default. With the flag unset, Claude will neither spawn teammates nor propose them, and the failure is silent: you get sub-agents and a plausible answer.

**Recipe:**

Add the `env` block to `~/.claude/settings.json` (on Windows `$HOME\.claude\settings.json`), keeping everything already in the file, then restart the session with `/exit` and `claude`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**What to look for:** the check that proves it is on disk, not on screen. With the flag live, `~/.claude/teams/` gets a `session-XXXXXXXX` folder at session start, before any teammate exists, holding a `config.json` whose `members` array is just the lead. If that folder is missing, the flag did not take effect and everything below will run as sub-agents.

---

## Step 2: Spawn Three Named Reviewers

**Goal:** Get three teammates with disjoint lenses, named so you can address them later.

**Discover:**

```text
Read notes_api.py, store.py and config.py in this folder.

I want three independent reviewers on this service, each with a lens the other
two are not responsible for. Propose the three lenses, and for each one name the
specific files and functions that lens should own. Tell me where two lenses would
overlap and how you would split the overlap so no two reviewers report the same
finding.
```

**What to look for:** the split should be by concern, not by file, because all three reviewers need `store.py`. A good answer puts the token in `config.py` and the `/notes/{name}` path handling under security, `search()` and the per-request file reads under performance, and the total absence of tests under coverage. Push back if a lens is described as "general code quality": a lens that owns everything owns nothing, and two such reviewers produce one report twice.

**Recipe:**

```text
Spawn three agent team teammates, not sub-agents, named security, perf and tests.

- security: review config.py and the request handling in notes_api.py for secret
  handling, input validation and path traversal. Prove each finding by naming the
  exact call path from request to filesystem.
- perf: review store.py and the search endpoint. Quantify the cost of one search
  request in terms of file reads and comparisons as the note count grows.
- tests: review the whole folder for test coverage. List what a first test file
  would have to cover to catch the other two reviewers' findings.

Each teammate reports findings with a severity, a file and a line. Have them
message each other where their findings touch the same code path.
```

**What to look for:** three rows in the agent panel below the prompt input, one per name. Sub-agents appear in the same panel, so the panel alone does not prove a team formed: check `~/.claude/teams/` from Step 1. If you got sub-agents, ask again and say "agent team" explicitly.

> A row that vanishes has not stopped. Idle rows hide 30 seconds after every agent in the panel has gone idle, and come back on that teammate's next turn.

---

## Step 3: Read the Shared Task List

**Goal:** See the coordination surface that makes this a team rather than three parallel workers.

**Recipe:**

Press Ctrl+T to toggle the task list while the reviewers work.

**What to look for:** tasks move through pending, in progress and completed, and each in-progress task shows which teammate claimed it. Claiming is protected by file locking, so two teammates never hold the same task. If a task sits pending while every teammate is idle, it has an unresolved dependency or nobody claimed it, and the lead needs telling.

Ask the lead for the state in words when the panel is hard to read:

```text
List every task, its state, and which teammate owns it.
```

---

## Step 4: Redirect One Reviewer Mid-Flight

**Goal:** Use the surface sub-agents do not have: instructing one worker directly, without restarting anything.

**Recipe:**

Select `perf` in the agent panel with the up and down arrows, press Enter to open its transcript, and send it this:

```text
Also measure the cost of the write path, not just search. A note write reopens
and rewrites the whole file. Report it with the same units you used for search.
```

**What to look for:** the message lands in that teammate's own session and it continues from where it was, rather than starting over. While you are viewing a teammate, plain text goes to that teammate but built-in slash commands still run in the lead's session, which is why `/model` typed here changes the lead and not the teammate you are reading.

---

## Step 5: Gate the One Fix Behind Plan Approval

**Goal:** Let a teammate change code without letting it change code unreviewed.

**Discover:**

```text
Of everything the three reviewers found, which single fix would you make first,
and what is the argument for it over the other candidates? Name what could break
if the fix is wrong.
```

**What to look for:** the answer should rank on exploitability and blast radius, not on how easy the fix is. The path traversal in `/notes/{name}` reads any file the process can reach, which the search endpoint then makes greppable; that ranks above the hardcoded token, which is bad but bounded to writes.

**Recipe:**

```text
Spawn a fix teammate named patcher to close the highest-severity finding.
Require plan approval before it makes any changes. Only approve a plan that
names the exact function it changes and states how the fix is verified.
```

**What to look for:** the teammate works read-only until its plan reaches you, and a rejected plan sends it back into plan mode with your feedback rather than ending it. The lead approves autonomously, so criteria that are not in your prompt are not applied.

---

## Step 6: Merge Three Reviews Into One File

**Goal:** Produce the deliverable, which is a ranked list, not three appended reports.

**Recipe:**

```text
Wait for all teammates to finish, then write review-findings.md in this folder:

- One table of every finding: severity, lens, file, line, one-sentence description.
- Ranked by severity, then by blast radius.
- A "contested" section for any finding two reviewers disagreed on, with both
  positions and which one you accepted.
- A closing line naming which finding patcher fixed and how it was verified.

Do not include a finding no reviewer actually reported.
```

**What to look for:** the contested section is the part that proves the team worked as a team. If it is empty, either the lenses did not overlap at all or the reviewers never messaged each other, and the run was three sub-agents wearing teammate names.

---

## Step 7: Close the Team Down

**Goal:** End the run deliberately and know what survives it.

**Recipe:**

```text
Ask the patcher teammate to shut down.
```

**What to look for:** the lead sends a shutdown request and the teammate can approve it, exiting, or reject it with a reason. Shutdown is not instant, because a teammate finishes its current tool call first.

The team's shared directories are removed when the session ends, so there is no cleanup command to run. The task list under `~/.claude/tasks/` persists locally so a resumed session keeps its tasks, and it ages out under the same `cleanupPeriodDays` as your session transcripts.

You now have `review-findings.md` in your solution folder: one ranked list, produced by three reviewers who argued with each other, and one fix that could not land until you approved the plan behind it.
