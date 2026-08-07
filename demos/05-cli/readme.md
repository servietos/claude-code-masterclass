# Automate Claude Code from the Command Line

Claude Code is not only an interactive assistant. Run with `-p`, it becomes a programmable agent that exits with a shell code, writes structured JSON, and runs unmonitored inside CI pipelines, cron jobs, and orchestration scripts. This module covers the harness mechanics, tool scoping, parallel isolation, and long-running goal patterns that make headless agents reliable in production.

- Agent harness: tools, knowledge, action interfaces
- Agent loop: perceive, reason, act, dispatch
- Headless mode: print, CI exit codes
- Git worktrees for parallel agent lanes
- On-demand skill and context injection
- Background tasks and async delegation
- Hooks in CI: policy gate enforcement
- GitHub Actions: scripting agentic workflows

## Topics

| Topic | Description |
|-------|-------------|
| [01: Introduction](01-intro/readme.md) | The agent harness mental model: tools, knowledge, and action interfaces; headless mode with structured JSON output and CI exit codes; and least-privilege tool scoping for unmonitored scripts. |
| [03: CI Gates](03-ci-gate/readme.md) | Wiring Claude into a CI workflow using sentinel tokens to produce deterministic exit codes that approve or block builds based on AI code-audit judgments. |
| [04: Parallel Worktrees and Policy Hooks](04-parallel-hooks/readme.md) | Driving worktrees from a script (create them, commit inside each from a headless agent, merge back and clean up), showing that a PreToolUse gate lives in the checkout and therefore covers every lane, and scaling the two-worktree script into a task-queue orchestrator with per-agent exit codes. |
| [05: Always-On and Goal Patterns](05-always-on/readme.md) | Long-running autonomous agents that loop until a measurable end-state condition is met, with the goal condition stated in the prompt and the run bounded by `--max-turns`. |

## Demos

| Topic | Description |
|-------|-------------|
| [01: Introduction](01-intro/demo-headless-tool-scope.md) | Run `claude -p` for the first time, read the JSON envelope it returns, and prove that `--allowed-tools` grants permission while only `--tools` produces a read-only run. |
| [03: CI Gates](03-ci-gate/demo-ci-gates.md) | Wire Claude headless into a CI pipeline using sentinel tokens, confirm deterministic exit codes, and block a build on a failing audit. |
| [04: Parallel Worktrees and Policy Hooks](04-parallel-hooks/demo-parallel-hooks.md) | Prove the shipped `rm -rf` policy gate with one piped payload, then spawn two isolated agents in separate Git worktrees and see the same gate block the command in each lane. |
| [04: Parallel Worktrees and Policy Hooks](04-parallel-hooks/demo-worktree-orchestration.md) | Design a task-queue script that drives the full worktree lifecycle (create, dispatch, merge, clean up) for a list of tasks. |
| [05: Always-On and Goal Patterns](05-always-on/demo-always-on.md) | Set a measurable end-state condition, launch an autonomous agent with `claude -p --max-turns`, and watch it loop until the condition validates or the turn limit is reached. |

Every demo has a presenter guide beside it (`demo-presenter-<slug>.md`) holding the same
teaching in timed beats, for delivery without running the demo live.

## Starter and Solution Folders

Work in each topic's starter (for example `goal-demo/`); the finished, runnable result is beside it in `<starter>-solution/`.

## Bash and PowerShell

Every script in this module ships twice, as `<name>.sh` and `<name>.ps1`, and the demo guides give each prompt and run command in both forms. Pick one shell per demo and stay with it: the two scripts create the same worktrees and branches, so running both back to back finds the names already taken.

The `claude` flags never change between the shells. What changes is the shell's own machinery, and those differences are the only places the guides print two blocks.

| Bash | PowerShell |
|---|---|
| `cmd &` then `wait` | `Start-Job` then `Receive-Job -Wait -AutoRemoveJob` |
| `wait "$pid"` then `$?` | `$LASTEXITCODE` emitted as the job's last statement |
| `echo "$OUT" \| grep -q TOKEN` | `$Out -cmatch 'TOKEN'` (plain `-match` is case-insensitive) |
| `jq -r '.tool_input.command'` | `ConvertFrom-Json` (built in, nothing to install) |
| `IFS` plus `read -r slug desc` to split a delimited line | `-split` with the escaped delimiter and a limit of 2 |
| `bash -n script.sh` | `[System.Management.Automation.Language.Parser]::ParseFile(...)` |
| `chmod +x script.sh` | Not applicable; use `pwsh -File script.ps1` if the execution policy blocks it |

## Labs

| Lab | Description |
|-----|-------------|
| [Drive Claude Code Headlessly and Run Parallel Work in Git Worktrees](../../labs/05-cli/lab-01-headless-and-worktrees.md) | Run `claude -p` from bash scripts with meaningful exit codes, work in parallel across git worktrees, and inject skills on demand. |
| [Gate Tools with PreToolUse Hooks and Review Pull Requests in CI](../../labs/05-cli/lab-02-hooks-actions-and-cli-comparison.md) | Build a `PreToolUse` policy gate, review PRs from a GitHub Actions workflow, then compare the same task on Codex CLI and Aider. |
| [Keep Agents Working While You Are Away From the Keyboard](../../labs/05-cli/lab-03-always-on-and-fleet.md) | Persistent sessions, an OS scheduler, the Ralph Wiggum loop, scheduled GitHub Actions, and a parallel-worktree fleet with `xargs -P`. |

## Knowledge Check

### CQ-01: Failing the Build on a Finding

