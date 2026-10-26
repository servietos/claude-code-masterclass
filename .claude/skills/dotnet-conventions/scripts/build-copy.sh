#!/usr/bin/env bash
set -uo pipefail

usage() {
  echo "usage: build-copy.sh --root <repo> --out <dir> --path <rel> [--path <rel> ...] [--test <rel> ...] [--extra <rel> ...]"
  echo "  copies each --path/--test (bin, obj, node_modules excluded) into --out with the repo layout kept,"
  echo "  plus the root build files and every --extra file or folder the tests read (fixtures, seeds),"
  echo "  then builds every --path and tests every --test there."
  echo "  summary: BUILD errors=N warnings=N | TEST passed=N failed=N"
  exit 2
}

root=""; out=""; paths=(); tests=(); extras=()
while [ $# -gt 0 ]; do
  case "$1" in
    --root) root="$2"; shift 2 ;;
    --out) out="$2"; shift 2 ;;
    --path) paths+=("$2"); shift 2 ;;
    --test) tests+=("$2"); shift 2 ;;
    --extra) extras+=("$2"); shift 2 ;;
    -h|--help) usage ;;
    *) echo "unknown flag: $1"; usage ;;
  esac
done
[ -n "$root" ] && [ -n "$out" ] && [ $(( ${#paths[@]} + ${#tests[@]} )) -gt 0 ] || usage

rm -rf "$out"
mkdir -p "$out"
for f in "$root"/*.sln "$root"/*.slnx "$root"/global.json "$root"/nuget.config "$root"/NuGet.config \
         "$root"/Directory.Build.props "$root"/Directory.Build.targets "$root"/Directory.Packages.props "$root"/CLAUDE.md; do
  [ -f "$f" ] && cp "$f" "$out"/
done
for p in "${paths[@]}" "${tests[@]}"; do
  mkdir -p "$out/$p"
  (cd "$root/$p" && tar --exclude=./bin --exclude=./obj --exclude=./node_modules -cf - .) | tar -xf - -C "$out/$p"
done
for x in "${extras[@]}"; do
  mkdir -p "$out/$(dirname "$x")"
  cp -r "$root/$x" "$out/$x"
done

errors=0; warnings=0; passed=0; failed=0
for p in "${paths[@]}"; do
  log=$(dotnet build "$out/$p" -nologo -v q 2>&1)
  e=$(echo "$log" | grep -oE '[0-9]+ Error\(s\)' | tail -1 | cut -d' ' -f1)
  w=$(echo "$log" | grep -oE '[0-9]+ Warning\(s\)' | tail -1 | cut -d' ' -f1)
  echo "$log" | grep -E ': (error|warning) ' | sort -u
  errors=$(( errors + ${e:-1} )); warnings=$(( warnings + ${w:-0} ))
done
for t in "${tests[@]}"; do
  log=$(dotnet test "$out/$t" -nologo 2>&1)
  echo "$log" | grep -E '^\s+Failed [A-Za-z]' | sort -u
  f=$(echo "$log" | grep -oE 'Failed: +[0-9]+' | tail -1 | grep -oE '[0-9]+')
  s=$(echo "$log" | grep -oE 'Passed: +[0-9]+' | tail -1 | grep -oE '[0-9]+')
  [ -z "$s" ] && [ -z "$f" ] && f=1
  failed=$(( failed + ${f:-0} )); passed=$(( passed + ${s:-0} ))
done

echo "BUILD errors=$errors warnings=$warnings | TEST passed=$passed failed=$failed | copy=$out"
[ "$errors" -eq 0 ] && [ "$failed" -eq 0 ]
