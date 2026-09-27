#!/usr/bin/env bash
# Material -> Tailwind v4 migration helper for an Angular app.
#
#   material-to-tailwind.sh --verify <app-dir>
#       Read-only. Reports whether the app is fully off Angular Material and
#       correctly wired to Tailwind. Exit 0 = clean, 1 = work remaining.
#
#   material-to-tailwind.sh --wire <app-dir> [--dry-run]
#       The deterministic half of the migration: packages, .postcssrc.json,
#       angular.json style order, and the `*` reset that kills Tailwind borders.
#       Component templates are NOT touched; that is judgement work.
#
# Why this exists: the build passing proves nothing here. Material survives in
# e2e selectors, markdown guides and fixture data long after `ng build` is green,
# and an unlayered `* { border: 0 }` silently voids every Tailwind border utility.
set -uo pipefail

MODE=""
APP=""
DRY_RUN=0

while [ $# -gt 0 ]; do
  case "$1" in
    --verify) MODE="verify"; APP="${2:-}"; shift 2 ;;
    --wire)   MODE="wire";   APP="${2:-}"; shift 2 ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "unknown argument: $1" >&2; exit 2 ;;
  esac
done

[ -n "$MODE" ] && [ -n "$APP" ] || { sed -n '2,14p' "$0" | sed 's/^# \{0,1\}//'; exit 2; }
[ -f "$APP/angular.json" ] || { echo "not an Angular app: $APP" >&2; exit 2; }

cd "$APP" || exit 2

say() { printf '%s\n' "$*"; }
run() { if [ "$DRY_RUN" = 1 ]; then say "  would run: $*"; else "$@"; fi; }

# ----------------------------------------------------------------- verify ----
if [ "$MODE" = "verify" ]; then
  fail=0

  pkg_material=$(grep -c '"@angular/material"' package.json || true)
  pkg_cdk=$(grep -c '"@angular/cdk"' package.json || true)
  pkg_tw=$(grep -c '"tailwindcss"' package.json || true)
  has_postcss=$([ -f .postcssrc.json ] && echo 1 || echo 0)

  # style order: tailwind entry must precede the scss entry
  order_ok=0
  if grep -q 'tailwind.css' angular.json; then
    tw_line=$(grep -n 'tailwind.css' angular.json | head -1 | cut -d: -f1)
    scss_line=$(grep -n 'src/styles.scss' angular.json | head -1 | cut -d: -f1)
    [ -n "$tw_line" ] && [ -n "$scss_line" ] && [ "$tw_line" -lt "$scss_line" ] && order_ok=1
  fi

  # the reset that deletes every Tailwind border
  reset_hits=$(grep -rlE '^\s*\*\s*\{' src/ 2>/dev/null | xargs -r grep -lE 'border:\s*0' 2>/dev/null | tr '\n' ' ')

  # Material survivors, by surface
  src_hits=$(grep -rn "mat-\|Mat[A-Z]\|@angular/material\|@angular/cdk" src 2>/dev/null | wc -l)
  e2e_hits=0
  [ -d e2e ] && e2e_hits=$(grep -rn "mat-\|Mat[A-Z]\|matinput\|mattooltip" e2e 2>/dev/null | wc -l)
  doc_hits=0
  [ -d public ] && doc_hits=$(grep -rn "mat-[a-z]\|@angular/material" public 2>/dev/null | wc -l)

  say "app:            $APP"
  say "packages:       material=$pkg_material cdk=$pkg_cdk tailwind=$pkg_tw"
  say ".postcssrc.json: $has_postcss"
  say "style order ok: $order_ok"
  say "material in src: $src_hits"
  say "material in e2e: $e2e_hits"
  say "material in docs: $doc_hits"
  say "star-reset files: ${reset_hits:-none}"

  [ "$pkg_material" -eq 0 ] || { say "FAIL: @angular/material still in package.json"; fail=1; }
  [ "$pkg_cdk" -eq 0 ]      || { say "FAIL: @angular/cdk still in package.json"; fail=1; }
  [ "$pkg_tw" -gt 0 ]       || { say "FAIL: tailwindcss not installed"; fail=1; }
  [ "$has_postcss" -eq 1 ]  || { say "FAIL: .postcssrc.json missing"; fail=1; }
  [ "$order_ok" -eq 1 ]     || { say "FAIL: tailwind.css must precede styles.scss in angular.json"; fail=1; }
  [ "$src_hits" -eq 0 ]     || { say "FAIL: $src_hits Material references left in src/"; fail=1; }
  [ "$e2e_hits" -eq 0 ]     || { say "FAIL: $e2e_hits Material selectors left in e2e/"; fail=1; }
  [ "$doc_hits" -eq 0 ]     || { say "FAIL: $doc_hits Material references left in public/"; fail=1; }
  [ -z "$reset_hits" ]      || { say "FAIL: '* { border: 0 }' reset present, voids every Tailwind border"; fail=1; }

  if [ "$fail" -eq 0 ]; then say "RESULT: CLEAN"; else say "RESULT: WORK REMAINING"; fi
  exit "$fail"
fi

# ------------------------------------------------------------------- wire ----
say "wiring Tailwind v4 in $APP (dry-run=$DRY_RUN)"

say "1. packages"
run npm install -D tailwindcss @tailwindcss/postcss postcss
if grep -q '"@angular/material"\|"@angular/cdk"' package.json; then
  run npm uninstall @angular/material @angular/cdk
fi

say "2. .postcssrc.json"
if [ -f .postcssrc.json ]; then
  say "  exists, left alone"
elif [ "$DRY_RUN" = 1 ]; then
  say "  would create .postcssrc.json"
else
  printf '{\n  "plugins": {\n    "@tailwindcss/postcss": {}\n  }\n}\n' > .postcssrc.json
  say "  created"
fi

say "3. angular.json style order"
if grep -q 'src/tailwind.css' angular.json; then
  say "  tailwind.css already registered"
elif [ "$DRY_RUN" = 1 ]; then
  say "  would insert src/tailwind.css before src/styles.scss"
else
  python - <<'PY'
import pathlib
p = pathlib.Path('angular.json')
s = p.read_text(encoding='utf-8')
needle = '"styles": [\n              "src/styles.scss",'
if needle in s:
    s = s.replace(needle, '"styles": [\n              "src/tailwind.css",\n              "src/styles.scss",', 1)
    p.write_text(s, encoding='utf-8')
    print("  inserted")
else:
    print("  NOTE: styles array not in the expected shape, insert src/tailwind.css by hand")
PY
fi

say "4. the '* { border: 0 }' reset"
targets=$(grep -rlE '^\s*\*\s*\{' src/ 2>/dev/null | xargs -r grep -lE 'border:\s*0' 2>/dev/null)
if [ -z "$targets" ]; then
  say "  none found"
else
  for f in $targets; do
    if [ "$DRY_RUN" = 1 ]; then
      say "  would neutralise $f"
    else
      printf 'body {\n  margin: 0;\n}\n' > "$f"
      say "  neutralised $f"
    fi
  done
fi

say ""
say "Done with the deterministic half. Still manual:"
say "  - copy src/tailwind.css from the reference app"
say "  - convert component templates (see references/material-tailwind-migration.md)"
say "  - sweep e2e selectors, markdown guides and fixture data"
say "  - re-run: $0 --verify $APP"
