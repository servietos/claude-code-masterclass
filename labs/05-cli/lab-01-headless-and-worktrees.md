# Drive Claude Code headlessly and run parallel work in git worktrees

Drive Claude Code without a terminal UI. You will run `claude -p` for one-shot prompts, wrap it in a shell script with meaningful exit codes, run independent changes in parallel across git worktrees, kick off background tasks, and inject a skill on demand for a single run.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

## Prerequisites

- **Shell**: run every command in this lab from git-bash (Windows), WSL, or a macOS/Linux shell. PowerShell and cmd do not support the heredocs, herestrings, `chmod`, `nohup` or `/tmp` paths used here. In git-bash `/tmp` resolves to your Windows temp folder (`cygpath -w /tmp` prints the real path).
- **jq**: not bundled with Git for Windows. Install it first (`winget install jqlang.jq`) or drop the `| jq .` from Step 1.
- **Node.js 20+** and **npm**, for the project you scaffold in Setup.
- **Claude Code 2.x**: `claude --version` (this lab was verified against 2.1.219).

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The project lives outside this course checkout, for the reason Setup gives, so it is not a folder you will find in this repo. Setup below creates it; start the session inside it. Both commands work unchanged in PowerShell.

```bash
cd ~/projects/cli-utils
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `cli-utils` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere:

```text
In ~/projects/cli-utils write scripts/lint-with-claude.sh so it exits 1 when the model reports a lint issue ....
```

That works for any step whose result is just files. It does not work for the rest of the lab, because every step runs shell commands (`claude -p`, `git worktree add`, `nohup ... &`) that resolve `src/`, the project's `.git` and Step 5's `.claude/skills/` layout against the directory they were launched in, so a session opened elsewhere drives the wrong tree. Launch inside `cli-utils` from Step 1 onward.

The project is outside this course checkout, so the repo's own `CLAUDE.md`, `.claude/` and `.mcp.json` are not reachable by relative path at all and play no part in this lab. Every path in the prompts below is relative to the project folder.

Labs 02 and 03 open their sessions in the same folder.

## Setup: Scaffold a Tiny Node CLI

Steps 2 and 3 (and Lab 02) treat `cli-utils` as its own top-level git repository, so scaffold it **outside this course repo**. Running `git init` inside the course repo nests a repository, and Step 3 then drops two extra working trees into the course checkout as untracked junk.

```bash
cd ~/projects          # any folder OUTSIDE this course repo
mkdir cli-utils
cd cli-utils
```

Start Claude Code in that folder as the launch block above shows, then build the starter:

```text
Scaffold a Node.js CLI library at this folder:
  - package.json with type: module, name cli-utils
  - devDependencies: vitest (test runner) and typescript
  - scripts: "test": "vitest run" and "typecheck": "tsc --noEmit"
  - src/slugify.ts: function slugify(input: string): string that lowercases, strips non-alphanumerics, joins with hyphens
  - src/kebab-to-camel.ts: function kebabToCamel(input: string): string
  - JSDoc with @param and @returns on every exported function
  - test/ with Vitest tests covering both functions
  - tsconfig.json with strict mode
  - An empty scripts/ folder for shell wrappers
  - A README.md describing the two utilities

Install dependencies, then confirm `npm test` and `npm run typecheck` both pass.

Then `git init && git add . && git commit -m "initial scaffold"`.
```

**Expected result:** A `cli-utils/` folder with both source files, `npm test` green (Vitest runs the `.ts` sources directly, no build step) and `npm run typecheck` exit 0. Note that `npm test` alone never enforces strict mode: Vitest transpiles without type-checking, so `npm run typecheck` is the step that actually exercises the strict `tsconfig.json`.

The finished project is checked in at [01-headless/cli-utils-solution/](01-headless/cli-utils-solution/) as the completed reference (it deliberately ships no `.git`, so copy it out before running Step 3).

## Step 1: Headless Print Mode

**Goal:** Run Claude headlessly with `claude -p`, capture stdout, and inspect the output format.

**Command:**

Exit Claude Code (`/exit`). Then from the project root:

```bash
claude -p "Read src/slugify.ts and explain the algorithm in 3 bullets."
```

Then run it again with structured output:

```bash
claude -p "Read src/slugify.ts and return a JSON object with keys 'algorithm' (3 bullets) and 'edge_cases' (3 examples)." --output-format json | jq .
```

**Expected result:** The first run prints plain markdown to stdout. The second returns a JSON envelope whose fields include `result` (the model's response) plus `total_cost_usd`, `duration_ms`, `session_id`, `num_turns`, `is_error`, `usage` and `permission_denials`. `jq .` confirms the JSON parses cleanly.

Two rules that the rest of this lab depends on:

- **Print mode cannot ask for permission.** A `-p` run has no one to answer a prompt, so every tool call that is not covered by your settings is denied and recorded in `permission_denials`. Reading files works on a default profile; writing, editing and running commands does not. That is why Steps 3 and 4 pass `--permission-mode acceptEdits` and an explicit `--allowed-tools` list.
- **Variadic flags swallow the prompt.** `--add-dir <directories...>`, `--allowed-tools <tools...>` and `--tools <tools...>` accept multiple values, so a positional prompt placed after them is parsed as one more value and Claude exits with `Error: Input must be provided either through stdin or as a prompt argument when using --print`. Always put the prompt **before** a variadic flag.

## Step 2: CI Exit Codes

**Goal:** Wrap `claude -p` in a bash script that returns a meaningful non-zero exit code when the model reports a problem. This is the building block for using Claude as a CI gate.

**Command:**

Create `scripts/lint-with-claude.sh`. The `mkdir -p` matters: the heredoc fails with `No such file or directory` if `scripts/` does not exist yet.

```bash
mkdir -p scripts
cat > scripts/lint-with-claude.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail

