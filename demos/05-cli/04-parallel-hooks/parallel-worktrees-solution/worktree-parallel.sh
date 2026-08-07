#!/usr/bin/env bash

REPO_ROOT=$(git rev-parse --show-toplevel)
# the path of this folder inside the repository, so each worktree can cd to the same place
DEMO_DIR=$(git rev-parse --show-prefix)
# worktrees are created beside the repository, never inside it
FEAT_A="$REPO_ROOT/../wt-feat-camel"
FEAT_B="$REPO_ROOT/../wt-feat-slug"

echo "Creating worktrees..."
git worktree add "$FEAT_A" -b feat/improve-camel
git worktree add "$FEAT_B" -b feat/improve-slug

echo "Launching parallel Claude sessions..."
# ( ... ) & runs the session in a background subshell, so both agents work at the same time
(
  cd "$FEAT_A/$DEMO_DIR"
  claude -p "Improve src/kebab-to-camel.ts to handle multi-word inputs. Add tests. Commit the result." \
    --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 10
) &

(
  cd "$FEAT_B/$DEMO_DIR"
  claude -p "Improve src/slugify.ts to preserve numbers in slugs. Add tests. Commit the result." \
    --allowed-tools "Read,Edit,Bash(npm:*),Bash(git:*)" --max-turns 10
) &

# block here until both background sessions have exited
wait
echo "Both sessions complete."

echo "Resulting branches:"
git log --all --oneline | head -10

echo "Cleaning up worktrees..."
git worktree remove "$FEAT_A" --force
git worktree remove "$FEAT_B" --force
git branch -D feat/improve-camel feat/improve-slug
