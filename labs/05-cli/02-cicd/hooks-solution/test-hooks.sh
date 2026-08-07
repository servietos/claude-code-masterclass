#!/usr/bin/env bash
cd "$(dirname "$0")"
chmod +x .claude/hooks/policy-gate.sh .claude/hooks/scope-gate.sh

PASS=0
FAIL=0

run_case() {
  local label=$1 script=$2 payload=$3 want=$4
  local out rc
  out=$(printf '%s' "$payload" | ./.claude/hooks/"$script" 2>&1)
  rc=$?
  if [ "$rc" = "$want" ]; then
    PASS=$((PASS+1))
    printf 'PASS  %-46s exit=%s  %s\n' "$label" "$rc" "$out"
  else
    FAIL=$((FAIL+1))
    printf 'FAIL  %-46s exit=%s want=%s  %s\n' "$label" "$rc" "$want" "$out"
  fi
}

bash_payload() {
  jq -nc --arg c "$1" '{
    session_id: "8f1a2b3c-0000-4000-8000-000000000001",
    transcript_path: "/tmp/t.jsonl",
    cwd: "/repo",
    permission_mode: "default",
    hook_event_name: "PreToolUse",
    tool_name: "Bash",
    tool_input: { command: $c, description: "test" }
  }'
}

write_payload() {
  jq -nc --arg p "$1" '{
    session_id: "8f1a2b3c-0000-4000-8000-000000000001",
    transcript_path: "/tmp/t.jsonl",
    cwd: "/repo",
    permission_mode: "default",
    hook_event_name: "PreToolUse",
    tool_name: "Write",
    tool_input: { file_path: $p, content: "x" }
  }'
}

echo "--- policy-gate.sh (Bash matcher) ---"
run_case "rm -rf /tmp/x"                policy-gate.sh "$(bash_payload 'rm -rf /tmp/x')"                    2
run_case "git push --force"             policy-gate.sh "$(bash_payload 'git push --force')"                 2
run_case "npm test"                     policy-gate.sh "$(bash_payload 'npm test')"                         0
run_case "rm -rf /tmp/cli-utils-test"   policy-gate.sh "$(bash_payload 'rm -rf /tmp/cli-utils-test')"       2
run_case "git push --force-with-lease"  policy-gate.sh "$(bash_payload 'git push --force-with-lease')"      2
run_case "git push origin main --force" policy-gate.sh "$(bash_payload 'git push origin main --force')"     2
run_case "rm -r -f /tmp/x (split flags)" policy-gate.sh "$(bash_payload 'rm -r -f /tmp/x')"                 0
run_case "rm -fr /tmp/x (swapped flags)" policy-gate.sh "$(bash_payload 'rm -fr /tmp/x')"                   0
run_case "git push -f (short flag)"      policy-gate.sh "$(bash_payload 'git push -f origin main')"         0
run_case "echo hi && rm -rf /"           policy-gate.sh "$(bash_payload 'echo hi && rm -rf /')"             2

echo
echo "--- scope-gate.sh (Write|Edit matcher) ---"
run_case "abs /repo/src/slugify.ts"      scope-gate.sh "$(write_payload '/repo/src/slugify.ts')"            0
run_case "abs /etc/cli-utils-config.json" scope-gate.sh "$(write_payload '/etc/cli-utils-config.json')"     2
run_case "RELATIVE src/slugify.ts"       scope-gate.sh "$(write_payload 'src/slugify.ts')"                  0
run_case "RELATIVE test/slugify.test.ts" scope-gate.sh "$(write_payload 'test/slugify.test.ts')"            0
run_case "RELATIVE README.md"            scope-gate.sh "$(write_payload 'README.md')"                       0
run_case "RELATIVE package.json"         scope-gate.sh "$(write_payload 'package.json')"                    0
run_case "abs /repo/README.md"           scope-gate.sh "$(write_payload '/repo/README.md')"                 0
run_case "abs /repo/src/a/b/deep.ts"     scope-gate.sh "$(write_payload '/repo/src/a/b/deep.ts')"           0
run_case "abs /repo/src (no trailing)"   scope-gate.sh "$(write_payload '/repo/src')"                       2
run_case "windows C:\\repo\\src\\x.ts"   scope-gate.sh "$(write_payload 'C:\repo\src\x.ts')"                0
run_case "windows C:\\repo\\etc\\x.json" scope-gate.sh "$(write_payload 'C:\repo\etc\x.json')"              2
run_case "evil /tmp/src/pwn.sh"          scope-gate.sh "$(write_payload '/tmp/src/pwn.sh')"                 0
run_case "empty file_path"               scope-gate.sh "$(write_payload '')"                                0
run_case "docs .tool_input.path form"    scope-gate.sh '{"tool_name":"Write","tool_input":{"path":"/repo/src/a.ts","file_text":"x"}}' 0

echo
echo "PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
