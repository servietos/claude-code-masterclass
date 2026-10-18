---
presents: demo-competing-hypotheses.md
budget: 4 min
beats: 4
---

# Present: Find a root cause by making five agents argue

A confirmed theory and an unchallenged one look identical in a transcript, and only one of them is worth acting on. Four beats: the flag that decides whether you get a team at all, the five-way split, the concession that proves they talked, and the control experiment that closes it.

------

## Beats

### Beat 1: Without the flag you get sub-agents and never know (1 min)

**Open:** [Step 1: Decide What the Hypotheses Are](demo-competing-hypotheses.md#step-1-decide-what-the-hypotheses-are)
**Say:** Teams are experimental and off by default, and the flag lives in the global harness at `~/.claude/settings.json`, not in the project. With it missing, the same prompt spawns sub-agents that cannot message each other, and you still get a confident answer, which is the expensive failure.

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

**Result:** the check is on disk, not on screen, and it is what tells a team from five sub-agents

```text
~/.claude/teams/session-0581d643/config.json
  "leadAgentId": "team-lead@session-0581d643"
  members[0].agentType = "team-lead"
```

**Gotcha:** the agent panel shows sub-agents and teammates in the same rows, so the panel never proves a team formed.

### Beat 2: Five theories, one per teammate (1 min)

**Open:** [Step 1: Decide What the Hypotheses Are](demo-competing-hypotheses.md#step-1-decide-what-the-hypotheses-are)
**Say:** The split has to span layers, not restate one suspicion five ways. Config, predicate, stdin, transcript, commands: each one can produce the symptom on its own, which is what makes a refutation mean something.

```text
Spawn 5 agent team teammates, not sub-agents, one hypothesis each, named
config, predicate, stdin, transcript and commands.
Each teammate defends its own hypothesis and tries to falsify it with a control
experiment run outside this folder, changing one variable at a time.
Have them message each other by name to attack each other's theories.
```

**Result:** six members in one team, the lead plus five named teammates

```text
session-0581d643
  team-lead  | team-lead       | in-process
  config     | general-purpose | in-process
  predicate  | general-purpose | in-process
  stdin      | general-purpose | in-process
  transcript | general-purpose | in-process
  commands   | general-purpose | in-process
```

**Gotcha:** name them in the prompt, or later instructions have nothing to address and you cannot redirect one without restarting the run.

### Beat 3: The concession is the proof they talked (1 min)

**Open:** [Step 2: Demand the Control Experiment](demo-competing-hypotheses.md#step-2-demand-the-control-experiment)
**Say:** This line is the whole module in one sentence. A teammate did not merely fail to prove its own theory, it accepted another teammate's evidence, and a sub-agent structurally cannot do that because it never sees another worker's work.

```text
Message from predicate (ctrl+o to expand)
```

**Result:** the lead reports it without polling anyone

```text
predicate conceded to config's explanation with a single-variable proof.
Waiting on stdin, transcript, and commands.
```

**Gotcha:** messages arrive automatically, so a quiet lead means the teammates are still working, not that delivery failed.

### Beat 4: One variable, two runs, done (1 min)

**Open:** [Step 3: Write the Consensus Down](demo-competing-hypotheses.md#step-3-write-the-consensus-down) · [`findings.md`](session-loop-py-solution/findings.md)
**Say:** `config.json` writes `maxTurns`, `config.py` reads `max_turns`, and `.get` with a default turns the miss into a silent fallback to 1. The rejections are what make that worth acting on.

```text
Single-variable control, renaming only the JSON key to max_turns:
```

**Result:** the same code, one key renamed, and the loop runs to `/quit`

```text
you> echo: hello
you> echo: second message
you> closing session
session ended after 4 turns
```

**Gotcha:** the team also files a secondary observation nobody asked for, that `turns` counts user and assistant rows separately, so a correct `maxTurns` of 20 buys 10 exchanges. Name it as a second bug and move on, or the room relitigates the first one.

## If the room asks

| Question | Answer |
|---|---|
| Could sub-agents have found this? | The cause, probably. The refutations, no: each rejection here came from a teammate testing another teammate's claim, and sub-agents never see each other's evidence. |
| What does it cost against one session? | Roughly five times, because each teammate is a separate Claude instance with its own context window. That is why review and investigation are the first teams to build, not routine work. |
| Why not have them fix it too? | Five teammates editing one file overwrite each other. Split so no two own the same file, or gate the edit behind plan approval and let one teammate make it. |
