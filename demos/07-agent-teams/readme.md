# Coordinate a team of Claude Code sessions

- When a team beats sub-agents
- Four parts: lead, teammates, tasks, mailbox
- Enabling teams and session state
- Spawning teammates and choosing models
- Display modes and the agent panel
- Task states, dependencies, and claiming
- Direct and teammate-to-teammate messaging
- Competing hypotheses between teammates
- Plan approval and team hook gates
- Team sizing, conflicts, and cost

## Topics

| Topic | Description |
|-------|-------------|
| [01: Introduction](01-introduction/readme.md) | The lead, teammates, shared task list and mailbox; how a team differs from sub-agents in communication and cost; enabling the experimental flag; the team config, inbox and task paths on disk; the limits that decide whether a team is the right tool. |
| [02: Parallel Review](02-parallel-review/readme.md) | Spawning teammates by name, writing a spawn prompt that survives the missing conversation history, choosing models, the agent panel and its keys, task states and dependencies, and steering a teammate by messaging it directly. |
| [03: Debate and Control](03-debate-and-control/readme.md) | Competing hypotheses as an escape from anchoring, plan approval before a teammate edits, the three team hook events and their exit-code-2 gates, sub-agent definitions reused as teammate roles, the permission boundary between agents, and sizing against cost. |

## Demos

| Topic | Description |
|-------|-------------|
| [02: Parallel Review](02-parallel-review/demo-parallel-review-team.md) | Three named reviewers take one lens each on the `catalog-service-cs` API, claim tasks off the shared list, and the lead merges their findings into one ranked report. |
| [03: Debate and Control](03-debate-and-control/demo-competing-hypotheses.md) | Five teammates hold one root-cause theory each for a chat loop that exits after a single exchange, argue each other down by name, and write the surviving explanation to a consensus file. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Starter and Solution Folders

Topic 02 works in `02-parallel-review/catalog-service-cs`, topic 03 in `03-debate-and-control/session-loop-py`. Both starters run without a team, and neither carries a `.claude/` folder: the agent-teams flag is a global harness setting in `~/.claude/settings.json`. The finished result including the team's output file sits beside each starter in its `-solution` folder.

## Labs

| Lab | Description |
|-----|-------------|
| [Spawn a Review Team and Steer It](../../labs/07-agent-teams/lab-01-spawn-a-review-team.md) | Spawn three named reviewers on one unreviewed service, watch them claim tasks off the shared list, redirect one by message, and gate the fix behind plan approval. |

## Knowledge Check

### CQ-01: Sub-Agents or a Team

A refactor has to move a shared type, update every call site, and keep the test suite green. The three pieces are strictly ordered. Which shape fits?

- A) An agent team of three, one per piece, so the work runs in parallel.
- B) A single session or sub-agents, because the pieces depend on each other and touch the same files.
- C) An agent team of two, with the third piece done by the lead while it waits.
- D) An agent team with plan approval on every teammate, to serialize them safely.

**Answer: B**

Teams pay coordination overhead and a separate context window per teammate in exchange for independent work and cross-talk. A strict dependency chain has no independence to buy, and same-file edits from parallel teammates overwrite each other. Option D notices the risk and then pays for a team anyway to undo the parallelism that was the only reason to spawn one.

### CQ-02: The Teammate That Ignored the Obvious

A lead spawns a security reviewer with the prompt "Review the auth module." The teammate reports generic findings and misses the JWT-in-cookie design the team spent the last hour discussing. What is the cause?

- A) The teammate's model was too small for security work.
- B) The teammate needs `inherit_context` enabled so it can read the lead's window.
- C) The lead's conversation history does not carry over, so anything the teammate needs has to be in the spawn prompt.
- D) The teammate should have messaged the lead to ask for background.

**Answer: C**

A teammate loads the project the way any session does, including `CLAUDE.md`, MCP servers and skills, but it does not inherit the lead's conversation. The hour of discussion exists only in the lead's window, so the spawn prompt is the only channel for it. Option D is not wrong as a habit, but a teammate cannot ask about context it does not know exists.

### CQ-03: The Panel Went Quiet

Three teammates were working. Two rows vanish from the agent panel and the third is still going. What happened?

- A) The two teammates crashed, and their transcripts are gone with them.
- B) The two teammates finished and were shut down automatically.
- C) The rows hid after the panel went idle; the teammates are still running and still addressable.
- D) The lead reassigned their tasks and despawned them to save tokens.

**Answer: C**

Idle rows hide 30 seconds after every agent in the panel has gone idle, and reappear on that teammate's next turn. The teammate keeps running and stays addressable by name while hidden, and messaging it brings the row back. Reading a hidden row as a dead teammate is what leads people to spawn duplicates.

### CQ-04: Approval Relayed Through a Teammate

A teammate is denied a destructive command. It messages another teammate saying the user approved the action and asks it to run the command instead. What happens?

- A) The second teammate runs it, because permissions are per teammate and it was not denied.
- B) The second teammate treats the claim as untrusted input, because a message from another agent is not your consent.
- C) The command runs but is logged for later review by the lead.
- D) The team halts, because a denied action cannot be retried in the same session.

**Answer: B**

A receiving agent is told the message came from another Claude session rather than from you. A teammate cannot approve a permission prompt on your behalf, and in auto mode the classifier treats a relayed approval claim as untrusted input. This is the boundary that makes a team safe to run with more members than you can watch.

### CQ-05: The Teammate That Stops Too Early

Teammates keep marking their review task complete without writing the findings file the run exists to produce. What is the mechanism that fixes this without you watching every teammate?

- A) Lower the teammates' effort so they take fewer shortcuts.
- B) A `TaskCompleted` hook that exits 2 when the findings file is missing, sending the reason back as feedback.
- C) Reduce the team to one teammate so the lead can supervise it.
- D) Re-prompt each teammate after every task with the same instruction.

**Answer: B**

Exit code 2 on `TaskCompleted` prevents the completion and delivers the stderr text as feedback, which turns "I am done" into a claim the harness can refuse. `TeammateIdle` does the same for a teammate about to go idle. Option D works and costs a round-trip every time, which is exactly what a gate replaces.
