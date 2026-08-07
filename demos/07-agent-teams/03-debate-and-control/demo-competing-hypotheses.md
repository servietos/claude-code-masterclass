# Find a root cause by making five agents argue

One agent investigating a bug finds a plausible cause and stops looking, and you cannot tell a confirmed theory from an unchallenged one. Here five teammates each defend a different theory and try to break each other's, so the explanation you keep has survived four attempts to kill it. What you hold at the end is a `findings.md` with a single-variable control experiment behind the survivor and a named refutation for every rejected theory.

------

## Running the Starter

```bash
cd demos/07-agent-teams/03-debate-and-control/session-loop-py
printf 'hello\nsecond message\n/quit\n' | python session_loop.py
```

```powershell
cd demos/07-agent-teams/03-debate-and-control/session-loop-py
"hello`nsecond message`n/quit" | python session_loop.py
```

```text
session started, /quit to end
you> echo: hello
session ended after 2 turns
```

Three lines went in and one exchange came out, although `config.json` sets `maxTurns` to 20. Nothing is installed for this demo; the app is stdlib only.

---

## Step 1: Turn Agent Teams On

**Overview:** Teams are experimental and off by default, and the failure mode is silent: without the flag Claude spawns sub-agents, which cannot argue with each other, and the run still produces a confident answer.

**Recipe:**

Add the flag to your global harness at `~/.claude/settings.json` (on Windows `$HOME\.claude\settings.json`), keeping whatever else is already in the file:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

Then start Claude Code in the starter:

```bash
claude
```

**Expected Outcome:** a team directory appears under `~/.claude/teams/` (on Windows `$HOME\.claude\teams`) at session start, before any teammate exists, named `session-` plus the first eight characters of the session id. Its `config.json` starts with the lead alone:

```json
{
  "name": "session-0581d643",
  "leadAgentId": "team-lead@session-0581d643",
  "members": [
    { "agentId": "team-lead@session-0581d643", "name": "team-lead",
      "agentType": "team-lead", "backendType": "in-process" }
  ]
}
```

If that directory never appears, the flag did not take effect and everything below will run as sub-agents.

---

## Step 2: Decide What the Hypotheses Are

**Overview:** The team is only as good as the spread of theories it holds. Assigning five teammates the same suspicion buys nothing, so the split has to cover genuinely different layers before anyone is spawned.

**Research:**

```text
Read session_loop.py, session.py, config.py, config.json, commands.py and
transcript.py in this folder.

The loop ends after one exchange although config.json sets maxTurns to 20.
List every distinct layer that could independently produce that symptom, one
line each, with the specific file and function that would carry the fault.
Do not tell me which one is at fault yet.
```

**Finding:** you want a list that spans layers rather than five variations of one idea: configuration loading, the loop predicate, standard input reaching EOF, the transcript writer, and the command handler. Push back on any entry that cannot produce the symptom on its own, and on an answer that jumps to a diagnosis, because a hypothesis nobody defends does not get tested.

**Recipe:**

```text
Spawn 5 agent team teammates, not sub-agents, one hypothesis each, named
config, predicate, stdin, transcript and commands.

- config: the settings never reach the Session
- predicate: Session.is_open is wrong
- stdin: input() hits EOF early
- transcript: the transcript writer interferes with the loop
- commands: the command handler ends the session

Each teammate defends its own hypothesis and tries to falsify it with a control
experiment run outside this folder, changing one variable at a time. Have them
message each other by name to attack each other's theories, like a scientific
debate. Do not change any source file in this folder.
```

**Expected Outcome:** five rows in the agent panel, and the team config now lists all six members:

```text
session-0581d643
  team-lead  | team-lead       | in-process
  config     | general-purpose | in-process
  predicate  | general-purpose | in-process
  stdin      | general-purpose | in-process
  transcript | general-purpose | in-process
  commands   | general-purpose | in-process
```

---