OUT=$(claude -p "Read src/slugify.ts and src/kebab-to-camel.ts. Look for: (1) unused exports, (2) missing JSDoc on exported functions, (3) any function over 30 lines. If you find ANY issue, end your response with the exact token: LINT_FAIL. If everything is clean, end with LINT_PASS." --output-format text)

echo "$OUT"

if grep -q "LINT_FAIL" <<< "$OUT"; then
  echo "claude-lint: issues found" >&2
  exit 1
fi

if grep -q "LINT_PASS" <<< "$OUT"; then
  exit 0
fi

echo "claude-lint: indeterminate output, neither LINT_PASS nor LINT_FAIL found" >&2
exit 2
SH
chmod +x scripts/lint-with-claude.sh
```

Then run it:

```bash
./scripts/lint-with-claude.sh
echo "exit code: $?"
```

Now introduce a deliberate issue, an unused export in `src/slugify.ts`:

```bash
echo "export const UNUSED_EXPORT = 42;" >> src/slugify.ts
./scripts/lint-with-claude.sh
echo "exit code: $?"
```

Roll the change back:

```bash
git checkout src/slugify.ts
```

**Expected result:** The first run ends with `LINT_PASS` and exits `0`, but only because the Setup prompt asked for JSDoc on every exported function; drop that requirement and criterion (2) fails the gate on a pristine scaffold. The deliberate-issue run prints `claude-lint: issues found` on stderr and exits `1`. The third exit code, `2`, is your safety net: a model that answers with neither token is a broken gate, not a passing one. The exit code is now a real signal you can plug into CI.

## Step 3: Parallel Worktrees

**Goal:** Run two independent changes simultaneously in separate git worktrees. Each worktree gets its own Claude session, and neither can clobber the other's working tree.

**Commands:**

```bash
git worktree add ../cli-utils-feat-camel -b feat/camel-improvements
git worktree add ../cli-utils-feat-slug -b feat/slug-improvements
```

A fresh worktree contains tracked files only, and `node_modules/` is git-ignored, so `npm test` cannot run until you install in each tree.

In one terminal, in the first worktree:

```bash
cd ../cli-utils-feat-camel
npm install
claude -p "Improve src/kebab-to-camel.ts to handle multi-word kebab strings ('a-b-c-d' -> 'aBCD'). Add tests covering 2, 3, and 4-segment inputs. Commit when tests pass." --permission-mode acceptEdits --allowed-tools "Read,Edit,Write,Bash(npm *),Bash(git *)"
```

In a second terminal, in the second worktree (in parallel):

```bash
cd ../cli-utils-feat-slug
npm install
claude -p "Improve src/slugify.ts to preserve numbers and strip leading/trailing hyphens. Add tests for these cases. Commit when tests pass." --permission-mode acceptEdits --allowed-tools "Read,Edit,Write,Bash(npm *),Bash(git *)"
```

Both prompts sit before the variadic `--allowed-tools`, per the Step 1 rule. Without the two permission flags every edit, npm run and commit is denied and the run produces nothing.

When both finish:

```bash
cd ../cli-utils
git worktree list
git log --all --oneline | head -10
```

**Expected result:** Two new branches with one commit each, both visible in `git log --all`. Neither worktree interfered with the other. The two changes can be reviewed and merged independently.

Clean up:

```bash
git worktree remove ../cli-utils-feat-camel
git worktree remove ../cli-utils-feat-slug
```

If a run left an uncommitted change or an untracked file behind (a half-written test, a stray notes file), removal refuses with `fatal: ... contains modified or untracked files, use --force to delete it`. Use `git worktree remove --force <path>` then. An ignored `node_modules/` in the tree does not block removal. Removing a worktree leaves its branch in place; `git branch -d feat/camel-improvements` drops that too.

## Step 4: Background Async Task

**Goal:** Kick off a long-running headless task in the background, poll its output file, and keep using the terminal for other work.

**Commands:**

`nohup`, `$!` and `kill -0` are POSIX-only. They all work in git-bash on Windows; in PowerShell none of them exist. The `< /dev/null` matters: a backgrounded `claude -p` otherwise stalls waiting on stdin and logs `Warning: no stdin data received in 3s`.

```bash
nohup claude -p "Write a comprehensive ARCHITECTURE.md describing this project: every module, every function signature, and every test file. Save to ARCHITECTURE.md. Be thorough, target 1,500+ words." --permission-mode acceptEdits --allowed-tools "Read,Write,Edit" < /dev/null > /tmp/claude-bg.log 2>&1 &

