# Run Two Claude Sessions Without Them Colliding

A git worktree gives each session its own checkout while both share one history, which is what makes parallel work safe. You create worktrees with `claude --worktree`, let two sessions edit the same file at once, then review what each produced.

------

Run every command from the repository root; the sessions edit `demos/01-fundamentals/04-git-worktrees/worktree-sandbox/`, each result stays on its own `worktree-<name>` branch, and `<repo>` in the output stands for your clone.

## Step 1: Run two sessions in parallel and prove they cannot collide

Pass `--worktree` with a name and Claude Code creates `.claude/worktrees/<name>/` on a new branch named `worktree-<name>`, then starts the session inside it. Start `claude --worktree feature-auth` in one terminal, then a second session in another with `claude --worktree hotfix-greet`, and send the second session this prompt:

```bash
claude --worktree feature-auth
claude --worktree hotfix-greet
```

```text
In demos/01-fundamentals/04-git-worktrees/worktree-sandbox/, edit app.js so the greeting template ends with an exclamation mark. Do not commit.
```

Compare both copies of `app.js` from your checkout, in Bash or PowerShell:

```bash
S=demos/01-fundamentals/04-git-worktrees/worktree-sandbox
cat $S/app.js
cat .claude/worktrees/hotfix-greet/$S/app.js
```

```powershell
$S = "demos/01-fundamentals/04-git-worktrees/worktree-sandbox"
Get-Content "$S/app.js"
Get-Content ".claude/worktrees/hotfix-greet/$S/app.js"
```

```text
export function greet(name) {
  return `Hello, ${name}!`
}
```

Your checkout still returns `Hello, ${name}` while the hotfix worktree carries the exclamation mark, and `git status --short` prints nothing. `git worktree list` marks both worktrees `locked`, which Claude Code sets while the session is alive so a cleanup sweep cannot delete work in progress.

## Step 2: Send a task to the background and watch it isolate itself

A background session creates a worktree on its own before it edits any file, which is what makes it safe to dispatch several at once. Dispatch from the repository root:

```bash
claude --bg "In demos/01-fundamentals/04-git-worktrees/worktree-sandbox/, create NOTES.md with three bullet points about git worktrees. Commit it with the message 'docs: add NOTES.md'."
```

Once it finishes, `git log --oneline --all` shows the commit:

```text
1e87867 docs: add NOTES.md
4e88f4c chore: update models and presentation materials
```

Claude named the worktree `notes-md` from the task itself and committed there, while no file changed in your working directory and `git status --short` stays empty.

## Step 3: Review a branch without checking it out

Reviewing is ordinary git: you read the diff from where you are standing, even though the branch is checked out somewhere else.

```bash
git diff --stat master..worktree-notes-md
git show worktree-notes-md:demos/01-fundamentals/04-git-worktrees/worktree-sandbox/NOTES.md
```

```text
 demos/01-fundamentals/04-git-worktrees/worktree-sandbox/NOTES.md | 7 +++++++
 1 file changed, 7 insertions(+)
```

`git show <branch>:<path>` reads a file straight out of another branch without checking anything out, which is the fastest way to review a background session's work.