## Step 3: Watch the Debate, Not the Answers

**Overview:** The value of the run is in the traffic between teammates. A team that never messages is five sub-agents wearing names, and you can see the difference on screen while it happens.

**Recipe:**

Leave the session in the foreground and read the lead's incoming messages. Press Ctrl+T to toggle the shared task list.

**Expected Outcome:** the lead reports each teammate as it lands, and messages from teammates arrive without the lead polling for them:

```text
Five teammates are running the debate. Waiting for their verdicts.
Teammate @config finished
Message from predicate (ctrl+o to expand)
predicate conceded to config's explanation with a single-variable proof.
Waiting on stdin, transcript, and commands.
Message from stdin (ctrl+o to expand)
Three in. Waiting on transcript and commands.
```

A concession is the signal to look for. `predicate` did not merely fail to prove its own theory, it accepted another teammate's proof, which is the thing a sub-agent cannot do because it never sees another worker's evidence.

---

## Step 4: Demand the Control Experiment

**Overview:** A theory that explains the symptom is not the same as a theory that has been tested. The cheap way to tell them apart is to insist each teammate changes exactly one variable and reports both runs.

**Recipe:**

```text
Before anyone writes a conclusion: every teammate must produce a control
experiment for its own hypothesis. Copy the project somewhere outside this
folder, change exactly one thing there, and report the run before and the run
after. A hypothesis with no control experiment is rejected by default.
```

**Expected Outcome:** the teammates run their controls in a scratch copy, so `git status` in this folder stays clean. `predicate` reports that fixing only `is_open` still ends the run after two turns; `stdin` reports that `yes hello | python session_loop.py`, where standard input never ends, still stops after two turns; `transcript` reports that a no-op writer reproduces the bug byte for byte.

---

## Step 5: Write the Consensus Down

**Overview:** The deliverable is one file that records what survived and what killed everything else, because the rejections are what make the survivor worth acting on.

**Recipe:**

```text
When a consensus emerges, write findings.md in this folder with:

- The surviving explanation, with file and line references.
- The evidence, including the loaded settings, the failing run, and the
  single-variable control that fixes it.
- A table with one row per rejected hypothesis saying exactly what disproved it.
- Anything the team noticed that is not the reported bug, in its own section.
```

**Expected Outcome:** [`findings.md`](session-loop-py-solution/findings.md) names the key-name mismatch as the survivor, with the control run beside the failing one:

```text
Failing run as shipped:
session started, /quit to end
you> echo: hello
session ended after 2 turns

Single-variable control, renaming only the JSON key to max_turns:
you> echo: hello
you> echo: second message
you> closing session
session ended after 4 turns
```

and one refutation per rejected theory:

```text
| predicate  | Fixing only is_open and leaving config.py as shipped still gives
               session ended after 2 turns.                                    |
| stdin      | yes hello | python session_loop.py, where stdin never ends,
               still stops after 2 turns.                                      |
| commands   | In the failing run /quit is never reached: commands.handle is
               called once, with hello, and session.closed stays False.        |
```

The team also filed a secondary observation nobody asked for: `turns` counts user and assistant rows separately, so a correctly loaded `maxTurns` of 20 buys 10 exchanges, not 20.

---

## Step 6: Close the Team

**Overview:** Teammates keep running until they are told to stop, and knowing what survives the session is what stops you looking for a cleanup command that does not exist.

**Recipe:**

```text
Ask the transcript teammate to shut down.
```

**Expected Outcome:** the lead sends a shutdown request, and the teammate approves it and exits, or rejects it with a reason. Shutdown waits for the teammate's current tool call to finish, so it is not instant. When the session ends, `~/.claude/teams/session-XXXXXXXX/` is removed, while the task list under `~/.claude/tasks/` stays and ages out with your session transcripts.

The finished result is beside the starter in [`session-loop-py-solution/`](session-loop-py-solution/), holding the team's `findings.md`.
