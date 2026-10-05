# Run Two Claude Sessions Without Them Colliding

A git worktree gives each session its own checkout while both share one history, which is what makes parallel work safe. You create one by hand and one with `claude --worktree`, let two sessions edit the same file at once, then review and clean up what each produced. You finish holding two reviewable branches, a working copy that never moved, and the git commands that make worktrees safe to use daily.

------

## Prerequisites

- Claude Code v2.1.139 or later. Check with `claude --version`; this guide was verified on 2.1.220.
- Git 2.5 or later, and a terminal you can open three times.
- Bash or PowerShell 7. Every `git` and `claude` command below is identical in both; the two places where the shell's own commands differ give both versions.

## Setup

There is none. This course repository is a git repository, which is the only prerequisite a worktree has, so every command below runs from the repository root.

The file you will edit is `demos/01-fundamentals/06-git-worktrees/worktree-sandbox/app.js`. It is small and nothing depends on it, which makes it a safe target for two sessions to fight over. Every edit lands on a branch, never on your checkout, and Step 6 deletes all of them.

Where an output block shows an absolute path, `<repo>` stands in for wherever you cloned this repository.

## Step 1: Watch git create a second working tree

A worktree is a second checkout of the same repository living at its own path. Both directories share one `.git` object store, so history, branches, and remotes are common, but the files on disk are independent. This is the whole reason parallel work is safe: two directories, one history.

Create one by hand first, so the mechanic is visible before Claude does it for you.

```bash
git worktree add .claude/worktrees/scratch -b scratch
git worktree list
```

Expected output:

```text
<repo>                            4e88f4c [master]
<repo>/.claude/worktrees/scratch  4e88f4c [scratch]
```

Two entries, one repository. Look at what git put inside the new directory. Hidden files matter here, so list them explicitly.

Bash:

```bash
ls -a .claude/worktrees/scratch
```

PowerShell:

```powershell
Get-ChildItem -Force .claude/worktrees/scratch
```

Expected output: the full contents of this repository, plus a `.git` entry. That `.git` is a file, not a directory. It holds a single line pointing back at the real repository, which is why a second checkout of a large repo costs almost nothing on disk.

Remove it again before continuing, and note that removing a worktree leaves its branch behind:

```bash
git worktree remove .claude/worktrees/scratch
git branch -D scratch
```

Expected result: `git worktree list` prints one line again, and `git branch` no longer lists `scratch`.

## Step 2: Start a Claude session in its own worktree

Pass `--worktree` (or `-w`) with a name and Claude Code creates the worktree for you, then starts the session inside it. The default location is `.claude/worktrees/<name>/` at your repository root, on a new branch named `worktree-<name>`, branched from your repository's default branch. You never run `git worktree add` yourself.

From the repository root:

```bash
claude --worktree feature-auth
```

Inside the session, give it a task:

```text
In demos/01-fundamentals/06-git-worktrees/worktree-sandbox/, add a file called auth.js exporting a function login(user) that returns true.
```

The status line at the bottom of the session now reads `worktree-feature-auth` instead of `master`. Leave this session running and open a second terminal at the repository root:

```bash
git worktree list
git status --short
```

Expected output:

```text
<repo>                                 4e88f4c [master]
<repo>/.claude/worktrees/feature-auth  4e88f4c [worktree-feature-auth] locked
```

```text
```

Two things worth reading carefully. The worktree is marked `locked`, which Claude Code sets while the session is alive so a cleanup sweep cannot delete work in progress. And `git status` is completely empty: `auth.js` exists in the worktree and nowhere near your checkout, and `.claude/worktrees/` is gitignored so the worktree itself is invisible here too.

Expected result: `auth.js` exists under `.claude/worktrees/feature-auth/` and nowhere else. `git branch` marks the new branch with a `+`, which is git's notation for a branch checked out in another worktree.

## Step 3: Run two sessions in parallel and prove they cannot collide

One isolated session is convenient. Two sessions editing the same file at the same time is the point. Start a second worktree session in a third terminal, from the repository root:

```bash
claude --worktree hotfix-greet
```

Give it a task that touches a file the first session can also see:

```text
In demos/01-fundamentals/06-git-worktrees/worktree-sandbox/, edit app.js so the greeting template ends with an exclamation mark. Do not commit.
```

Now compare all three copies of `app.js` from your checkout. The paths are long, so set a variable for the part they share:

Bash:

```bash
S=demos/01-fundamentals/06-git-worktrees/worktree-sandbox
cat $S/app.js
cat .claude/worktrees/hotfix-greet/$S/app.js
ls .claude/worktrees/feature-auth/$S
```

PowerShell:

```powershell
$S = "demos/01-fundamentals/06-git-worktrees/worktree-sandbox"
Get-Content "$S/app.js"
Get-Content ".claude/worktrees/hotfix-greet/$S/app.js"
Get-ChildItem ".claude/worktrees/feature-auth/$S"
```

Expected output:

```text
export function greet(name) {
  return `Hello, ${name}`
}
```

```text
export function greet(name) {
  return `Hello, ${name}!`
}
```

```text
app.js  auth.js  README.md
```

Three working trees, three different file states, one repository. The hotfix session changed `app.js` and the feature session did not; the feature session added `auth.js` and the hotfix session cannot see it. Your own checkout is untouched, which `git status --short` confirms by printing nothing at all.

Confirm git agrees:

