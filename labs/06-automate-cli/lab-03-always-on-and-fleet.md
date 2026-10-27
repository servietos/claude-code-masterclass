# Keep agents working while you are away from the keyboard

Five ways to keep agents working when you are not at the keyboard: persistent session resume, an OS-level scheduler, the Ralph Wiggum loop technique, GitHub Actions on a schedule, and a parallel-worktree fleet pattern that runs N agents concurrently.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

> **Prerequisites**
> - Complete Lab 01 and Lab 02 (you should have a working `cli-utils/` project on disk and pushed to GitHub).
> - `jq` on your PATH, used in Step 1 to read the session id.
> - **Shell:** every command block is bash. On Windows run them in **Git Bash**. Steps 1, 3 and 5 work there unchanged. Step 2 is the exception, its scheduler is different on Windows and the step gives both forms.
> - Step 4 needs a **GitHub account**, the `gh` CLI authenticated, and an `ANTHROPIC_API_KEY` repo secret (set in Lab 02).
> - Steps 1, 2, 3 and 5 all spend Anthropic API credit. Step 3 spends it in a loop, so read the budget note before you start it.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The project lives outside this course checkout, for the reason Lab 01's Setup gives, so it is not a folder you will find in this repo. Labs 01 and 02 created it; start the session inside it. Both commands work unchanged in PowerShell.

```bash
cd ~/projects/cli-utils
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `cli-utils` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere:

```text
In ~/projects/cli-utils add .github/workflows/weekly-house-keeping.yml running the housekeeping agent every Monday ....
```

That works for any step whose result is just files. It does not work for Step 3b, whose `ralph-wiggum` plugin installs a `Stop` hook into the running session, nor for the `.claude/settings.json` gate Lab 02 left in the project: both load from the directory the session was launched in. Launch inside `cli-utils` from Step 1 onward.

The project is outside this course checkout, so the repo's own `CLAUDE.md`, `.claude/` and `.mcp.json` are not reachable by relative path at all and play no part in this lab. Every path in the prompts below is relative to the project folder.

Everything this lab writes (the cron script, the scheduled workflow, the fleet worktrees) lands there or in your home directory, never in this repository's `.claude/`.

---

## Setup

**Goal:** Start from the repo, on the branch the scheduled workflow in Step 4 needs.

**Command:**

```bash
git checkout main && git pull
```

Lab 02 left you on `feat/uppercase-helper`. GitHub only registers a `schedule:` or `workflow_dispatch:` workflow once it exists on the **default branch**, so Step 4 must commit there. Substitute `master` for `main` if that is what `git init` gave you in Lab 01:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

**Expected result:** You are on the default branch with a clean tree. No further setup, every step uses the existing project plus the Claude CLI.

---

## Step 1: Persistent Sessions With `--resume` and `--continue`

**Goal:** Pick up a Claude session across terminal restarts. Useful when a refactor takes hours and you want to close the laptop without losing context.

**Commands:**

Start a session and have it do partial work:

```bash
claude --print "Read src/slugify.ts. Propose three concrete improvements but DO NOT implement them yet. Tell me which one you'd start with."
```

Capture the session id with `claude --print --output-format json`. Plain print mode returns only the answer text, no id:

```bash
claude --print --output-format json "Read src/slugify.ts. Propose three concrete improvements but DO NOT implement them yet." | jq -r '.session_id' > /tmp/last-session.txt
cat /tmp/last-session.txt
```

Resume it later (any time, same machine):

```bash
SESSION=$(cat /tmp/last-session.txt)
claude --resume "$SESSION" "Now implement improvement #1. Run the tests after."
```

Or continue the most recent session without specifying an id:

```bash
claude --continue "Run improvement #2 now."
```

**Expected result:** `/tmp/last-session.txt` holds a UUID such as `c1af47aa-b4f0-4b7f-9d5f-de8916ce7372`. The resumed session remembers the three improvements proposed earlier and proceeds with #1 directly, with no re-pasting of context. The session id is durable across terminal restarts: close the terminal, open a new one, `--resume` still works.

---

## Step 2: OS Scheduler for Headless Runs

**Goal:** Run `claude -p` on a schedule via the operating system's scheduler. The agent fires whether you are at the keyboard or not.

**Commands:**

Create the script the scheduled job will call. This part is identical on every platform and runs fine in Git Bash on Windows:

```bash
mkdir -p ~/cli-utils-cron
cat > ~/cli-utils-cron/hourly-summary.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
cd /full/path/to/cli-utils    # <-- edit this to your absolute path

