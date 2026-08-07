# Build Agents That Loop Until a Verifiable Goal Is Met

Most headless agent runs are single-pass: one prompt, one result, one exit. Goal-driven agents are different. They loop across turns until a measurable condition is satisfied, then exit cleanly. The goal pattern encodes the success condition into the prompt itself so every turn is evaluated against it. When the condition fails, the agent continues; when it passes, the agent stops.

## The Goal Pattern

A goal condition must be verifiable, not just desirable. "Fix the bug" is not a goal condition because the agent cannot test whether it is satisfied. "npm test exits 0 with no skipped tests and no test files modified outside src/" is a goal condition because it resolves to a binary outcome. The model checks its own work against the condition at the end of each turn. When the check passes, the session ends with a clean exit.

The secondary evaluator variant is stronger. Instead of letting the executing model judge its own output, a separate evaluation step (another Claude invocation or a deterministic script) checks the condition independently. This prevents the executing model from convincing itself that a failing condition has passed. Separation of concerns between execution and evaluation is the same principle that makes test-driven development reliable: the entity that writes the code is not the entity that grades it.

## Permission Modes and Turn Controls

Unmonitored loops need the per-tool confirmation prompt out of the way. Two flags do that: `--allowed-tools` pre-approves a narrow tool set (`"Read,Edit,Bash(npm:*)"`), and `--permission-mode acceptEdits` lets the agent apply file edits without asking. Combined with `--max-turns`, they create a bounded autonomous loop: the agent runs without interruption until the goal is met or the turn ceiling is hit.

Turn limits are not optional for goal-driven agents. A goal condition that is never satisfied because of an environment issue (missing dependency, wrong working directory, a test that always fails for an unrelated reason) will loop until the turn limit is reached. Budget accordingly: if each turn costs $0.10 and the limit is 15 turns, the worst case is $1.50 per run. Set the limit based on task complexity, not on optimism about the goal condition always being reachable.

## Helpful Claude Code CLI Commands

| Command | Usage |
|---|---|
| `claude -p "<goal condition>" --max-turns 15` | Run a goal-driven headless agent with a hard turn ceiling. |
| `claude -p "..." --permission-mode acceptEdits --allowed-tools "Read,Edit,Bash(npm:*)"` | Remove tool confirmation for a narrow, pre-approved tool set. |
| `claude -p "..." --output-format json \| jq '{result, turns: .num_turns, cost: .total_cost_usd}'` | Extract the result summary, turn count, and run cost from the JSON envelope. |
| `claude -p "..." --output-format json \| ConvertFrom-Json \| Select-Object result, num_turns, total_cost_usd` | The same three fields in PowerShell, with no `jq` needed on the machine. |

## Key Topics Covered in This Module

- [Claude CLI reference](https://code.claude.com/docs/en/cli-reference): `--max-turns`, `--permission-mode`, `--allowed-tools`, and `--output-format`
- [Headless mode](https://code.claude.com/docs/en/headless): running `claude -p` unmonitored and parsing the JSON envelope