BG_PID=$!
echo "background pid: $BG_PID"
```

Now poll without blocking your terminal:

```bash
while kill -0 $BG_PID 2>/dev/null; do
  echo "still running... ($(wc -c < /tmp/claude-bg.log 2>/dev/null || echo 0) bytes logged)"
  sleep 5
done
echo "done. ARCHITECTURE.md size: $(wc -c < ARCHITECTURE.md) bytes"
```

**Expected result:** The background process runs without occupying the terminal. The poll loop prints periodic status. When the process finishes, `ARCHITECTURE.md` exists with substantial content. `cat /tmp/claude-bg.log` shows the output post-hoc.

## Step 5: Inject a Skill On Demand for One Run

**Goal:** Run a one-shot Claude invocation that has access to a skill which is not registered in the project's `.claude/skills/`. Useful for ephemeral tools, or for testing a skill before promoting it.

**Commands:**

`--add-dir` loads a directory's `.claude/skills/` and `.claude/agents/`, not arbitrary `SKILL.md` files lying around in it. A skill at `<added-dir>/json-summarize/SKILL.md` is never discovered; it has to sit at `<added-dir>/.claude/skills/<name>/SKILL.md`. Create exactly that layout:

```bash
mkdir -p /tmp/ephemeral-skills/.claude/skills/json-summarize
cat > /tmp/ephemeral-skills/.claude/skills/json-summarize/SKILL.md <<'MD'
---
name: json-summarize
description: Produce a one-line JSON summary of a code module
---

# JSON Summarize

When the user asks to summarize a file, return ONLY a one-line JSON object with keys:
  file: <path>
  exports: [<exported symbol names>]
  loc: <line count>
  has_tests: <boolean, true if a matching test file exists under test/>

No prose, no markdown, no other text.
MD
```

Run Claude with that skills directory injected, prompt first:

```bash
claude -p "Use the json-summarize skill on src/slugify.ts" --add-dir /tmp/ephemeral-skills
```

**Expected result:** Claude returns a one-line JSON object summarising `src/slugify.ts`, for example `{"file":"src/slugify.ts","exports":["slugify"],"loc":13,"has_tests":true}`. The skill was never in the project's `.claude/skills/`, and after the run the project's `.claude/` is unchanged.

To prove the skill really loaded, list what the session registered:

```bash
claude -p "hi" --output-format stream-json --verbose --add-dir /tmp/ephemeral-skills | jq -r 'select(.subtype=="init") | .skills[]' | grep json-summarize
```

Point `--add-dir` at the folder without the `.claude/` layer and the same command prints nothing, which is the silent failure this step exists to expose.

## What You Just Practised

| Mechanic | Step | Use it for |
|---|---|---|
| `claude -p "..."` headless one-shot | 1 | Any non-interactive invocation |
| `--output-format json` | 1 | Anything piped to `jq` or another script |
| Prompt before variadic flags | 1 | Every command that also passes `--add-dir` or `--allowed-tools` |
| Exit-code wrapping with sentinel tokens | 2 | CI gates, pre-commit hooks |
| `--permission-mode` + `--allowed-tools` | 3, 4 | Any headless run that writes, edits or shells out |
| Parallel `git worktree` | 3 | Independent feature branches running concurrently |
| `nohup … &` background launch + poll | 4 | Long-running documentation, large refactors |
| `--add-dir` with a `.claude/skills/` layout | 5 | Testing a skill before promoting, one-off tools |

[Lab 02](lab-02-hooks-actions-and-cli-comparison.md) turns these mechanics into a real GitHub Actions workflow, layers a PreToolUse hook on top as a policy gate, and runs the same task through OpenAI Codex CLI and Aider so you have a feel for the broader agent-CLI landscape.
