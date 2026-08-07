# Make teammates argue, and gate what they ship

One agent investigating a bug finds a plausible explanation and stops. That is not laziness, it is anchoring: once a theory is on the table, every later step is read as evidence for or against that theory rather than as evidence for the alternatives nobody proposed. Sequential investigation cannot escape this, because there is nothing in the loop that wants a different answer.

A team can. Give five teammates one hypothesis each and tell them to disprove each other, and the theory that survives has been attacked rather than merely confirmed. This topic covers that pattern and the three controls that keep it safe: plan approval before a teammate edits anything, hooks that refuse bad work, and the permission boundary between agents.

## Debate as an Investigation Technique

The mechanism is the instruction to argue, not the number of teammates. A prompt that only assigns hypotheses produces five parallel monologues; a prompt that tells them to challenge each other produces a debate whose survivor is worth acting on.

```text
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific debate.
Update the findings doc with whatever consensus emerges.
```

Two details make this work. Each teammate must be able to reach the others by name, which is what the mailbox provides and what sub-agents cannot do. And the output must be a single shared artifact, so the run ends in a consensus rather than in five reports you have to reconcile yourself.

The same shape applies to review. Assign each teammate a distinct lens, security, performance, test coverage, and a single reviewer's tendency to gravitate toward one class of issue stops being a problem, because no reviewer is responsible for the other two lenses.

## Plan Approval Before a Teammate Edits

For anything risky, require the teammate to plan first. It works read-only in plan mode until the lead approves the approach.

```text
Spawn an architect teammate to refactor the authentication module.
Require plan approval before they make any changes.
```

When the teammate finishes planning it sends a plan approval request to the lead. The lead approves it, or rejects it with feedback, in which case the teammate stays in plan mode, revises, and resubmits. Approval happens once and then the teammate exits plan mode and implements.

The lead decides autonomously, which means the criteria have to be in your prompt if you want them applied.

```text
Only approve plans that include test coverage. Reject any plan that changes the
database schema.
```

## Quality Gates With Team Hooks

Three hook events fire on team activity, and each one blocks on exit code 2 with the stderr text delivered back as feedback.

| Hook | Fires when | Exit code 2 |
|---|---|---|
| `TeammateIdle` | A teammate is about to go idle | Prevents the teammate from going idle, so it keeps working |
| `TaskCreated` | A task is being created | Rolls the task creation back |
| `TaskCompleted` | A task is being marked complete | Prevents the completion |

```json
{
  "hooks": {
    "TaskCompleted": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/require-findings.sh\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

`TeammateIdle` is the one that changes team behaviour most, because it converts "I am done" into a claim the harness can refuse. A teammate that stops before the findings file exists gets told so and carries on, without you noticing the stop and typing the correction yourself.

The `team_name` field in these hook payloads carries the session-derived team name and is deprecated, so do not build a gate that depends on it.

## Reusing a Sub-Agent Definition as a Teammate Role

A teammate can be spawned from any sub-agent definition you already have, at project, user, plugin, or CLI scope. One role, defined once, usable as both a delegated sub-agent and a team member.

```text
Spawn a teammate using the playwright-expert agent type to verify the two pages
we changed at desktop and mobile widths.
```

What carries over is narrower than the file suggests:

- The definition's `tools` allowlist and `model` apply.
- The definition's body is appended to the teammate's system prompt as extra instructions, rather than replacing it.
- `skills` and `mcpServers` from the frontmatter are not applied. A teammate loads skills and MCP servers from your project and user settings, like any regular session.
- `SendMessage` and the task management tools are always available, even when `tools` restricts everything else. A teammate you cannot message is not a teammate.

## The Permission Boundary Between Agents

Teammates start with the lead's permission settings, including `--dangerously-skip-permissions` if the lead was launched with it. Teammate permission prompts surface in the lead session, and you answer them there.

The boundary that matters is between an agent and you. When one agent messages another with `SendMessage`, the receiving agent is told the message came from another Claude session, not from you. A teammate cannot approve a permission prompt on your behalf, and a teammate that was denied an action cannot get a second teammate to do it instead. In auto mode the classifier treats a relayed approval claim as untrusted input rather than as your consent.

Plan approval is the designed exception: the lead grants teammate plan approvals without prompting you separately, which is why the approval criteria belong in the prompt.

## Sizing a Team and What It Costs

Token usage scales linearly with active teammates, because each one is a separate context window. Coordination overhead scales too, and past a point extra teammates stop buying speed.

- Start with three to five teammates. Three focused ones routinely beat five scattered ones.
- Aim for five to six tasks per teammate. Fifteen independent tasks is a three-teammate job.
- Size a task as a self-contained unit with a clear deliverable: a function, a test file, a review. Too small and coordination costs more than the work; too large and the teammate runs a long way before anyone can correct it.
- Split the work so no two teammates own the same file. Parallel edits to one file overwrite each other, which is why review and research are the safest first teams.

## Shutting a Teammate Down

Ask by name. The lead sends a shutdown request, and the teammate can approve it and exit, or reject it with an explanation.

```text
Ask the researcher teammate to shut down.
```

The team's shared directories are cleaned up when the session ends, so there is no separate cleanup step. If a teammate stops on an error instead of recovering, open its transcript from the panel and either give it new instructions or spawn a replacement.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/update-config` | Wire the `TaskCompleted` or `TeammateIdle` gate into `settings.json` |
| `/permissions` | Pre-approve routine operations so teammate prompts stop landing in the lead |
| `/agents` | Find where sub-agent definitions live, so you can name one as a teammate role |
| `/cost` | Read what the run actually billed, which is the number that decides your next team size |

## Key Topics covered in this module

- [Require plan approval for teammates](https://code.claude.com/docs/en/agent-teams#require-plan-approval-for-teammates): the read-only-until-approved flow and how the lead judges a plan
- [Claude Code Hooks](https://code.claude.com/docs/en/hooks): the configuration shape, exit codes, and the full event list including the three team events
- [Use subagent definitions for teammates](https://code.claude.com/docs/en/agent-teams#use-subagent-definitions-for-teammates): what a definition carries into a teammate and what it does not
- [Agent team token costs](https://code.claude.com/docs/en/costs#agent-team-token-costs): what team runs bill against a single session
