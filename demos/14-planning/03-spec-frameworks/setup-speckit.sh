#!/usr/bin/env bash

# $0 is this script's own path, so the topic folder resolves from any working directory
TOPIC_DIR=$(cd "$(dirname "$0")" && pwd)
# ${1:-...} takes the first argument if given, and the default sits outside the checkout because spec kit initialises its own git repo
RUN_DIR=${1:-$HOME/spec-runs/notes-cli-speckit}

mkdir -p "$(dirname "$RUN_DIR")"
# || copies only when the run folder is missing, so a second run keeps the work from the first
[ -d "$RUN_DIR" ] || cp -r "$TOPIC_DIR/notes-cli" "$RUN_DIR"

if command -v uv > /dev/null; then
  uv tool install --force specify-cli --from git+https://github.com/github/spec-kit.git
else
  pipx install --force git+https://github.com/github/spec-kit.git
fi

cd "$RUN_DIR"
# --force lets init run in a folder that already holds the copied starter
specify init . --integration claude --script sh --force

echo "Spec Kit ready in $RUN_DIR"
echo "Start the demo with: cd $RUN_DIR && claude"
