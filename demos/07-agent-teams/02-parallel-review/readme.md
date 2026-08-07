# Spawn a team and steer it while it works

Spawning a team is a sentence, not a configuration file. You describe the work and the roles you want, and the lead creates the tasks, spawns the teammates, and starts synthesizing as results arrive. What decides whether the run is useful is how much of the job you put in the spawn prompt, because a teammate inherits your project but not your conversation.

Steering matters just as much. A team left alone for twenty minutes can produce twenty minutes of the wrong work, so the panel, the task list, and direct messages are the three surfaces you use to keep it pointed at the goal.

## Spawning: You Ask, or Claude Proposes

There are two paths to a team. You describe a task and explicitly ask for teammates, or Claude decides the task would benefit from parallel work and suggests spawning them. In both cases nothing spawns without your approval.

```text
I want a review of the catalog API before we ship it. Spawn three teammates:
one on security, one on performance, one on test coverage. Have each review
the code and report findings.
```

Claude sometimes answers a request like this with sub-agents instead of a team. Sub-agents and teammates share the same agent panel, so seeing rows appear does not confirm a team formed. If you got sub-agents, ask again and say "agent team" explicitly.

The strongest cases are the ones where roles do not wait on each other: review from independent angles, research across separate sources, a new feature where each teammate owns different files, or a bug where competing theories can be tested at the same time.

## Writing a Spawn Prompt a Teammate Can Act On

A teammate starts a fresh session. It loads the project the same way any session does, including `CLAUDE.md`, MCP servers, and skills, and it receives the spawn prompt from the lead. What it does not get is the lead's conversation history, which is where most of the context you think is obvious actually lives.

```text
Spawn a security reviewer teammate with the prompt: "Review the controllers in
Controllers/ for input validation and injection risk. The API is ASP.NET Core
with EF Core against SQLite, and every route is anonymous today. Report each
finding with a severity and the file and line it sits on."
```

Naming is worth doing deliberately. The lead assigns every teammate a name at spawn, and every later instruction you write refers to that name, so telling the lead what to call them is what makes "ask the security reviewer to also check the config endpoint" resolve to the right session.

## Choosing Models

Teammates do not inherit the lead's `/model` selection. The default comes from Default teammate model in `/config`, which can be set to Default (leader's model) if you want them to follow the lead. You can also decide per spawn.

```text
Spawn 4 teammates to review these modules in parallel. Use Sonnet for each teammate.
```

Effort level is the exception: teammates inherit the lead's effort level. A teammate's model and fast mode are fixed at spawn, so `/model` and `/fast` typed later only change the lead, while `/effort` still reaches the teammate you are viewing.

## Display Modes and the Agent Panel

In-process is the default and it works in any terminal: every teammate runs inside your main terminal and appears as a row in the agent panel below the prompt. Split-pane mode gives each teammate its own pane but requires tmux or iTerm2 with the `it2` CLI, and it is not supported in the VS Code integrated terminal, Windows Terminal, or Ghostty. On Windows that makes in-process the practical choice.

```json
{
  "teammateMode": "auto"
}
```

`teammateMode` lives in `~/.claude/settings.json` and takes `in-process`, `auto`, `tmux`, or `iterm2`. For a single session, pass `claude --teammate-mode auto` instead; the flag is experimental and does not appear in `claude --help`.

| Key | Effect in the agent panel |
|---|---|
| Up and down | Select a teammate |
| Enter | Open the selected teammate's transcript and message it directly |
| Escape | Interrupt the selected teammate's current turn |
| `x` | Stop the selected teammate |
| Ctrl+T | Toggle the shared task list |

A row that disappears has not stopped. Idle rows hide 30 seconds after every agent in the panel has gone idle and come back on that teammate's next turn, and when more than three teammates are idle the surplus collapses into a single `N idle agents` row that Enter expands.

## The Shared Task List

The task list is what turns three parallel sessions into a team. Tasks have three states, pending, in progress, and completed, and a task can declare dependencies on other tasks. A pending task whose dependencies are unresolved cannot be claimed, and completing the blocker unblocks it automatically.

Work reaches a teammate in one of two ways. The lead assigns a task explicitly, or a teammate that has just finished picks up the next unassigned, unblocked task by itself. Claiming is protected by file locking, so two teammates reaching for the same task at the same time do not both get it.

```text
Assign the config endpoint review to the security reviewer, and let the other two
self-claim from the list when they finish what they are on.
```

## Talking to a Teammate Directly

Every teammate is a full Claude Code session, so you can message it to add instructions, ask a question, or redirect it. Select it in the panel, press Enter, and type. While you are viewing a teammate, plain text and skills go to that teammate, but built-in slash commands still run in the lead's session.

Messages between agents are delivered automatically, so the lead does not poll for updates, and a teammate that finishes notifies the lead on its own. Teammate messaging is one recipient at a time: to reach everyone, send one message per teammate.

One failure mode is worth recognizing early. If the lead starts implementing tasks itself instead of waiting, say so directly.

```text
Wait for your teammates to complete their tasks before proceeding.
```

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/model` | Changes the lead only; a teammate's model is fixed when it spawns |
| `/effort` | Change effort for the teammate you are currently viewing, unlike `/model` and `/fast` |
| `/context` | Check what the lead is holding before writing the next spawn prompt |
| `/cost` | Read what the parallel teammates actually billed against a single session |

## Key Topics covered in this module

- [Control your agent team](https://code.claude.com/docs/en/agent-teams#control-your-agent-team): display modes, specifying teammates and models, assigning and claiming tasks
- [Interactive mode task list](https://code.claude.com/docs/en/interactive-mode#task-list): the shared list the panel toggles with Ctrl+T
- [Claude Code Settings](https://code.claude.com/docs/en/settings): the `teammateMode` setting and the rest of the settings hierarchy
- [Adjust effort level](https://code.claude.com/docs/en/model-config#adjust-effort-level): the one session setting teammates inherit from the lead
