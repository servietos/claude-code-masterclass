# Build a Three-Event Hook Pipeline

A hook is a plain program the harness runs on an event, outside the model, so it enforces rather than persuades. You decode the stdin payload contract, then write and test `PreToolUse`, `PostToolUse`, and `Stop` hooks in Python and wire them into `.claude/settings.json`. You finish with a three-event pipeline that blocks protected paths, appends an audit record per write, and prints a session summary.

---

## Setup

Open Claude Code with `demos/02-harness/03-hooks/hook-pipeline/` as the working folder. Nothing needs installing: the project is Python standard library only and needs Python 3.9 or newer.

```bash
cd demos/02-harness/03-hooks/hook-pipeline
python --version
python -m unittest discover -s tests
```

The three shipped tests must pass before you start. The folder contains one finished reference hook (`hooks/inspect_payload.py`), its wiring in `.claude/settings.json`, and a test harness that pipes real JSON into a hook script.

---

## Step 1: Decode the Payload Contract

**Overview:** Every hook is a plain program that reads one JSON object from stdin. Before writing a hook you need to know exactly which fields arrive for which event, because the difference between `PreToolUse` and `PostToolUse` is a single extra key that the whole audit design depends on.

**Research / Planning / Discussion:**

```text
Read hooks/inspect_payload.py and tests/test_inspect_payload.py in this folder, then look up the Claude Code hooks documentation at https://code.claude.com/docs/en/hooks.

Answer these four questions:
1. Which fields are present in the stdin payload for every hook event, regardless of type?
2. Which field does a PostToolUse payload carry that a PreToolUse payload does not, and what is inside it?
3. Which fields does a Stop payload have, and which tool-related fields are absent?
4. On exit code 0, what does Claude Code do with whatever the hook printed to stdout?

Two sentences per answer. Do not write any code yet.
```

**Finding:** Claude should name `session_id`, `transcript_path`, `cwd`, and `hook_event_name` as the fields common to every event, and identify `tool_response` as the `PostToolUse` addition that carries the written content. For `Stop` it should note that `tool_name` and `tool_input` are absent and `last_assistant_message` is present instead. Critically, on question 4 it must say that stdout is parsed as JSON control output on exit 0, which is why diagnostics belong on stderr; if it claims stdout is simply shown to Claude, push back and ask it to re-read the exit-code section of the docs.

**Recipe:**

```text
In demos/02-harness/03-hooks/hook-pipeline/, run the reference hook by hand with three different payloads so I can see the contract for each event:

1. A PreToolUse payload for a Write to /repo/src/app.py with content "print(1)", session_id "s-1", cwd "/repo".
2. The same payload shaped as PostToolUse, adding a tool_response object with file_path and content.
3. A Stop payload with session_id "s-1" and last_assistant_message "Done."

Use this form for each so the exit code is visible, in Bash:
echo '<json>' | python hooks/inspect_payload.py; echo "exit=$?"

or this one in PowerShell, where $? is a boolean and the exit code lives in $LASTEXITCODE:
'<json>' | python hooks/inspect_payload.py; "exit=$LASTEXITCODE"

Then write a short table of which payload fields each event carries, and state in one sentence why inspect_payload.py prints to stderr rather than stdout.
```

**Expected Outcome:** Three runs, each ending in `exit=0`. The first prints exactly:

```text
[inspect] event=PreToolUse session=s-1 tool=Write tool_input_keys=content,file_path
exit=0
```

The Stop run prints `event=Stop`, `tool=-`, and `tool_input_keys=-`, because those keys are absent from a Stop payload.

---

## Step 2: Block a Tool Call with Exit Code 2

**Overview:** Exit code 2 is the only exit code that stops a tool call, and the stderr text is what Claude reads as the reason. You build a `PreToolUse` hook that protects generated paths, which teaches the blocking contract without repeating the destructive-command guardrail covered in module 09.

**Research / Planning / Discussion:**

```text
I want a PreToolUse hook that stops Claude from writing to generated output paths (docs/generated/* and any *.lock file), because those files are owned by a build step, not by the agent.

Before writing it, reason through:
1. Why is exit 2 the correct exit code here, and what happens instead if the hook exits 1?
2. Why does the reason text have to go to stderr and not stdout when the hook exits 2?
3. The payload gives an absolute file_path plus a cwd. What has to happen to that path before a pattern like docs/generated/* can match it?
4. The hook is wired with a matcher, so why should the script still check tool_name itself?

Keep each answer to two or three sentences. Do not write code yet.
```

