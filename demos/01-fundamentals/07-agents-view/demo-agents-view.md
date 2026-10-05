# Dispatch and Triage a Fleet of Background Sessions

The agents view is a board for supervising many background sessions instead of waiting on one task at a time. You decide which chores actually split cleanly, dispatch three of them, then triage the board, unblock the session that stalls, and review each branch without checking it out. You finish with three reviewable branches, a cleared board, and the knowledge of which delete operation destroys uncommitted changes and which one refuses to.

---

## Demo Files

There is no setup. This course repository is already a git repository, which is all a background session needs to isolate itself, so every command below runs from the repository root.

The work happens in `demos/01-fundamentals/07-agents-view/agents-sandbox/`: three small modules, each carrying one independent chore, and nothing depends on any of them. Every edit lands on its own branch, never on your checkout, and Step 5 deletes all of them.

| File | What it represents |
|------|--------------------|
| `src/greet.js` | Undocumented exports, the chore for session one |
| `src/parse.js` | Unvalidated input, the chore for session two |
| `src/format.js` | Untested code, the chore for session three |

Run `claude` once in the sandbox and accept the workspace trust dialog before dispatching anything.

---

## Step 1: Decide What Is Actually Worth Parallelising

Overview: Fanning out is not free. Ten sessions cost roughly ten times the quota of one, and two sessions editing the same file produce a merge conflict you now have to resolve twice over. The judgement that makes the agents view useful is deciding which work splits cleanly before you dispatch anything.

Research / Planning / Discussion:

```text
Read every file under src/ in this repository.

I want to run several Claude sessions in parallel on this codebase. Tell me
which chores here are genuinely independent and which would collide, and say
what "collide" means concretely in each case: same file, same function, or a
shared contract one change would break for the other.

Then tell me which chores are not worth a separate session at all. Do not
change any files yet.
```

Finding: A useful answer names the file each chore touches and points out that a change to `parse.js` validation could alter the contract `format.js` tests rely on, even though they are separate files. Push back if the response only counts files: independence is about the blast radius of a change, not its location. If it recommends parallelising something a single session would finish faster, that is the right instinct and worth keeping.

Recipe:

```text
Write a dispatch plan for three background sessions against this repository.
Each session gets exactly one chore, and no two sessions may write to the same
file.

Session 1: add JSDoc comments to every export in src/greet.js
Session 2: add input validation to parseDuration in src/parse.js so malformed
           input throws a clear Error instead of a TypeError
Session 3: create src/format.test.js covering formatBytes

For each, give me the exact `claude --bg --name "..." "..."` command with a
short session name and a prompt that ends by committing the change. Output the
three commands in a copy-paste block and nothing else.
```

Expected Outcome: three `claude --bg --name` commands, each naming one file, each ending with a commit instruction. Read them before running: a prompt that does not say "commit" leaves the work uncommitted in a worktree, which changes how you have to clean up later.

---

## Step 2: Dispatch the Fleet

Overview: A background session returns your terminal immediately and keeps working. This step turns the plan into three running sessions and shows what the dispatch actually hands back to you.

Research / Planning / Discussion:

```text
Before I dispatch background sessions, explain what happens to my working
directory while they run.

1. Where do the file edits land, and why not in my checkout?
2. What does the short ID printed at dispatch let me do afterwards?
3. What happens to a session if I close this terminal?

One or two sentences each.
```

Finding: The answer should place edits in an isolated worktree under `.claude/worktrees/`, explain that a separate supervisor process owns the sessions so closing the terminal does not stop them, and name `attach`, `logs`, and `stop` as what the ID unlocks. If it claims the session dies with the terminal, that is wrong and worth correcting before you rely on it.

Recipe: run the three commands from Step 1 at the repository root. Each names its target with a full path, because a background session starts at the root just as you do:

Bash:

```bash
S=demos/01-fundamentals/07-agents-view/agents-sandbox
claude --bg --name "jsdoc-greet" "Add JSDoc comments to every export in $S/src/greet.js. Commit with the message 'docs: document greet exports'."
claude --bg --name "validate-parse" "Add input validation to parseDuration in $S/src/parse.js so malformed input throws a clear Error. Commit with the message 'fix: validate parseDuration input'."
claude --bg --name "test-format" "Create $S/src/format.test.js with tests covering formatBytes. Commit with the message 'test: cover formatBytes'."
```

PowerShell:

```powershell
$S = "demos/01-fundamentals/07-agents-view/agents-sandbox"
claude --bg --name "jsdoc-greet" "Add JSDoc comments to every export in $S/src/greet.js. Commit with the message 'docs: document greet exports'."
claude --bg --name "validate-parse" "Add input validation to parseDuration in $S/src/parse.js so malformed input throws a clear Error. Commit with the message 'fix: validate parseDuration input'."
claude --bg --name "test-format" "Create $S/src/format.test.js with tests covering formatBytes. Commit with the message 'test: cover formatBytes'."
```

Each command returns straight away and prints a block like this. It is output, not something to type:

```text
backgrounded · 7c5dcf5d
  claude agents             list sessions
  claude attach 7c5dcf5d    open in this terminal
  claude logs 7c5dcf5d      show recent output
  claude stop 7c5dcf5d      stop this session
```

