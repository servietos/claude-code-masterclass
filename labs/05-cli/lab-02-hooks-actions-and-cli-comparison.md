# Gate tools with PreToolUse hooks and review pull requests in CI

Build a PreToolUse hook that gates dangerous commands, wire Claude into a GitHub Actions workflow that comments on pull requests, then run the same task through OpenAI Codex CLI and Aider so you have a felt sense of the agent-CLI landscape, not just Claude Code.

Each step contains:
- **Goal**: what you are building
- **Prompt or command**: what you run
- **Expected result**: what the outcome looks like

> **Prerequisites**
> - Complete Lab 01 (you should have a working `cli-utils/` project).
> - `jq` on your PATH. Both hook scripts parse their stdin with it (`winget install jqlang.jq` on Windows, `brew install jq` on macOS, `apt install jq` on Linux).
> - **Shell:** every command block in this lab is bash. On Windows run them in **Git Bash**, not PowerShell. Where a PowerShell equivalent matters, it is given inline.
> - Steps 3, 4 and 7 need a **GitHub account** and the `gh` CLI authenticated (`gh auth status`) against a user that can create public repos. Without one, read those steps and skip the pushes.
> - Steps 3 and 4 need an **Anthropic API key** stored as a repo secret. Steps 5 and 6 need an **OpenAI (or other model provider) key** of your own. These are billed to you.

> **Completed reference:** the finished hook scripts, settings and workflow files live in [02-cicd/hooks-solution/](02-cicd/hooks-solution/), together with `test-hooks.sh`, a stdin harness that feeds both hooks real PreToolUse payloads. Build your own first, compare afterwards.

---

## Where to Open Claude Code

This lab builds its own harness, so open Claude Code inside the lab project rather than at the repo root. The harness is project-scoped: `CLAUDE.md`, `.claude/settings.json` hooks, `.claude/agents/`, `.claude/skills/`, `.claude/commands/` and `.mcp.json` all load from the directory the session was launched in. A session opened at the repo root leaves everything you write here inert, with no error to tell you.

The project lives outside this course checkout, for the reason Lab 01's Setup gives, so it is not a folder you will find in this repo. Lab 01 created it; start the session inside it. Both commands work unchanged in PowerShell.

```bash
cd ~/projects/cli-utils
claude
```

If you start Claude Code with the Claude Terminal extension (`Ctrl+F1` / `Cmd+F1`), it opens in the VS Code workspace folder and reuses an already-open terminal, so it will not follow the `cd` above. Open `cli-utils` as the workspace folder (**File > Open Folder**) before pressing the shortcut, or run the command above in a plain terminal.

> Note: you can also skip the folder switch entirely and name the path in the prompt instead, working from a session opened anywhere:

```text
In ~/projects/cli-utils write a PreToolUse hook that blocks rm -rf and git push --force ....
```

That works for any step whose result is just files. It does not work for the gate itself: `.claude/settings.json` and the scripts under `.claude/hooks/` load from the directory the session was launched in, so a session opened elsewhere writes the hooks into `cli-utils` and then never fires them. Launch inside `cli-utils` from Step 1 onward.

Restart the session with `/exit` then `claude` after any edit to `.claude/settings.json`, because hook configuration is read at startup.

The project is outside this course checkout, so the repo's own `CLAUDE.md`, `.claude/` and `.mcp.json` are not reachable by relative path at all and play no part in this lab. Every path in the prompts below is relative to the project folder.

The hooks and `settings.json` you write in Step 1 belong under that project's `.claude/`, never under this repository's.

---

## Setup: Push the Project to GitHub

**Goal:** Get `cli-utils` onto GitHub so the workflow steps have somewhere to run.

**Command:**

```bash
gh repo create cli-utils --public --source=. --remote=origin --push
gh repo view --web
```

Note which branch GitHub made the default, you will need the name in Step 5:

```bash
gh repo view --json defaultBranchRef --jq '.defaultBranchRef.name'
```

**Expected result:** A public `cli-utils` repo at `github.com/<your-user>/cli-utils`. The default branch is whatever `git init` produced in Lab 01, `main` on recent Git, `master` on older configurations. Use that name wherever this lab writes `main`.

---

## Step 1: PreToolUse Hook as a Policy Gate

**Goal:** Block destructive commands (`rm -rf`, writes outside `src/`, `git push --force`) at the harness level. Hooks fire before tools run, so they enforce policy without depending on the model behaving.

**Command:**

Create `.claude/settings.json` (or merge into the existing file):