**Finding:** Claude should say exit 2 blocks the call while any other non-zero code is a non-blocking error that only logs a warning and lets the tool run. On stderr it should explain that stdout is ignored entirely on exit 2. On the path question it should propose stripping the `cwd` prefix to get a repo-relative path before matching. On the matcher question a good answer notes that a matcher is a convenience, not a guarantee, and that a script tested in isolation should defend its own preconditions; if Claude says the `tool_name` check is redundant, push back and point at the test harness, which calls the script directly.

**Recipe:**

```text
Create hooks/protect_paths.py in demos/02-harness/03-hooks/hook-pipeline/.

Behaviour:
- Read one JSON object from stdin.
- If tool_name is not Write or Edit, exit 0 immediately.
- Take tool_input.file_path, normalise it with pathlib to POSIX form, and strip the leading cwd prefix so the path is repo-relative.
- Match the result against the patterns ["docs/generated/*", "*.lock"] using fnmatch.
- On a match, print a one-line reason to stderr naming the relative path and the pattern that matched, then exit 2.
- Otherwise exit 0 with no output.

Constraints: Python standard library only, no try/except. Comment only a line a reader cannot decode at a glance, one short line above it.
```

**Expected Outcome:** `hooks/protect_paths.py` exists. Piping a protected path in produces this exact pair:

```text
Blocked: docs/generated/api.md matches the protected pattern 'docs/generated/*'. Generated output is owned by the build step, so edit the generator input instead.
exit=2
```

Piping `/repo/src/app.py` instead produces no output and `exit=0`.

---

## Step 3: Wire the Pipeline in settings.json

**Overview:** The `hooks` key in `.claude/settings.json` is an object keyed by event name, and each event holds matcher groups rather than flat entries. Getting this shape wrong is the single most common reason a hook silently never fires.

**Research / Planning / Discussion:**

```text
Read .claude/settings.json in this folder, which currently wires only the reference hook.

Then explain, using the Claude Code hooks documentation:
1. What is the nesting order of the hooks configuration, from the "hooks" key down to a single command entry?
2. What does the matcher string match against, and what does "Write|Edit" mean?
3. If two separate matcher groups under PreToolUse both match a Write call, do both run, and does one blocking makes the other irrelevant?
4. What is $CLAUDE_PROJECT_DIR and why is it safer in a command string than a relative path like python hooks/foo.py?

Do not edit the file yet.
```

**Finding:** Claude should describe the nesting as `hooks` object, then event name, then a list of groups, then each group's `matcher` plus a `hooks` array whose entries carry `type: "command"` and `command`. It should explain the matcher is a regex over the tool name and `Write|Edit` matches either, and add that non-tool events such as `Stop` do not support matchers at all: a `matcher` field there is silently ignored. On question 4 it should note that a hook's working directory is not guaranteed to be the project root, so `$CLAUDE_PROJECT_DIR` anchors the script path. If Claude produces a flat array with a top-level `event` key, stop and tell it to re-check the docs, because that shape is obsolete.

**Recipe:**

```text
Update .claude/settings.json in demos/02-harness/03-hooks/hook-pipeline/ so it wires the full pipeline.

Keep the existing PreToolUse group for inspect_payload.py with matcher "Write|Edit|Bash", and add:
- A second PreToolUse group with matcher "Write|Edit" running hooks/protect_paths.py.
- A PostToolUse group with matcher "Write|Edit" running hooks/audit_write.py.
- A Stop group with no matcher key at all, running hooks/session_summary.py. Stop does not support matchers and always fires, so a matcher there is silently ignored.

Every command must be of the form: python "$CLAUDE_PROJECT_DIR/hooks/<script>.py"
Use the object-keyed hooks shape: hooks -> event name -> list of groups -> matcher plus a hooks array of {"type": "command", "command": ...}.

Then print the file back and confirm it is valid JSON by parsing it with python -m json.tool.
```

**Expected Outcome:** `.claude/settings.json` has a `hooks` object with `PreToolUse` (two groups), `PostToolUse`, and `Stop`, and the `Stop` group carries a `hooks` array with no `matcher` key. `python -m json.tool .claude/settings.json` exits 0 and echoes the formatted document. The two hook scripts referenced under `PostToolUse` and `Stop` do not exist yet, which is expected; you build them next.

