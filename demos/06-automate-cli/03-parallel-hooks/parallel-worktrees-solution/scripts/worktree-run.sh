#!/usr/bin/env bash

# repository root and this folder's path inside it, so every agent starts in the same folder of its worktree
REPO=$(git rev-parse --show-toplevel)
DEMO_DIR=$(git rev-parse --show-prefix)
TASKS_FILE=$1
pids=()
slugs=()

mkdir -p logs

while IFS='|' read -r slug desc; do
  slugs+=("$slug")
  # one worktree and one feat/<slug> branch per task, created beside the repository
  git worktree add "$REPO/../wt-$slug" -b "feat/$slug"
  # the agent runs in the background; stdin comes from /dev/null so claude never reads the tasks file
  (
    cd "$REPO/../wt-$slug/$DEMO_DIR"
    claude -p "$desc. Add tests. Commit the result." \
      --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 10
  ) > "logs/log-$slug.txt" 2>&1 < /dev/null &
  # $! is the PID of the background agent, kept so the script can wait on each one
  pids+=($!)
done < "$TASKS_FILE"

failed=0
for pid in "${pids[@]}"; do
  # wait returns the agent's exit code; any non-zero marks the whole run as failed
  wait "$pid" || failed=1
done

remove_worktrees() {
  for slug in "${slugs[@]}"; do
    git worktree remove --force "$REPO/../wt-$slug"
  done
}

if [ "$failed" -ne 0 ]; then
  remove_worktrees
  exit 1
fi

for slug in "${slugs[@]}"; do
  # --no-ff keeps one merge commit per task, so each feature stays visible in history
  if ! git merge --no-ff "feat/$slug"; then
    git merge --abort
    remove_worktrees
    exit 1
  fi
done

remove_worktrees
for slug in "${slugs[@]}"; do
  # -d refuses to delete a branch that is not merged, so only merged feature branches go
  git branch -d "feat/$slug"
done