```bash
mkdir -p .claude/hooks
cat > .claude/settings.json <<'JSON'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/policy-gate.sh\"" }
        ]
      },
      {
        "matcher": "Write|Edit",
        "hooks": [
          { "type": "command", "command": "bash \"$CLAUDE_PROJECT_DIR/.claude/hooks/scope-gate.sh\"" }
        ]
      }
    ]
  }
}
JSON

cat > .claude/hooks/policy-gate.sh <<'SH'
#!/usr/bin/env bash
INPUT=$(cat)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

if echo "$COMMAND" | grep -E '\brm\s+-rf\b' >/dev/null; then
  echo "Policy gate: rm -rf is blocked." >&2
  exit 2
fi

if echo "$COMMAND" | grep -E '\bgit\s+push\s+.*--force\b' >/dev/null; then
  echo "Policy gate: force push is blocked." >&2
  exit 2
fi

exit 0
SH

cat > .claude/hooks/scope-gate.sh <<'SH'
#!/usr/bin/env bash
INPUT=$(cat)
TARGET=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""')
TARGET=${TARGET//\\//}

case "$TARGET" in
  "")
    exit 0
    ;;
  *src/*|*test/*|*scripts/*|*.claude/*|*.github/*|*README.md|*package.json|*tsconfig.json|*STATE.md|*ARCHITECTURE.md)
    exit 0
    ;;
  *)
    echo "Scope gate: writes outside src/, test/, scripts/, .claude/, .github/ blocked. Target: $TARGET" >&2
    exit 2
    ;;
esac
SH

chmod +x .claude/hooks/policy-gate.sh .claude/hooks/scope-gate.sh
```

Three details in `scope-gate.sh` are load-bearing, and each one is a bug the first draft of this lab shipped:

- `TARGET=${TARGET//\\//}` rewrites backslashes to forward slashes. Claude passes the Write tool an **absolute** path, and on Windows that path looks like `C:\repo\cli-utils\src\slugify.ts`. Without this line no pattern matches, control falls to the deny branch, and the gate blocks every legitimate write while looking like it works.
- The allow patterns start with `*`, not `*/`, so both `/repo/src/a.ts` and a bare relative `src/a.ts` match.
- The empty case is tested first so a payload with no path is allowed through rather than denied.

A policy gate that silently fails open (or, as here, fails closed on every write) is worse than no gate at all. Test it before you trust it.

**Windows and Git:** `chmod +x` does not survive `git add` on Windows, Git records mode `100644` and the ubuntu runner then cannot execute the scripts. Set the bit in the index explicitly and pin the line endings:

```bash
printf '*.sh text eol=lf\n' > .gitattributes
git update-index --chmod=+x .claude/hooks/policy-gate.sh .claude/hooks/scope-gate.sh
```

Run those after the files are staged in Step 3. Without `.gitattributes`, Git rewrites the heredoc-written `.sh` files to CRLF on the next checkout and `#!/usr/bin/env bash` stops resolving in Git Bash.

**Expected result:** Two hook scripts and a `settings.json` entry. Restart Claude Code (`/exit` then `claude`) so the new hook config is loaded.

---

## Step 2: Verify the Gate Locally

**Goal:** Confirm both hooks fire and block the dangerous tool call before it executes.

**Prompt:**

```text
Run `rm -rf /tmp/cli-utils-test` to clean up a test directory.
```

Then:

```text
Write a new file at /etc/cli-utils-config.json with some example config.
```

**Expected result:** Both attempts are blocked. Claude's reply quotes the hook's own stderr, for example `PreToolUse:Bash hook error: [.claude/hooks/policy-gate.sh]: Policy gate: rm -rf is blocked.`, then asks you for a different approach. The model never runs the forbidden command.

There is no `.claude/logs/` directory, Claude Code does not create one. Two things do show you the block:

```bash
claude --debug hooks -p "Run rm -rf /tmp/cli-utils-test"
claude -p --output-format json "Run rm -rf /tmp/cli-utils-test" | jq '.permission_denials'
```

The first traces hook matching and exit codes; the second returns a populated `permission_denials` array containing the blocked `tool_input`.

Test the happy path to confirm legitimate work still passes:

```text
Add a JSDoc comment to the slugify function in src/slugify.ts.
```

This succeeds. The scope-gate receives the **absolute** path Claude resolved (`/repo/cli-utils/src/slugify.ts`, or `C:\repo\cli-utils\src\slugify.ts` on Windows), the separator normalization turns the Windows form into `C:/repo/cli-utils/src/slugify.ts`, `*src/*` matches, and the hook exits 0.

To exercise the gate without burning tokens, feed it a PreToolUse payload directly. Build the JSON with `jq -n` rather than `echo`, so the backslashes in a Windows path survive intact:

