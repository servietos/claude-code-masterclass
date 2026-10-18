# Find a root cause by making five agents argue

One agent investigating a bug finds a plausible cause and stops looking, and you cannot tell a confirmed theory from an unchallenged one. Here five teammates each defend a different theory and try to break each other's, so the explanation you keep has survived four attempts to kill it.

------

Work in `session-loop-py/` (stdlib only, nothing to install); the finished result is beside it in [`session-loop-py-solution/`](session-loop-py-solution), holding the team's `findings.md`.

## Step 1: Decide What the Hypotheses Are

Teams are off by default: add `"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"` under `env` in `~/.claude/settings.json`, or Claude silently spawns sub-agents, which cannot argue with each other.

Assigning five teammates the same suspicion buys nothing, so the split has to cover genuinely different layers before anyone is spawned.

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

Five rows appear in the agent panel, and the team config under `~/.claude/teams/` now lists all six members. Each theory can produce the symptom on its own, which is what makes a refutation mean something.

## Step 2: Demand the Control Experiment

The value of the run is in the traffic between teammates, and a theory that explains the symptom has not yet been tested. Leave the session in the foreground, press Ctrl+T to toggle the shared task list, and insist each teammate changes exactly one variable and reports both runs:

```text
Before anyone writes a conclusion: every teammate must produce a control
experiment for its own hypothesis. Copy the project somewhere outside this
folder, change exactly one thing there, and report the run before and the run
after. A hypothesis with no control experiment is rejected by default.
```

Messages from teammates arrive without the lead polling for them:

```text
Message from predicate (ctrl+o to expand)
predicate conceded to config's explanation with a single-variable proof.
Waiting on stdin, transcript, and commands.
```

A concession is the signal to look for: `predicate` accepted another teammate's proof, which a sub-agent cannot do because it never sees another worker's evidence. The controls run in a scratch copy, so `git status` in this folder stays clean.

## Step 3: Write the Consensus Down

The deliverable is one file that records what survived and what killed everything else, because the rejections are what make the survivor worth acting on.

```text
When a consensus emerges, write findings.md in this folder with:
- The surviving explanation, with file and line references.
- The evidence, including the loaded settings, the failing run, and the
  single-variable control that fixes it.
- A table with one row per rejected hypothesis saying exactly what disproved it.
- Anything the team noticed that is not the reported bug, in its own section.
```

[`findings.md`](session-loop-py-solution/findings.md) names the key-name mismatch as the survivor, with the control run beside the failing one:

```text
Single-variable control, renaming only the JSON key to max_turns:
you> echo: hello
you> echo: second message
you> closing session
session ended after 4 turns
```

The failing run as shipped ends after 2 turns; the same code with one key renamed runs to `/quit`, and every rejected theory gets its own refutation row.
