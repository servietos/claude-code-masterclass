#!/usr/bin/env bash

# first argument, or tasks.txt when the script is called without one
TASKS_FILE="${1:-tasks.txt}"
REPO=$(git rev-parse --show-toplevel)
# the path of this folder inside the repository, so each worktree can cd to the same place
DEMO_DIR=$(git rev-parse --show-prefix)
LOGS="$PWD/logs"

mkdir -p "$LOGS"

slugs=()
pids=()

# IFS='|' splits each task line into a slug and a task description
while IFS='|' read -r slug desc; do
  [ -z "$slug" ] && continue

  WORKTREE="$REPO/../wt-$slug"
  echo "Creating worktree $WORKTREE on feat/$slug"
  git worktree add "$WORKTREE" -b "feat/$slug"

  # 2>&1 folds stderr into the per-agent log, & starts the session in the background
  (
    cd "$WORKTREE/$DEMO_DIR"
    claude -p "$desc" \
      --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" \
      --max-turns 8
  ) > "$LOGS/log-$slug.txt" 2>&1 &

  slugs+=("$slug")
  # $! is the process id of the background job just started
  pids+=($!)
done < "$TASKS_FILE"

echo "Launched ${#pids[@]} agents, waiting..."

failed=()
for i in "${!pids[@]}"; do
  # waiting on a known pid yields that agent's exit code instead of the last one to finish
  wait "${pids[$i]}"
  code=$?
  if [ "$code" -ne 0 ]; then
    failed+=("${slugs[$i]} (exit $code)")
  fi
done

remove_worktrees() {
  for slug in "${slugs[@]}"; do
    git worktree remove "$REPO/../wt-$slug" --force
  done
  git worktree prune
}

# one failed agent stops the merge, so a half-finished fan-out never lands on the branch
if [ "${#failed[@]}" -ne 0 ]; then
  echo "Agents failed, skipping merge:"
  printf '  %s\n' "${failed[@]}"
  remove_worktrees
  echo "Branches kept for inspection: $(printf 'feat/%s ' "${slugs[@]}")"
  exit 1
fi

echo "All agents succeeded, merging..."
for slug in "${slugs[@]}"; do
  # --no-ff keeps one merge commit per agent, so each lane stays visible in the history
  if ! git merge --no-ff "feat/$slug" -m "Merge feat/$slug"; then
    echo "Conflict merging feat/$slug, aborting"
    git merge --abort
    remove_worktrees
    echo "Branches kept for inspection: $(printf 'feat/%s ' "${slugs[@]}")"
    exit 1
  fi
done

echo "Cleaning up..."
remove_worktrees
for slug in "${slugs[@]}"; do
  # lowercase -d refuses to delete a branch that was never merged
  git branch -d "feat/$slug"
done

git log --oneline --graph -10