```bash
jq -n '{tool_name:"Write",tool_input:{file_path:"C:\\repo\\src\\a.ts",content:"x"}}' | ./.claude/hooks/scope-gate.sh; echo "exit=$?"
jq -n '{tool_name:"Write",tool_input:{file_path:"/etc/passwd",content:"x"}}' | ./.claude/hooks/scope-gate.sh; echo "exit=$?"
jq -n '{tool_name:"Bash",tool_input:{command:"rm -rf /tmp/x"}}' | ./.claude/hooks/policy-gate.sh; echo "exit=$?"
```

The first prints `exit=0`, the second and third print `exit=2` with their deny message. If a hook ever receives JSON it cannot parse, `jq -r` yields an empty string and the gate exits 0, so a malformed payload fails open: another reason to test with real payloads. [02-cicd/hooks-solution/test-hooks.sh](02-cicd/hooks-solution/test-hooks.sh) runs 24 such cases in one go.

---

## Step 3: GitHub Actions Workflow That Reviews PRs

**Goal:** Run Claude on every pull request and post a review comment with what it found. This is the headless mode from Lab 01 turned into a CI gate.

**Command:**

Create the workflow:

```bash
mkdir -p .github/workflows
cat > .github/workflows/claude-review.yml <<'YML'
name: Claude PR review

on:
  pull_request:
    types: [opened, synchronize]

permissions:
  contents: read
  pull-requests: write

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
        with:
          fetch-depth: 0
          ref: ${{ github.event.pull_request.head.sha }}

      - name: Install Claude Code
        run: npm install -g @anthropic-ai/claude-code

      - name: Get PR diff
        id: diff
        run: |
          git diff origin/${{ github.event.pull_request.base.ref }}...HEAD > /tmp/pr.diff
          echo "diff_size=$(wc -c < /tmp/pr.diff)" >> $GITHUB_OUTPUT

      - name: Run Claude review
        if: steps.diff.outputs.diff_size != '0'
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          claude -p --max-turns 3 --allowed-tools "Read,Bash(git:*)" "Review the diff at /tmp/pr.diff. Focus on: type safety, missing tests, unsafe error handling. Output a brief markdown review with 'Issues' and 'Suggestions' sections. End with a one-line verdict: APPROVE, REQUEST_CHANGES, or COMMENT." > /tmp/review.md

      - name: Post review comment
        if: steps.diff.outputs.diff_size != '0'
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: gh pr comment ${{ github.event.pull_request.number }} --body-file /tmp/review.md
YML
```

`gh` is preinstalled on `ubuntu-latest` runners, but it only authenticates when `GH_TOKEN` is present, which is why the comment step sets it. `pull-requests: write` is exactly the scope `gh pr comment` needs.

Add the `ANTHROPIC_API_KEY` secret (this needs a GitHub account and a key you pay for):

```bash
gh secret set ANTHROPIC_API_KEY
```

Commit and push:

```bash
git add .github .claude .gitattributes
git update-index --chmod=+x .claude/hooks/policy-gate.sh .claude/hooks/scope-gate.sh
git commit -m "ci: add Claude PR review workflow + policy hooks"
git push
```

**Expected result:** The workflow file is committed to the default branch and the repo's Actions tab shows the workflow registered. `git ls-files --stage .claude/hooks` reports mode `100755` for both scripts. The `ANTHROPIC_API_KEY` secret is set.

---

## Step 4: Trigger the Workflow With a Small PR

**Goal:** Open a small PR and watch Claude comment on it.

**Commands:**

```bash
git checkout -b feat/uppercase-helper
cat > src/uppercase.ts <<'TS'
export function shout(s: string): string {
  return s.toUpperCase() + "!";
}
TS

git add src/uppercase.ts
git commit -m "feat: add shout helper"
git push -u origin feat/uppercase-helper
gh pr create --title "feat: add shout helper" --body "Adds a trivial uppercase helper."
```

Watch the workflow run:

```bash
gh run watch
```

When it finishes:

```bash
gh pr view --comments
```

**Expected result:** A comment from `github-actions[bot]` on the PR with a markdown review. What it flags depends on the model and your diff; a missing test file for `shout` is the usual first hit, and the one-line verdict at the bottom reads `REQUEST_CHANGES` or `COMMENT`. The agentic CI loop is now live: every PR gets a first-pass review.

You are still on `feat/uppercase-helper` after this step. Lab 03 needs you back on the default branch, it says so in its own setup.

---

## Step 5: Run the Same Task Through Codex CLI

**Goal:** Get a felt sense of OpenAI's Codex CLI by running the exact task Claude just did. Same prompt, different agent.

**Commands:**

Install Codex CLI. The installer OpenAI documents is the standalone script; the npm package still publishes if you prefer that route:

```bash
curl -fsSL https://chatgpt.com/codex/install.sh | sh
codex --version
```