The first line confirms the session was backgrounded and gives it a short ID, `7c5dcf5d` here. The four indented lines are a reminder card: every command you might want later, already filled in with that session's ID so you never have to look it up. Yours will differ, and you will use `claude logs` and `claude stop` in the steps below.

Expected Outcome: three short session IDs, returned within a second or two of each other. Run `git status --short` at the repository root and confirm it prints nothing: none of the three sessions has touched a file in your checkout, and `.claude/worktrees/` is gitignored.

---

## Step 3: Triage the Board Without Attaching

Overview: The board earns its keep when you stop opening sessions to find out what they are doing. Peeking, replying, and dispatching all happen from the list, and attaching becomes the exception rather than the routine.

Research / Planning / Discussion:

```text
I have three background sessions running. Before I open the agents view,
explain the difference between these session states and what each one is
asking of me: Working, Needs input, Ready for review, Completed, Failed.

Then tell me which of them I should act on first and why.
```

Finding: A good answer puts Needs input first, because a blocked session burns wall-clock time doing nothing while the others finish. It should distinguish Ready for review (finished, waiting on your judgement) from Completed (finished and closed out). If the response treats every state as equally urgent, it has missed the point of the grouping.

Recipe: open the board and work it from the keyboard.

```bash
claude agents
```

Then, without attaching to anything:

1. Press `Space` on the top row to open the peek panel and read the session's latest output.
2. Press `↓` and `↑` to peek the neighbouring sessions.
3. If a session sits in Needs input, answer it from the peek panel: type a reply and press `Enter`, or press the number key matching a choice it offered.
4. Press `Ctrl+S` to regroup by directory, then `Ctrl+S` again to return to grouping by state.
5. Press `Esc` to close the panel.

Expected Outcome: all three sessions reach Ready for review or Completed without you attaching to any of them. A session that stalls in Needs input is almost always a permission prompt, and answering it from the peek panel is the whole skill this step teaches. For a scriptable view of the same state:

```bash
claude agents --json
```

```json
{
  "id": "7c5dcf5d",
  "kind": "background",
  "name": "jsdoc-greet",
  "status": "busy",
  "state": "working"
}
```

---

## Step 4: Review Three Branches Without Checking Any Out

Overview: Each session committed to its own branch. Reviewing them means reading three diffs from where you are standing, not checking out three branches in turn and losing your place each time.

Research / Planning / Discussion:

```text
Three background sessions each committed to their own branch in this
repository, and I am still on master.

Show me how to list those branches and see what each one changed relative to
master, without checking out a single branch. Give the exact commands and say
what each shows me that the others do not.
```

Finding: Expect `git branch --list` and `git diff master..<branch>`. If the answer proposes `git checkout` for any part of the review, push back: it defeats the isolation and puts you back where you started. Reading a whole file straight out of a branch with `git show` is [06: Git Worktrees](../06-git-worktrees/demo-worktrees-intro.md#step-5-review-a-branch-without-checking-it-out) Step 5, and works here unchanged.

Recipe:

```bash
git branch --list "worktree-*"
git diff --stat master..worktree-validate-parse
```

Read the validation change closely. It is the one chore of the three whose implementation is a judgement call rather than a mechanical edit, and it is the one most likely to have solved a slightly different problem than you asked for.

Expected Outcome: three branches listed, each carrying exactly one commit, and a diff that touches exactly one file. Repeat the `git diff --stat` against the other two branches; if any of them touches a file another branch also touched, your Step 1 plan was wrong about independence, which is worth knowing now rather than at merge time.

---

## Step 5: Clear the Board Without Losing Work

Overview: Deleting a session is not a tidy-up, it is a destructive operation with two different behaviours depending on how you do it. This step teaches the difference, then closes the board out.

Research / Planning / Discussion:

```text
I am about to delete finished sessions from the agents view.

Tell me exactly what is destroyed in each case, and what survives:

1. Pressing Ctrl+X twice on a row in the agents view
2. Running `claude rm <id>` from the shell
3. A worktree holding uncommitted changes, under each of the above
4. A worktree holding commits that were never pushed

Be precise about which of these can lose work I cannot recover.
```

Finding: The answer should say that `Ctrl+X` twice removes the worktree along with uncommitted changes in it, while `claude rm` keeps a worktree that still holds uncommitted changes, and that both keep a worktree with unpushed commits. If it treats the two as equivalent, correct it before you use either, because the difference is exactly where unrecoverable work is lost.

Recipe: delete the three sessions two different ways, so you see both behaviours.

```bash
claude agents
```

Delete one row with `Ctrl+X` pressed twice, which takes its worktree and any uncommitted changes with it. Then stop and remove the other two from the shell, which keeps a worktree that still holds uncommitted work:

```bash
claude stop <id>
claude rm <id>
```

Removing whatever worktrees and branches survived is the git cleanup [06: Git Worktrees](../06-git-worktrees/demo-worktrees-intro.md#step-6-clean-up-and-the-two-errors-that-block-it) Step 6 teaches, refusals included:

```bash
git worktree list
git worktree remove --force .claude/worktrees/<name>
git branch -D worktree-jsdoc-greet worktree-validate-parse worktree-test-format
```

Expected Outcome: `claude agents` shows an empty board, `git worktree list` shows only your checkout, and `git branch` lists no `worktree-*` entries.

