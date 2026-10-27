# Run Claude Code in Headless Mode

Claude Code is designed to run without a human in the loop. The `-p` flag switches it from interactive mode into a single-pass agent that reads a prompt, reasons across turns, calls tools, and exits when the task is complete or a turn limit is reached. In this mode the process is fully scriptable: its output is machine-readable, its exit code is reliable, and its tool access is bounded by whatever you allow.

## The Terminal and the CLI

The two get used as if they were one thing, and the difference is what makes headless mode work. The terminal is where you type: PowerShell, bash, or zsh, in Windows Terminal, iTerm2, or the VS Code panel. It runs programs, pipes their output, and reports their exit codes. Everything this module leans on (`|`, `>`, `$?`, `&&`, background jobs) belongs to the terminal, not to Claude.

The CLI is `claude` itself, one of the programs you run there, alongside `git` and `npm`. So "the CLI" is not the terminal; it is a single program inside it, and that program has two very different modes.

| Mode | Command | Behaviour |
|---|---|---|
| Interactive | `claude` | Takes over the screen, waits for you, never exits on its own |
| Headless | `claude -p "..."` | Reads the prompt, works, prints to stdout, exits with a code |

Only the second composes with the terminal. An interactive session owns the screen and has no exit code to branch on, so it cannot sit inside a pipeline, a CI step, or a cron job. That is why "using the CLI" and "running headless" are not the same claim, and why the rest of this module is about the `-p` half.

## Where Headless Mode Fits

Headless mode pays off wherever a task is well defined enough to state once and valuable enough to repeat. An interactive session is for exploring a problem you cannot yet describe; `-p` is for work you can describe completely up front. Anything that already runs on a trigger (a push, a schedule, a queue, a file drop) is a candidate.

| Use case                    | What the run does                                                              |
| --------------------------- | ------------------------------------------------------------------------------ |
| Pull-request quality gate   | Audits the diff against your standards and exits non-zero to block the merge   |
| Parallel feature lanes      | One agent per Git worktree, each on its own branch, merged after review        |
| Batch work across a repo    | One invocation per file, package, or service, fanned out and collected         |
| Scheduled maintenance       | A cron job that triages new issues, refreshes a changelog, or flags dead links |
| Goal-driven repair          | Loops until a measurable condition holds, then exits clean                     |
| Glue inside a larger script | Emits JSON that the next step in your pipeline consumes                        |

The common thread is that a human reads the result, not the process. That changes how you write the prompt: state the success condition, the output format, and the boundaries, because there is nobody to answer a clarifying question mid-run.

Headless mode is the wrong tool when the task needs judgment you cannot pre-state. A run that would have asked "which of these three approaches do you want" simply picks one. Scope the prompt so any reasonable choice is acceptable, or keep the work interactive.

## The Agent Harness Mental Model

Every Claude Code session runs inside a harness that exposes three interfaces to the model. The tools interface lists which actions are available: reading files, running commands, writing files. The knowledge interface controls what context the model starts with: CLAUDE.md files, injected text, and any resources loaded at session start. The action interface is the output the model produces: text, tool calls, structured JSON, and finally an exit code that the calling process can act on.

Understanding these three interfaces separately is what separates a reliable automation from an unpredictable one. Treating tool scoping as optional means an unmonitored agent can delete files or push branches when all you wanted was a code review. Every harness decision (what tools to allow, what context to inject, what turn limit to set) maps to a specific interface.

## Headless Mode Mechanics

The `--output-format json` flag wraps every Claude response in a structured envelope containing the text result, session metadata, turn count, and token cost. The exit code from the `claude` process is 0 on success and non-zero on error, which is the only signal most CI systems need. Turn limits set with `--max-turns` are a hard cap that prevents runaway loops from burning budget.

Structured output is the bridge between AI judgment and shell automation. Once the result is JSON, you can pipe it through `jq`, extract specific fields, and branch your script on the contents without relying on fragile string parsing. The JSON envelope also makes cost accounting tractable: every session logs its token usage, so you can project what an automated pipeline costs before you run it in production.

## Least-Privilege Tool Scoping

Three flags shape tool access, and they do different jobs. `--allowed-tools` is an allow list: it lets the named tools run without a permission prompt, but it does not remove anything else. `--disallowed-tools` is a deny list: a bare tool name (`Write`) removes that tool from the session, while a scoped rule (`Bash(rm *)`) keeps the tool and denies only matching calls. `--tools` is the restrictive whitelist: it replaces the built-in tool set with exactly the names you pass, and `--tools ""` disables the built-in tools entirely.

| Flag                               | Effect                                           | Use it for                                          |
| ---------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| `--allowed-tools "Read,Glob,Grep"` | Pre-approves those tools so they never prompt    | Removing confirmation friction in an unattended run |
| `--disallowed-tools "Bash(rm *)"`  | Denies matching calls, leaves the tool available | Surgical bans on a specific dangerous command       |
| `--tools "Read,Glob,Grep"`         | Makes those the only built-in tools that exist   | A genuinely read-only audit                         |

Reaching for `--allowed-tools` when you meant `--tools` is the common mistake, and it fails silently. A run scoped with `--allowed-tools "Read,Glob,Grep"` can still write files whenever your `settings.json` already permits writing, because the flag added a permission rather than removing one.

Removing a tool is not the same as removing a capability. Denying `Write` while leaving `Bash` available means the agent can still create the file with a shell redirect, which is exactly what it does when the prompt asks for one. A read-only harness has to close the shell too, and MCP tools sit outside `--tools` entirely, so add `--disallowed-tools "mcp__*"` or `--strict-mcp-config` when a run must not reach connected servers.

Least-privilege scoping is not optional for unmonitored agents. An agent running inside CI with no tool restrictions could, in principle, push code, delete branches, or read secrets from environment variables. The security model is: the harness decides what is possible; the prompt decides what is attempted. Never trust the prompt alone to enforce safety boundaries.

## Hands-On Demo

[Run a Headless Agent and Prove Its Tool Scope](demo-headless-tool-scope.md) takes about five minutes and needs no project setup. You run one `claude -p` call against this topic's own readme, read the real JSON envelope it returns, then run the same write request twice to see `--allowed-tools` let the write through and `--tools` refuse it.

## Helpful Claude Code CLI Commands

| Command                                                     | Usage                                                                           |
| ----------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `claude -p "prompt" --output-format json`                   | Run headless and capture the full structured output envelope.                   |
| `claude -p "prompt" --tools "Read,Glob,Grep"`               | Replace the built-in tool set with a read-only one for safe audits.             |
| `claude -p "prompt" --disallowed-tools "Bash(rm *),mcp__*"` | Deny a specific shell pattern and every MCP tool while leaving the rest intact. |
| `claude -p "prompt" --max-turns 10`                         | Cap the agent at 10 reasoning turns to control cost.                            |

## Key Topics Covered in This Module

- [Claude CLI reference](https://code.claude.com/docs/en/cli-reference): full flag listing including `--tools`, `--allowed-tools`, `--disallowed-tools`, `--output-format`, and `--max-turns`
- [Claude headless JSON output](https://code.claude.com/docs/en/headless#get-structured-output): envelope schema and field descriptions
- [Identity and access management](https://code.claude.com/docs/en/iam): how `settings.json` permission rules combine with the CLI scoping flags
