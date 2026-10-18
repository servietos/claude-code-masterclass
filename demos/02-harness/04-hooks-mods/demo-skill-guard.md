# Enforce a Skill Folder Convention with Hooks

Hooks become an enforcement layer once you point them at a real convention: one root `SKILL.md` per master skill, with frontmatter-free `references/` leaves. You build a `PreToolUse` blocker that stops a nested manifest reaching disk and a `PostToolUse` linter that catches what slipped past.

---

Work in `demos/02-harness/04-hooks-mods/skill-guard/` (Python 3.9 or newer and a `bash` on PATH, Git Bash on Windows); the completed reference is in [skill-guard-solution/](skill-guard-solution/readme.md).

## Step 1: Refuse the Nested Subskill Before It Lands

**Overview:** A `PreToolUse` hook reads the write before it happens, so the nested `SKILL.md` never gets created and Claude is told the correct path in the same breath. This is the step where the payload's `content` field earns its place, and only a `Write` carries it, since an `Edit` carries `old_string` and `new_string`.

```text
Create hooks/block_nested_skill.py in demos/02-harness/04-hooks-mods/skill-guard/.
Behaviour:
- Read one JSON object from stdin. If tool_name is not Write or Edit, exit 0.
- Take tool_input.file_path, normalise it to POSIX form, and strip the leading cwd prefix so the path is repo-relative.
- Split into segments. If the path is not under a .claude/skills/ folder, exit 0. Let the segments after "skills" be the tail; if the tail is shorter than two segments, exit 0.
- Block with exit 2 and a one-line reason on stderr in these three cases:
  1. The last segment is SKILL.md in any casing and the tail is longer than two segments: a nested subskill manifest. Name the correct replacement path, .claude/skills/<skill>/references/<nested>.md, and mention promoting it to a top-level skill folder as the alternative.
  2. The last segment is exactly skill.md and the tail is exactly two segments: wrong casing. Say a lowercase manifest is invisible on case-sensitive filesystems.
  3. The second tail segment is "references", the file ends in .md, and tool_input.content starts with a --- frontmatter block containing a name or description key. Say a reference must stay a plain document because frontmatter makes it get discovered as its own skill.
```

**Expected Outcome:** Piping a nested manifest in produces exit 2 and a reason that names the replacement path:

```text
nested subskill manifest .claude/skills/angular-conventions/forms/SKILL.md: write .claude/skills/angular-conventions/references/forms.md instead, or promote it to a top-level skill folder
exit=2
```

A reference carrying frontmatter blocks the same way, while a plain `references/forms.md` produces no output and `exit=0`.

## Step 2: Sweep the Whole Tree After Every Change

**Overview:** The blocker only sees writes that pass through the tool layer, so a file copied by a shell command or pulled by git bypasses it. You wrap the shipped linter in a `PostToolUse` hook, where exit 2 cannot undo the write; it feeds stderr back to Claude so the next turn repairs the file.

```text
Create hooks/lint_skills.py in demos/02-harness/04-hooks-mods/skill-guard/.
Behaviour:
- Read one JSON object from stdin. If tool_name is not Write or Edit, exit 0.
- Take tool_input.file_path and normalise it to POSIX form. If it contains neither ".claude/skills/" nor ".claude/agents/", exit 0.
- Resolve the lint root from the HOOK_LINT_ROOT environment variable, defaulting to the project folder resolved relative to the script file.
- Run scripts/lint-claude-config.sh against that root with subprocess.
- If the linter exits 0, print "[lint] skill and agent config clean" to stderr and exit 0.
- Otherwise print the linter's stdout to stderr and exit 2.
Portability constraint: invoke bash with a script path relative to the lint root and pass "." as the argument, with cwd set to the lint root. Do not pass absolute paths to bash. The bash at Git\usr\bin\bash.exe on Windows rejects a drive-letter path like D:/repo/scripts/lint.sh and exits 127.
```

**Expected Outcome:** Pointed at the broken fixture, the hook prints the full issue list on stderr, ending in `4 issue(s) found. Fix before relying on skill discovery / auto-delegation.` and `exit=2`.

Pointing it at the clean fixture prints `[lint] skill and agent config clean` and exits 0, and a write to `src/app.py` prints nothing and exits 0 without ever spawning bash.

## Step 3: Prove Both Layers with Exit-Code Tests

**Overview:** Wire both hooks in `.claude/settings.json` first: a `PreToolUse` group running `hooks/block_nested_skill.py` and a `PostToolUse` group running `hooks/lint_skills.py`, each with matcher `Write|Edit` and a command of the form `python "$CLAUDE_PROJECT_DIR/hooks/<script>.py"`. Then assert the contract each layer promises, including the paths that must stay allowed.

```text
Wire both hooks in demos/02-harness/04-hooks-mods/skill-guard/.claude/settings.json: a PreToolUse group running hooks/block_nested_skill.py and a PostToolUse group running hooks/lint_skills.py, each with matcher Write|Edit and a command of the form python "$CLAUDE_PROJECT_DIR/hooks/<script>.py".
Add two test modules to demos/02-harness/04-hooks-mods/skill-guard/tests/, following the style of test_lint_script.py and importing run_hook from hook_harness.
tests/test_block_nested_skill.py:
- a root .claude/skills/angular-conventions/SKILL.md passes with exit 0 and empty stderr
- a nested forms/SKILL.md blocks with exit 2, and stderr names the replacement path .claude/skills/angular-conventions/references/forms.md
- a lowercase root skill.md blocks with exit 2 and stderr says it must be named SKILL.md
- a references/signals.md whose content carries name and description frontmatter blocks with exit 2
- the blocked case writes nothing to stdout
tests/test_lint_skills.py (set HOOK_LINT_ROOT to a fixtures path per case):
- a skill write against fixtures/clean exits 0 and reports "skill and agent config clean"
- a skill write against fixtures/broken exits 2, stderr contains "nested manifest 'forms/SKILL.md'" and "4 issue(s) found", and stdout is empty
- a write to src/app.py against fixtures/broken exits 0 with empty stderr
Constraints: standard library unittest only, no inline comments. Then run: python -m unittest discover -s tests -v
```

**Expected Outcome:** The new cases join the three shipped tests and the run ends in `OK`. The `src/app.py` case points the lint root at the broken fixture, so it passes only if the path filter short-circuits before the linter ever runs.