DATE=$(date +%Y-%m-%d)
OUT=~/cli-utils-cron/logs/summary-$DATE.md
mkdir -p "$(dirname "$OUT")"

claude -p "Summarise the last 24 hours of git activity on this repo (commits, branches, file changes). Append the summary as a new dated section to $OUT. Be terse, bullet points only." --max-turns 4 --allowed-tools "Read,Write,Bash(git:*)" >> ~/cli-utils-cron/logs/cron.log 2>&1
SH
chmod +x ~/cli-utils-cron/hourly-summary.sh
```

`--allowed-tools` matters here: an unattended run has nobody to answer a permission prompt, so the agent must be pre-approved for the Write it is being asked to perform. The prompt sits before that variadic flag, per the Lab 01 Step 1 rule.

Test it manually first:

```bash
~/cli-utils-cron/hourly-summary.sh
cat ~/cli-utils-cron/logs/summary-$(date +%Y-%m-%d).md
```

**Register it, macOS or Linux (or WSL):**

```bash
crontab -l > /tmp/crontab.bak 2>/dev/null || true
(crontab -l 2>/dev/null; echo "0 * * * * $HOME/cli-utils-cron/hourly-summary.sh") | crontab -
crontab -l | tail -3
```

**Register it, Windows:** there is no cron daemon and no `crontab` command on Windows, Git Bash included (`which crontab` comes back empty). Use Task Scheduler instead, pointing it at Git Bash as the interpreter. Run these two from **PowerShell**:

```powershell
schtasks /Create /TN cli-utils-hourly /SC HOURLY /TR '"C:\Program Files\Git\bin\bash.exe" -lc "~/cli-utils-cron/hourly-summary.sh"'
schtasks /Query /TN cli-utils-hourly
```

Keep the outer single quotes. They are what makes PowerShell hand the whole quoted command line to `schtasks` as one argument; the `\"` escaping that works in cmd splits into fragments here.

**Expected result:** The manual run produces a dated summary file. The registered job shows up in `crontab -l` (Unix) or `schtasks /Query /TN cli-utils-hourly` (Windows). After an hour, a new section appears in the dated summary file, written without any human in the loop.

Remove the job when finished:

```bash
crontab /tmp/crontab.bak
```

```powershell
schtasks /Delete /TN cli-utils-hourly /F
```

---

## Step 3: Ralph Wiggum Loop