---

## Step 4: Record an Audit Line on Every Write

**Overview:** `PostToolUse` runs after the tool has already executed, so it can never prevent anything: its value is the guaranteed side effect. You write one JSONL line per file write, which becomes the data the `Stop` hook summarises.

**Research / Planning / Discussion:**

```text
I want a PostToolUse hook that appends one JSON line per file write to logs/audit.jsonl.

Think through the design before coding:
1. Why is JSONL a better format here than a single JSON array file, given that hooks run as separate short-lived processes?
2. Which payload fields belong in an audit record so that a later Stop hook can group by session and by file?
3. tool_response carries the written content. Should the audit line store the content itself, or something derived from it, and why?
4. The tests need to point this hook at a temporary log file. What is the least intrusive way to make the log path overridable?

Two or three sentences each. No code yet.
```

**Finding:** Claude should give the append-only argument for JSONL: each process appends one line without reading or rewriting the file, so concurrent hook invocations cannot corrupt it. For fields it should propose a timestamp, `session_id`, `tool_name`, and `file_path`. On question 3 it should recommend storing a derived size rather than the content, to keep the log small and avoid duplicating file contents on disk. On question 4 an environment variable read with a sensible default is the expected answer; if Claude suggests a command-line argument, push back, because hooks are invoked by a fixed command string.

**Recipe:**

```text
Create hooks/audit_write.py in demos/02-harness/03-hooks/hook-pipeline/.

Behaviour:
- Resolve the log path from the HOOK_AUDIT_LOG environment variable, defaulting to <project>/logs/audit.jsonl resolved relative to the script file.
- Read one JSON object from stdin. If tool_name is not Write or Edit, exit 0.
- Build a record with these keys exactly: ts (UTC ISO 8601, seconds precision), session_id, tool, file_path, bytes (the length of tool_response.content).
- Create the parent directory if needed, append the record as one JSON line, print a one-line confirmation to stderr, and exit 0.

Constraints: Python standard library only, no try/except. Comment only a line a reader cannot decode at a glance, one short line above it. The hook must never exit non-zero.
```

**Expected Outcome:** Piping two payloads (a Write of `print(1)` and an Edit of `x = 1`, both session `s-1`) prints to stderr and exits 0 each time:

```text
[audit] recorded Write /repo/src/app.py
exit=0
[audit] recorded Edit /repo/src/util.py
exit=0
```

`logs/audit.jsonl` then contains exactly two lines:

```text
{"ts": "2026-07-23T05:23:26+00:00", "session_id": "s-1", "tool": "Write", "file_path": "/repo/src/app.py", "bytes": 8}
{"ts": "2026-07-23T05:23:26+00:00", "session_id": "s-1", "tool": "Edit", "file_path": "/repo/src/util.py", "bytes": 5}
```

Your timestamps will differ.

---

## Step 5: Summarise the Session on Stop

**Overview:** `Stop` fires when Claude finishes a turn, which makes it the natural place to close the loop and report what the turn actually changed. It is also the event where exit 2 has a surprising meaning, and knowing that is what keeps a reporting hook from turning into an infinite loop.

**Research / Planning / Discussion:**

```text
I want a Stop hook that reads logs/audit.jsonl and prints a summary of what this session wrote.

Reason through the risks first:
1. A Stop payload has no tool_name and no tool_input. Which field ties the summary back to the right rows in the log?
2. What does exit code 2 do on a Stop hook specifically, and what would happen if my summary hook exited 2 by mistake?
3. The log accumulates rows across many sessions. What must the hook do before counting anything?
4. What should the hook do when logs/audit.jsonl does not exist at all, and why is exiting non-zero the wrong answer there?

Two sentences each.
```

**Finding:** The answer that matters is question 2: on `Stop`, exit 2 prevents Claude from stopping and continues the conversation, so a reporting hook that exits 2 traps the session in a loop. Claude should also identify `session_id` as the join key, say the hook must filter rows to the current session before counting, and treat a missing log as a normal empty state reported on stderr with exit 0. If Claude describes exit 2 on Stop as simply blocking or as a no-op, correct it: the docs are explicit that it prevents stopping.

**Recipe:**

