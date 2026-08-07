#!/usr/bin/env bash

# $0 is this script's own path, so the topic folder resolves from any working directory
TOPIC_DIR=$(cd "$(dirname "$0")" && pwd)
# ${1:-...} takes the first argument if given, and the default sits outside the checkout because bmad installs its own git repo
RUN_DIR=${1:-$HOME/spec-runs/notes-cli-bmad}

mkdir -p "$(dirname "$RUN_DIR")"
# || copies only when the run folder is missing, so a second run keeps the work from the first
[ -d "$RUN_DIR" ] || cp -r "$TOPIC_DIR/notes-cli" "$RUN_DIR"

cd "$RUN_DIR"
npx --yes bmad-method install --directory . --modules bmm --tools claude-code --yes

echo "BMAD ready in $RUN_DIR"
echo "Start the demo with: cd $RUN_DIR && claude"
