#!/usr/bin/env bash
INPUT=$(cat)
TARGET=$(echo "$INPUT" | jq -r '.tool_input.file_path // .tool_input.path // ""')
TARGET=${TARGET//\\//}

case "$TARGET" in
  "")
    exit 0
    ;;
  *src/*|*test/*|*scripts/*|*.claude/*|*.github/*|*README.md|*package.json|*tsconfig.json|*STATE.md|*ARCHITECTURE.md)
    exit 0
    ;;
  *)
    echo "Scope gate: writes outside src/, test/, scripts/, .claude/, .github/ blocked. Target: $TARGET" >&2
    exit 2
    ;;
esac