```text
Create hooks/session_summary.py in demos/02-harness/03-hooks/hook-pipeline/.

Behaviour:
- Resolve the log path from HOOK_AUDIT_LOG, defaulting to <project>/logs/audit.jsonl relative to the script file.
- Read the Stop payload from stdin and take session_id.
- If the log is missing, or holds no rows for this session, print "[summary] session <id>: no file writes recorded" to stderr and exit 0.
- Otherwise filter the rows to this session and print to stderr:
  - a header line: "[summary] session <id>: <n> writes, <n> files, <n> bytes" where files is the count of distinct file_path values and bytes is the sum of the bytes field
  - one indented line per tool in the form "  <Tool> x<count>", sorted by tool name
  - one indented line per distinct file_path, sorted
- Always exit 0.

Constraints: Python standard library only (use collections.Counter), no try/except. Comment only a line a reader cannot decode at a glance, one short line above it.
```

**Expected Outcome:** With the two audit rows from Step 4 on disk, piping a Stop payload for session `s-1` prints exactly this and exits 0:

```text
[summary] session s-1: 2 writes, 2 files, 13 bytes
[summary]   Edit x1
[summary]   Write x1
[summary]   /repo/src/app.py
[summary]   /repo/src/util.py
exit=0
```

---

## Step 6: Prove the Pipeline with Exit-Code Tests

**Overview:** A hook that is never tested is a hook you discover is broken during a live session. The shipped harness already pipes real JSON into a script and returns exit code, stdout, and stderr, so the remaining work is asserting the contract each of your three hooks promises.

**Research / Planning / Discussion:**

```text
Read tests/hook_harness.py and tests/test_inspect_payload.py in this folder.

Then plan the test coverage for the three hooks I just built:
1. Which exit code does each hook's test need to assert, and which hook is the only one that should ever produce a non-zero code?
2. protect_paths.py blocks on exit 2. Besides the exit code, what else should the test assert about the process output, and which stream should be empty?
3. audit_write.py and session_summary.py touch the filesystem. How do I keep those tests isolated from logs/audit.jsonl, and which mechanism did I already build in for that?
4. The summary hook filters by session_id. What is the one fixture row that proves the filter actually works?

List the test cases you would write, one line each. Do not write the tests yet.
```

**Finding:** Claude should propose exit 2 assertions only for `protect_paths.py` and exit 0 for everything else, plus an assertion that stdout is empty on the block path since exit 2 discards stdout. For isolation it must reach for `HOOK_AUDIT_LOG` with `tempfile.TemporaryDirectory`, not for monkeypatching or for deleting the real log. On question 4 the answer to look for is a fixture row belonging to a different session that must not appear in the output; if Claude's plan has no such row, the filter is untested and you should say so.

**Recipe:**

```text
Add three test modules to demos/02-harness/03-hooks/hook-pipeline/tests/, following the style of test_inspect_payload.py and importing run_hook from hook_harness.

tests/test_protect_paths.py:
- an ordinary source path passes with exit 0 and empty stderr
- a docs/generated/ path blocks with exit 2 and stderr naming both the path and the pattern
- a *.lock path via an Edit call blocks with exit 2
- a Bash call against a protected path is ignored with exit 0
- the blocked case writes nothing to stdout

tests/test_audit_write.py (use tempfile.TemporaryDirectory plus the HOOK_AUDIT_LOG env var for isolation):
- two calls append exactly two lines, with the second line's bytes field correct
- one record has exactly the keys ts, session_id, tool, file_path, bytes and the right values
- the hook exits 0
- a Bash call writes no log file at all

tests/test_session_summary.py (seed a temp log with two rows for session abc123 and one row for session "other"):
- the summary counts only abc123, reports "2 writes, 1 files, 8 bytes", lists "Write x1" and "Edit x1", and never mentions the other session's file
- an unknown session reports "no file writes recorded"
- a missing log file exits 0 and reports "no file writes recorded"

Constraints: standard library unittest only, no inline comments. Then run: python -m unittest discover -s tests -v
```

**Expected Outcome:** The suite grows from 3 tests to 15 and passes:

```text
----------------------------------------------------------------------
Ran 15 tests in 0.558s

OK
```

Your timing will differ. The completed reference, with all four hooks and the full settings wiring, is in [hook-pipeline-solution/](hook-pipeline-solution/readme.md). Its `logs/audit.jsonl` is not checked in: like the one you produced in Step 4, it is generated when the hooks run.