A CI job runs Claude Code to review a diff and must fail the build when a critical finding appears. What makes the result reliably machine-readable?

- A) Append "Return ONLY valid JSON" to the prompt and parse the output with `jq`.
- B) Run with `--output-format json` and `--json-schema` so the CLI enforces a known structure.
- C) Pipe the output through `sed` to strip markdown code fences before parsing.
- D) Parse the human-readable output with a regular expression matching the word "critical".

**Answer: B**

The flags move the guarantee from the prompt into the CLI, which is the difference between usually-parseable and parseable. Prompt-level instructions are probabilistic: the model will occasionally wrap the JSON in a fenced block and break the parser at the worst moment. Options C and D are repairs applied downstream of a problem that should not exist.

### CQ-02: Parallel Lanes on One Repository

A nightly job runs four independent Claude Code tasks against the same repository. What keeps their file edits from colliding?

- A) Run them sequentially and accept the longer wall time.
- B) Give each task its own git worktree so each has an isolated checkout on its own branch.
- C) Run all four in the same checkout with distinct `--append-system-prompt` values naming their assigned directories.
- D) Run all four in the same checkout and resolve conflicts with a merge step at the end.

**Answer: B**

Worktrees give each lane a real filesystem-level isolation boundary and a branch to merge deliberately at the end. Option C relies on four independent agents each honouring a directory instruction, and option D lets them overwrite each other's uncommitted work, which git cannot recover.

### CQ-03: What a Headless Run Returns

A pipeline step needs to branch on whether Claude Code succeeded. What should the script check?

- A) Whether the output text contains the word "error".
- B) The process exit code, which headless mode sets for the pipeline to act on.
- C) The presence of an output file, since a failed run writes nothing.
- D) The wall-clock duration, since failures return faster than successes.

**Answer: B**

Headless mode is built to behave like any other command line tool: it exits with a shell code the pipeline can branch on directly. Grepping output text is brittle, and the remaining options infer success from side effects that a partially failed run can still produce.

### CQ-04: Resuming Yesterday's Work

A developer documented half an API on Tuesday and will finish on Wednesday. The codebase has not changed. What is the cheapest correct approach?

- A) Use `--resume` to continue the session, because the prior context is still valid and no tool result has gone stale.
- B) Start a fresh session and re-upload the codebase, asking Claude to identify what is missing.
- C) Fork the session so Wednesday's work runs on a parallel branch.
- D) Start a fresh session with a hand-written summary of Tuesday's progress.

**Answer: A**

Resuming preserves the conversation state, the reasoning path, and prior tool results, so nothing needs re-uploading or re-explaining. Forking is for comparing alternatives from a shared baseline, not for continuing one line of work. Options B and D both pay to reconstruct context that already exists.

### CCA-F Q5 (Domain 1: Agentic Architecture and Orchestration)

A developer spent Tuesday documenting half of an API using an agentic workflow. They plan to finish the second half on Wednesday. Which session management strategy is most efficient for continuing the task, assuming the codebase hasn't changed?

- A) Use `--resume` to continue the session on Wednesday, because the prior context is entirely valid and no tool results have become stale.
- B) Use fork_session on Wednesday to create a parallel branch for the second half of the documentation.
- C) Start a new session and re-upload the entire API codebase, asking Claude to identify what is missing from the previous day's work.
- D) Start a fresh session on Wednesday with a structured summary of what was documented so far, to avoid context window limits.

**Answer: A**

Using session resumption preserves the conversation state, reasoning path, and prior tool outputs, ensuring continuity and avoiding the overhead of re-uploading artifacts or re-explaining the task.

### CCA-F Q43 (Domain 3: Claude Code Configuration and Workflow)

A security team is integrating Claude Code into a GitLab CI pipeline to scan for hardcoded secrets. The pipeline needs to parse the output using `jq` to fail the build if the `severity` field is "CRITICAL". Despite adding "Return ONLY valid JSON" to the prompt, Claude occasionally wraps the JSON output in markdown code blocks, which breaks the `jq` parser. What is the most robust way to configure the Claude Code CLI to guarantee strict JSON output without markdown wrappers?

- A) Set the `CLAUDE_DISABLE_MARKDOWN=true` environment variable in the GitLab CI runner configuration.
- B) Execute the command using the `--output-format json` flag combined with `--json-schema` to enforce a strict, machine-parseable output structure.
- C) Pipe the Claude Code output through a `sed` command that strips leading and trailing markdown code fences before parsing.
- D) Add the `--raw-output` flag to the Claude Code invocation so that the response omits all markdown formatting.

**Answer: B**

Using --output-format json with --json-schema is the most robust way to enforce strict, machine-parseable JSON output. These flags instruct the CLI and model to adhere to a specific schema and return raw JSON, bypassing conversational markdown formatting.

### CCA-F Q47 (Domain 3: Claude Code Configuration and Workflow)

When integrating `Claude Code` into a CI/CD pipeline for automated code reviews, which approach ensures the output is machine-parseable and can be used to programmatically fail a build based on specific criteria?

- A) Use the `--format structured-text` flag to force Claude to use a predictable markdown table format.
- B) Use the `--inline-comments` flag to allow `Claude Code` to interact directly with the GitHub API.
- C) Append "Return ONLY valid JSON" to the prompt and parse the output using `jq`.
- D) Use the `--output-format json` and `--json-schema` CLI flags to enforce machine-parseable structured findings.

**Answer: D**

To generate machine-parseable findings for CI/CD pipelines, run Claude Code with flags like --output-format json and --json-schema. This ensures the output is structured and conforms to a predefined schema, making it reliable for automated parsing and for decisions like failing a build.