```bash
npm install -g @openai/codex
```

Both are **global installs**, they write outside this project. Skip this step if you would rather not.

Authenticate. Codex reads `OPENAI_API_KEY`, or run `codex login` for browser-based auth. The variable lives only in the shell you set it in:

```bash
export OPENAI_API_KEY=...
```

```powershell
$env:OPENAI_API_KEY = '...'
```

Then run the same review task locally. Replace `main` with your default branch name from the Setup step if `git init` gave you `master`:

```bash
git diff origin/main...HEAD > /tmp/pr.diff
codex exec "Review the diff at /tmp/pr.diff. Focus on: type safety, missing tests, unsafe error handling. Output a brief markdown review with 'Issues' and 'Suggestions' sections. End with a one-line verdict: APPROVE, REQUEST_CHANGES, or COMMENT." > /tmp/review-codex.md
cat /tmp/review-codex.md
```

**Expected result:** A review of the same diff from Codex, billed to your OpenAI account. Compare it against the Claude review on the PR and note the differences in tone, structure, and what each agent prioritised.

---

## Step 6: Run the Same Task Through Aider

**Goal:** Round out the comparison with Aider, another popular agentic CLI with a different design philosophy (diff-based pair programming, deep git integration).

**Commands:**

Install Aider. `pipx` is the safer path because it isolates the install:

```bash
pipx install aider-chat
```

The `pip` route also works, but on any PEP 668 managed Python (most Linux distros, Homebrew Python) it aborts with `externally-managed-environment` unless you are inside a virtualenv:

```bash
python -m venv .venv-aider && source .venv-aider/bin/activate
python -m pip install aider-install
aider-install
```

Aider needs a model key of its own. The `OPENAI_API_KEY` you exported in Step 5 carries over only if you are still in that same shell.

Run the same task:

```bash
aider --no-auto-commits --message "Review the changes in this branch versus main. Focus on: type safety, missing tests, unsafe error handling. Output a brief markdown review with 'Issues' and 'Suggestions' sections. End with a one-line verdict: APPROVE, REQUEST_CHANGES, or COMMENT. Do not modify any files." > /tmp/review-aider.md 2>&1
cat /tmp/review-aider.md
```

**Expected result:** Aider's review, billed to whichever provider key it picked up. Aider is unusual in that it loads the whole repo's diff versus the default branch rather than a flat diff file, so its review tends to be more contextual but slower.

---

## Step 7: Three-Way Comparison

**Goal:** Tabulate what you learned across the three agents.

**Command:**

The Claude review only ever existed inside the runner, so pull it down from the PR first:

```bash
gh pr view --comments --json comments --jq '.comments[-1].body' > /tmp/review.md
```

**Prompt** (back in Claude Code):

```text
Read /tmp/review.md, /tmp/review-codex.md, and /tmp/review-aider.md.

Produce comparison.md at the repo root with this table:

  | Agent | Issues found | Style | Strengths on this task | Weaknesses on this task | Cost per run | Best fit |
  |---|---|---|---|---|---|---|
  | Claude Code (-p) | | | | | | |
  | Codex CLI (exec) | | | | | | |
  | Aider | | | | | | |

Then write a "When I'd reach for each" section with one sentence per agent.
```

**Expected result:** A `comparison.md` filled in with concrete observations from the three runs. The pattern that usually emerges: Claude Code is strongest at structured prompts with tools, Codex is faster and more terse, and Aider shines when you actually want it to make the changes interactively rather than act as a one-shot CI reviewer.

---

## What You Just Practised

| Mechanic | Step | What it gives you |
|---|---|---|
| `PreToolUse` hook for Bash | 1, 2 | Block destructive commands before they run |
| `PreToolUse` hook for Write/Edit | 1, 2 | Scope writes to allowed directories |
| Path normalization in a hook | 1, 2 | A gate that holds on Windows instead of denying everything |
| GitHub Actions running `claude -p` | 3 | First-pass review on every PR |
| `--max-turns` and `--allowed-tools` | 3 | Cost cap and no permission prompts in CI |
| Headless agent-CLI comparison | 5, 6, 7 | Honest read on when Claude is or is not the right tool |

`--allowed-tools` pre-approves tools so CI never blocks on a prompt; it does not restrict which tools exist. The flags that actually restrict are `--tools` (limits the available set) and `--permission-mode dontAsk` (denies anything not pre-approved instead of asking). Reach for those when the runner is untrusted.

[Lab 03](lab-03-always-on-and-fleet.md) takes the agentic-CLI mechanics further into always-on territory: persistent sessions, OS schedulers, Ralph Wiggum loops, scheduled GitHub Actions, and a parallel-worktree fleet.
