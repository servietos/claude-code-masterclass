# Run a Headless Agent and Prove Its Tool Scope

Run `claude -p` for the first time, read the JSON envelope it returns, then prove on your own machine which scoping flag actually makes a run read-only. Four commands run against this topic's own readme, and there is no project to install. You end holding evidence that `--allowed-tools` grants permission while `--tools` withdraws capability, plus the envelope fields a script branches on.

------

## Prerequisites

- Claude Code installed and logged in (`claude --version` prints a version).
- A terminal open at this topic folder: `cd demos/05-cli/01-intro`. Every command below runs there, and the only file the demo can create is `scoped.txt`, which you delete at the end.

## Step 1: Run one headless call

```bash
claude -p "List the H2 headings in readme.md, one per line, with no commentary." --tools "Read,Glob,Grep" --max-turns 5
```

Expected output:

```text
The Terminal and the CLI
Where Headless Mode Fits
The Agent Harness Mental Model
Headless Mode Mechanics
Least-Privilege Tool Scoping
Hands-On Demo
Helpful Claude Code CLI Commands
Key Topics Covered in This Module
```

Expected result: the headings print as plain text with no session UI, no spinner, and no prompt afterwards. The process has already exited, and its exit code is 0 (`echo $?` in bash, `$LASTEXITCODE` in PowerShell).

## Step 2: Read the JSON envelope

```bash
claude -p "List the H2 headings in readme.md, one per line, with no commentary." --tools "Read,Glob,Grep" --max-turns 5 --output-format json
```

The envelope contains these fields among others:

```json
{
  "type": "result",
  "subtype": "success",
  "is_error": false,
  "num_turns": 2,
  "session_id": "1ef515cf-ab16-45b7-b7af-748b6a60454c",
  "total_cost_usd": 1.584339,
  "result": "The Terminal and the CLI\nWhere Headless Mode Fits\n..."
}
```

Expected result: a single JSON object on stdout. Your `session_id` and `total_cost_usd` will differ; the field names will not.

## Step 3: Watch `--allowed-tools` fail to lock the run down

Ask a supposedly read-only agent to create a file:

```bash
claude -p "Create a file named scoped.txt in this folder containing the word hello." --allowed-tools "Read,Glob,Grep" --max-turns 3
```

Then check whether it did:

```bash
ls scoped.txt
```

Expected result: on a typical developer setup the file exists, and Claude reports having created it. The flag named "allowed tools" did not restrict anything, because it grants permissions instead of withdrawing them. If your `settings.json` does not already permit writing you may see a refusal instead; that is the same lesson from the other side, since the outcome was decided by your settings rather than by the flag.

## Step 4: Lock it down for real with `--tools`

```bash
claude -p "Create a file named scoped.txt in this folder containing the word hello." --tools "Read,Glob,Grep" --max-turns 3
```

Claude reports that it cannot comply, naming the tools it has:

```text
I can't create that file: this session has no file-writing tool enabled. The only
local tools available to me here are read-only: Read, Glob, and Grep.
```

Expected result: no file is created. Run `ls scoped.txt` and the shell reports that it does not exist, which is the only proof that matters. The exact wording of the refusal varies between runs; the absence of the file does not.

## Verify

You have proven three things on your own machine:

- `claude -p` exits on its own and prints to stdout, so it composes with pipes and exit codes.
- `--output-format json` returns `is_error`, `result`, `num_turns`, and `total_cost_usd` for a script to branch on.
- `--allowed-tools` grants permission while `--tools` withdraws capability, and only the second produces a read-only run.

One caveat worth carrying forward: `--tools` governs the built-in tools only. Connected MCP servers remain reachable, so a run that must not touch them also needs `--disallowed-tools "mcp__*"` or `--strict-mcp-config`.