```bash
git worktree list
```

Expected output:

```text
<repo>                                 4e88f4c [master]
<repo>/.claude/worktrees/feature-auth  4e88f4c [worktree-feature-auth] locked
<repo>/.claude/worktrees/hotfix-greet  4e88f4c [worktree-hotfix-greet] locked
```

Expected result: two locked worktrees on two branches, both branched from the same commit, neither able to write into the other.

## Step 4: Send a task to the background and watch it isolate itself

You do not have to ask for a worktree. A background session creates one on its own before it edits any file, which is what makes it safe to dispatch several at once. Exit or background your interactive sessions, then dispatch from the repository root:

```bash
claude --bg "In demos/01-fundamentals/06-git-worktrees/worktree-sandbox/, create NOTES.md with three bullet points about git worktrees. Commit it with the message 'docs: add NOTES.md'."
```

The command returns a short session ID and keeps working without holding your terminal. What this step tests is where the edits went. Once it finishes:

```bash
git worktree list
git status --short
git log --oneline --all
```

Expected output:

```text
<repo>                              4e88f4c [master]
<repo>/.claude/worktrees/notes-md   1e87867 [worktree-notes-md] locked
```

```text
```

```text
1e87867 docs: add NOTES.md
4e88f4c chore: update models and presentation materials
```

Claude named the worktree `notes-md` from the task itself and committed there. The commit is visible from your checkout through `--all`, but no file changed in your working directory and `git status` is still empty.

Expected result: a new branch carrying one commit, a locked worktree under `.claude/worktrees/`, and a clean `git status`.

## Step 5: Review a branch without checking it out

Reviewing is ordinary git. You do not enter the worktree and you do not switch branches; you read the diff from where you are standing, even though the branch is checked out somewhere else.

```bash
git diff --stat master..worktree-notes-md
git show worktree-notes-md:demos/01-fundamentals/06-git-worktrees/worktree-sandbox/NOTES.md
```

Expected output:

```text
 demos/01-fundamentals/06-git-worktrees/worktree-sandbox/NOTES.md | 7 +++++++
 1 file changed, 7 insertions(+)
```

```text
# Notes

## Git worktrees

- A worktree lets one repository have several working directories checked out at once, each on its own branch, all sharing a single `.git` object store and history.
- `git worktree add ../feature-x feature-x` creates one; `git worktree list` shows them all, and `git worktree remove ../feature-x` cleans one up (`git worktree prune` clears stale entries).
- A branch can only be checked out in one worktree at a time, which makes worktrees a safe way to run a build, review a PR, or hotfix in parallel without stashing or disturbing the main working copy.
```

`git show <branch>:<path>` reads a file straight out of another branch without checking anything out, which is the fastest way to review a background session's work.

In your own project this is the moment you would accept the work with `git merge --no-ff worktree-notes-md`. Do not run it here: this is the course repository, and these three branches are demo output. Step 6 deletes them instead.

Expected result: a one-file diff and the file's full contents, read without leaving `master`.

## Step 6: Clean up, and the two errors that block it

Removal refuses in two different situations, and each prints a different error. That is the safety net, so trigger both deliberately.

```bash
git worktree remove .claude/worktrees/hotfix-greet
```

Expected output:

```text
fatal: cannot remove a locked working tree, lock reason: claude session hotfix-greet (pid 55268 start 639206594865118980)
use 'remove -f -f' to override or unlock first
```

The lock is Claude Code protecting a running agent. Release it, then remove:

```bash
git worktree unlock .claude/worktrees/hotfix-greet
git worktree remove .claude/worktrees/hotfix-greet
```

The second condition is unfinished work. The `feature-auth` worktree still holds the untracked `auth.js`:

```bash
git worktree unlock .claude/worktrees/feature-auth
git worktree remove .claude/worktrees/feature-auth
```

Expected output:

```text
fatal: '.claude/worktrees/feature-auth' contains modified or untracked files, use --force to delete it
```

Git will not silently discard work. Once you have decided the changes are disposable, force it, then remove the last worktree and all three branches:

```bash
git worktree remove --force .claude/worktrees/feature-auth
claude stop <id>
git worktree unlock .claude/worktrees/notes-md
git worktree remove --force .claude/worktrees/notes-md
git branch -D worktree-feature-auth worktree-hotfix-greet worktree-notes-md
```

Replace `<id>` with the session ID Step 4 printed, and clear it from the board with `claude rm <id>`.

Expected result: `git worktree list` shows one line, `git branch` lists only the branches you started with, and `git status --short` prints nothing.

## Carry your local files into the next worktree

One more thing surprises people on their first real project. A worktree is a fresh checkout, so gitignored files such as `.env` are absent and the app fails to start in it. List them in a `.worktreeinclude` at the repository root, using `.gitignore` syntax, and Claude Code copies them into every worktree it creates:

```text
.env
.env.local
config/secrets.json
```

Only files that match a pattern and are also gitignored are copied, so tracked files are never duplicated.

## Verify

You have demonstrated worktrees if all four hold:

- `git worktree list` showed three entries at once in Step 3, each on its own branch.
- `app.js` had different contents in your checkout and in the `hotfix-greet` worktree at the same moment.
- A `--bg` session committed to a branch you never checked out, while `git status` in your checkout stayed empty throughout.
- `git worktree remove` refused twice, once for a lock and once for untracked files, and you resolved each with the matching command.

