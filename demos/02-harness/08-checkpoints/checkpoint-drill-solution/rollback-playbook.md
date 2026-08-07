# Choose Between an Anchor and a Commit

Checkpoints are session-local undo for files Claude edited with its own tools. Git is permanent history that survives restarts, machines, and reviewers. This playbook decides which one a situation needs before the risky work starts.

## Decision Rule

| Situation | Anchor | Commit | Why |
|-----------|--------|--------|-----|
| A risky refactor I might abandon in the next ten minutes | Yes | No | Pure checkpoint case: the work never has to outlive the session, and `/rewind` restores byte-identical files. |
| A working feature I want to keep across a machine restart | No | Yes | Checkpoints are session state and expire with the session, so only a commit carries the work forward. |
| A migration script that writes to a database | Yes | Yes | The checkpoint covers the script file, but nothing rolls back the rows, so the commit is the only durable record of what ran. |
| A change made partly by Claude and partly by me editing files by hand | No | Yes | Manual edits are outside the checkpoint boundary, so a restore would leave a half-reverted tree. |
| Work I want a colleague to review | No | Yes | Review happens on a branch and a diff, neither of which a checkpoint produces. |

## Before You Start Anything Risky

```text
Before you modify anything, confirm the current state in one sentence: the file list and the test result.
I want to recognise this exact point in the rewind menu later.
```

```text
Run the test suite and report pass and fail counts plus the exit code. Do not change any file.
This run is my baseline for the rollback.
```

```text
List every file you intend to touch for this change, with one line each on why.
Do not edit anything until I confirm the list.
```

## What Checkpoints Never Cover

A restore reverts only the files Claude edited through its file editing tools in this session. Files changed by a bash command Claude ran, your own manual editor changes, database rows, and git history are all outside the boundary. When any of those are in play, commit first and treat the checkpoint as a convenience, not as the safety net.
