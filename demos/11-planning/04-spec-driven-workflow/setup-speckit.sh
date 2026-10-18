#!/usr/bin/env bash

# $0 is this script's own path, so the topic folder resolves from any working directory
TOPIC_DIR=$(cd "$(dirname "$0")" && pwd)
# ${1:-...} takes the first argument if given, and the default sits outside the checkout so the course repo's own CLAUDE.md never loads into the run
RUN_DIR=${1:-$HOME/spec-runs/meeting-cost}

mkdir -p "$(dirname "$RUN_DIR")"
# || copies only when the run folder is missing, so a second run keeps the work from the first
[ -d "$RUN_DIR" ] || cp -r "$TOPIC_DIR/meeting-cost" "$RUN_DIR"

# command -v prints nothing and fails when uv is absent, so this reads as a presence test
if command -v uv > /dev/null; then
  # the version pin matches the recorded outputs; --reinstall replaces an older specify-cli that would otherwise stay put
  uv tool install specify-cli==1.2.1 --reinstall
else
  pipx install --force specify-cli==1.2.1
fi

cd "$RUN_DIR"
# --force lets init run in a folder that already holds the starter, --non-interactive stops it waiting for a keypress
specify init . --integration claude --script sh --force --non-interactive

echo "Spec Kit ready in $RUN_DIR"
echo "Start the demo with: cd $RUN_DIR && claude"
