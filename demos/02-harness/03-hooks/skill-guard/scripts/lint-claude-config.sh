#!/bin/bash
# Lint a repo's .claude/{skills,agents} for the defects that silently break
# skill discovery and expert auto-delegation. Project-agnostic, read-only.
#
# Usage: bash lint-claude-config.sh [REPO_ROOT]   (default: current dir)
# Exit:  0 = clean, 1 = issues found.

ROOT="${1:-.}"
CLAUDE_DIR="$ROOT/.claude"
ISSUES=0

note() { echo "  [!] $1"; ISSUES=$((ISSUES+1)); }

if [ ! -d "$CLAUDE_DIR" ]; then
  echo "No .claude directory at: $ROOT"
  exit 0
fi

# --- Skills ---------------------------------------------------------------
SKILLS_DIR="$CLAUDE_DIR/skills"
if [ -d "$SKILLS_DIR" ]; then
  echo "Skills ($SKILLS_DIR):"
  for d in "$SKILLS_DIR"/*/; do
    [ -d "$d" ] || continue
    name=$(basename "$d")
    # find a manifest case-insensitively, capture its real on-disk case
    manifest=$(find "$d" -maxdepth 1 -iname 'skill.md' -printf '%f\n' 2>/dev/null | head -n1)
    if [ -z "$manifest" ]; then
      note "$name: no SKILL.md (not a valid skill)"
      continue
    fi
    if [ "$manifest" != "SKILL.md" ]; then
      note "$name: manifest is '$manifest' — must be 'SKILL.md' (breaks on case-sensitive FS)"
    fi
    file="$d$manifest"
    # must start with YAML frontmatter; tr -d '\r' drops the CR a windows-authored file leaves on the line
    if [ "$(head -n1 "$file" | tr -d '\r')" != "---" ]; then
      note "$name: SKILL.md has no YAML frontmatter (no name/description)"
      continue
    fi
    # extract frontmatter block (between first two --- lines)
    fm=$(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$file")
    desc=$(echo "$fm" | grep -iE '^description:' | sed -E 's/^description:[[:space:]]*//I')
    nm=$(echo "$fm" | grep -iE '^name:' | sed -E 's/^name:[[:space:]]*//I')
    [ -z "$(echo "$desc" | tr -d '[:space:]')" ] && note "$name: empty 'description:' (skill cannot be auto-selected)"
    [ -z "$(echo "$nm"   | tr -d '[:space:]')" ] && note "$name: empty 'name:'"
    [ -n "$nm" ] && [ "$nm" != "$name" ] && note "$name: frontmatter name '$nm' != folder '$name' (drift)"
    # flag nested SKILL.md manifests: leaves of a master must be frontmatter-less
    # references/<leaf>.md, never nested subskills. Promote an independently-discoverable
    # capability to its own top-level peer skill instead of nesting it.
    while IFS= read -r nested; do
      [ -z "$nested" ] && continue
      note "$name: nested manifest '${nested#$d}' — leaves must be references/<leaf>.md (no frontmatter), or a top-level peer skill; never a nested SKILL.md"
    # < <(...) feeds the loop without a pipe, so the ISSUES count survives instead of dying in a subshell
    done < <(find "$d" -mindepth 2 -iname 'skill.md' 2>/dev/null)
    # flag stray frontmatter in reference leaves: a name/description makes a leaf get
    # discovered as its own skill, which references must not do.
    if [ -d "${d}references" ]; then
      while IFS= read -r ref; do
        [ -z "$ref" ] && continue
        # <(...) hands awk's output to grep as if it were a file, so no temp file is needed
        if [ "$(head -n1 "$ref" | tr -d '\r')" = "---" ] && grep -qiE '^(name|description):' <(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$ref"); then
          note "$name: reference '${ref#$d}' has name/description frontmatter — references must be plain docs so they are not discovered as skills"
        fi
      done < <(find "${d}references" -iname '*.md' 2>/dev/null)
    fi
  done
fi

# --- Agents ---------------------------------------------------------------
AGENTS_DIR="$CLAUDE_DIR/agents"
if [ -d "$AGENTS_DIR" ]; then
  echo "Agents ($AGENTS_DIR):"
  for file in "$AGENTS_DIR"/*.md; do
    [ -f "$file" ] || continue
    base=$(basename "$file" .md)
    if [ "$(head -n1 "$file" | tr -d '\r')" != "---" ]; then
      note "$base: no YAML frontmatter"
      continue
    fi
    fm=$(awk 'NR>1 && /^---[[:space:]]*$/{exit} NR>1{print}' "$file")
    desc=$(echo "$fm" | grep -iE '^description:' | sed -E 's/^description:[[:space:]]*//I')
    [ -z "$(echo "$desc" | tr -d '[:space:]')" ] && note "$base: empty 'description:' (agent cannot be auto-routed)"
  done
fi

echo
if [ "$ISSUES" -eq 0 ]; then
  echo "OK — no skill/agent config defects found."
else
  echo "$ISSUES issue(s) found. Fix before relying on skill discovery / auto-delegation."
fi
exit $([ "$ISSUES" -eq 0 ] && echo 0 || echo 1)