**Goal:** Use the [Ralph Wiggum technique](https://ghuntley.com/ralph/), a self-referential loop where the same prompt is fed back to the agent until it self-declares completion. There are two flavours: vanilla bash (Geoffrey Huntley's original) and the official Anthropic [`ralph-wiggum` plugin](https://github.com/anthropics/claude-code/blob/main/plugins/ralph-wiggum/README.md).

> **Budget warning:** every iteration is a fresh billed session. Both forms below are bounded on purpose, the bash loop by an iteration counter and a dollar cap, the plugin by `--max-iterations`. Never run this pattern unbounded.

### 3a: The vanilla bash form

**Command:**

```bash
mkdir -p ralph-experiment
cd ralph-experiment

cat > PROMPT.md <<'MD'
Build a complete Node.js todo CLI with:
  - add "task": create a todo (stored in todos.json)
  - list: list all todos
  - done <id>: mark a todo done
  - remove <id>: remove a todo

Requirements:
  - ESM modules, Node 22+
  - Vitest tests covering each command, real fs operations on a tmp dir
  - All tests passing
  - README with usage examples

When everything above is true, end your response with the literal token: TASK_COMPLETE
MD

for i in $(seq 1 10); do
  RESPONSE=$(claude -p "$(cat PROMPT.md)" --max-turns 8 --max-budget-usd 2 --permission-mode acceptEdits --allowed-tools "Read,Edit,Write,Bash(npm *),Bash(npx *)" 2>&1)
  echo "--- iteration $i ($(date +%H:%M:%S)) ---"
  echo "$RESPONSE" | tail -20
  if echo "$RESPONSE" | grep -q "TASK_COMPLETE"; then
    echo "Ralph: done after $i iterations."
    break
  fi
  sleep 5
done

cd ..
```

`--max-turns` caps the turns inside one iteration and `--max-budget-usd` caps the spend of that iteration; the `for` loop caps how many iterations you pay for at all. `--max-turns` is a real, documented flag ([CLI reference](https://code.claude.com/docs/en/cli-reference)) even though it is currently missing from `claude --help` output, so do not assume it is a typo. `--permission-mode acceptEdits` and `--allowed-tools` let each iteration write files and run npm, which print mode otherwise denies (Lab 01, Step 1).

**Expected result:** The same prompt is fed in repeatedly. Each iteration Claude sees the previous iteration's files in the working tree and improves on them. The loop terminates when Claude writes `TASK_COMPLETE`, or after ten iterations, whichever comes first. Typical completion is 3 to 6 iterations. Cancel early at any time with `Ctrl+C`.

### 3b: The official `ralph-wiggum` plugin (in-session)

The Anthropic plugin keeps the session alive with a `Stop` hook, so it needs no external bash loop. Searching the default marketplace for `ralph-wiggum` finds nothing, it lives in a different marketplace than the one configured out of the box. Add it first, from inside Claude Code:

```text
/plugin marketplace add anthropics/claude-code
/plugin install ralph-wiggum@claude-code
```

The default `claude-plugins-official` marketplace publishes the same capability under the name `ralph-loop`, with the same commands, if you would rather not add a marketplace.

Then run the loop:

```text
/ralph-loop "Build a Node.js todo CLI with add/list/done/remove commands, Vitest tests, README. Output <promise>COMPLETE</promise> when all tests pass." --completion-promise "COMPLETE" --max-iterations 10
```

**Expected result:** Claude works on the task, attempts to exit, the Stop hook blocks the exit and feeds the prompt back in. The loop terminates when Claude outputs `<promise>COMPLETE</promise>` or hits `--max-iterations`. Use `/cancel-ralph` to stop manually.

**Compare the two:** The bash form is portable, scriptable from outside, and works with any agent CLI. The plugin form stays inside one session, gets richer iteration tracking, and is more ergonomic when you are already in Claude Code.

---

## Step 4: GitHub Actions on a Schedule

**Goal:** A scheduled cloud-side always-on agent. No machine to keep running and no local scheduler to maintain, GitHub triggers it on cadence.

**Command:**

From the `cli-utils` repo, on the default branch:

```bash
cat > .github/workflows/weekly-house-keeping.yml <<'YML'
name: Weekly house-keeping

on:
  schedule:
    - cron: "0 9 * * 1"   # every Monday at 09:00 UTC
  workflow_dispatch: {}

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  housekeeping:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0

      - run: npm install -g @anthropic-ai/claude-code

      - name: Run housekeeping agent
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          claude -p "
            Check the repo for housekeeping items:
              - Open issues older than 60 days with no activity: list them with their numbers and ages.
              - Stale branches (no commits in 30 days): list them.
              - Direct dependencies whose latest version is more than one major behind: list them.

            Open ONE issue titled 'Weekly housekeeping report ($(date +%Y-%m-%d))' with the findings as a structured markdown body. Use gh issue create.
          " --max-turns 6 --allowed-tools "Read,Bash(git:*),Bash(npm:*),Bash(gh issue *)"
        # Note: gh CLI is preinstalled on ubuntu-latest runners.
YML

git add .github/workflows/weekly-house-keeping.yml
git commit -m "ci: weekly housekeeping agent"
git push
```

Three details in that `run:` block are easy to get wrong and all three fail silently:

- The prompt is **double-quoted**, so backticks inside it would be command substitution. Writing ``Use `gh issue create`.`` makes the runner execute `gh issue create` while building the string and splice its empty output in, leaving the agent with `Use .` and no instruction. Plain `Use gh issue create.` is correct. `$(date +%Y-%m-%d)` is deliberate substitution and does expand as intended.
- `gh` is preinstalled on the runner but refuses to run without a token, hence `GH_TOKEN`. The job already declares `issues: write`, which is the scope `gh issue create` needs.
- `--allowed-tools` must pre-approve `Bash(gh issue *)`, otherwise the agent has no way to run the command it was asked to run. It follows the closing quote of the prompt because the flag is variadic.

Trigger it once by hand now:

```bash
gh workflow run "Weekly house-keeping"
gh run watch
```

`gh workflow run` dispatches against the workflow file as it exists on the default branch, which is why the Setup step put you there.

**Expected result:** The workflow appears in the Actions tab, and the manual dispatch opens one new issue titled `Weekly housekeeping report (<date>)` with structured findings. What the findings contain depends on your repo's age and dependencies; on a repo two labs old, expect a short report with mostly empty sections. From this point onward it fires every Monday at 09:00 UTC, and it costs nothing between firings because it only consumes compute when GitHub triggers it.

---

## Step 5: Parallel Worktree Fleet

**Goal:** Spawn N independent agent workers in parallel via `git worktree` and `xargs -P`. Each worker runs an independent task in an isolated worktree. This is the closest you get to a "fleet" without paid orchestration tooling.

**Commands:**

Create the task file, five independent improvements that can all run in parallel:

```bash
mkdir -p fleet-runs
cat > fleet-runs/tasks.txt <<'EOF'
add-uppercase|Add src/uppercase.ts exporting toUpper(s: string): string. Add tests.
add-truncate|Add src/truncate.ts exporting truncate(s: string, n: number): string. Add tests.
add-reverse|Add src/reverse.ts exporting reverse(s: string): string. Add tests.
add-pad|Add src/pad.ts exporting pad(s: string, n: number, ch: string): string. Add tests.
add-trim|Add src/trim-ext.ts exporting trimAll(s: string): string. Add tests.
EOF
```

Create the five worktrees **serially, before** the fan-out. Five concurrent `git worktree add` calls all write into the same `.git`, and the tempting `git worktree add ... || true` inside the worker hides any failure: the worker then falls into the next line, `cd` into a directory that was never created, and dies quietly under `set -e`. Creating them up front removes the race and lets a missing worktree be a loud error:

```bash
while IFS= read -r line; do
  [ -n "$line" ] || continue
  NAME=${line%%|*}
  git worktree add "../cli-utils-$NAME" -b "feat/$NAME"
done < fleet-runs/tasks.txt

git worktree list
```

The runner script assumes its worktree already exists and refuses to continue if it does not, so it can never work silently in the wrong directory:

```bash
cat > fleet-runs/run-one.sh <<'SH'
#!/usr/bin/env bash
set -euo pipefail
TASK=$1
NAME=${TASK%%|*}
DESC=${TASK#*|}

REPO=$(git rev-parse --show-toplevel)
WORKTREE="$REPO/../cli-utils-$NAME"

cd "$WORKTREE" || { echo "missing worktree: $WORKTREE" >&2; exit 1; }
npm install --silent
claude -p "$DESC. Run \`npm test\` to confirm. Commit with message 'feat: $NAME'." --max-turns 5 --max-budget-usd 1 --permission-mode acceptEdits --allowed-tools "Read,Edit,Write,Bash(npm *),Bash(git *)" > "$REPO/fleet-runs/log-$NAME.txt" 2>&1
echo "done: $NAME"
SH
chmod +x fleet-runs/run-one.sh
```

A fresh worktree has no `node_modules/` (Lab 01, Step 3), and the two permission flags let each worker edit, test and commit, which print mode otherwise denies.

Run the fleet, five parallel workers:

```bash
xargs -P 5 -I {} ./fleet-runs/run-one.sh "{}" < fleet-runs/tasks.txt
```

`xargs -P` with `-I` really does run the workers concurrently in Git Bash on Windows as well as on macOS and Linux: five three-second workers finish in about four seconds of wall clock, where a serial run takes fifteen.

When all five finish:

```bash
git worktree list
git branch -a | grep feat/add-
ls fleet-runs/log-*.txt
```

Inspect a log:

```bash
tail -20 fleet-runs/log-add-uppercase.txt
```

**Expected result:** Five log files, one per worker, and five `feat/add-*` branches. Each worker that got its tests passing within its turn budget leaves one commit on its branch; any worker that ran out of turns leaves its branch at the base commit and says so in its log, so read the logs before you count on five commits. All five ran concurrently, so total wall-clock time is roughly the slowest single worker, well below the sum.

Clean up:

```bash
for name in add-uppercase add-truncate add-reverse add-pad add-trim; do
  git worktree remove "../cli-utils-$name" --force 2>/dev/null || true
  git branch -D "feat/$name" 2>/dev/null || true
done
```

---

## What You Just Practised

| Mechanic | Step | When to reach for it |
|---|---|---|
| `claude --resume` and `--continue` | 1 | Multi-hour refactors that span sessions |
| OS scheduler (cron or Task Scheduler) + `claude -p` | 2 | Periodic agent work tied to a specific machine |
| Ralph Wiggum loop (bash, bounded) | 3a | Bounded autonomous tasks with a clear completion signal |
| Ralph Wiggum loop (Anthropic plugin) | 3b | The same, but inside one Claude session with iteration tracking |
| GitHub Actions `schedule:` cron | 4 | Cloud-side always-on work with zero idle cost |
| `git worktree` + `xargs -P` fleet | 5 | N independent tasks that can run in parallel |

This finishes Module 06. The progression: Lab 01 ran Claude headlessly, Lab 02 wired it into CI and compared it against other agent CLIs, Lab 03 kept it running when no human is watching.
