# Enforce a Skill Folder Convention with Hooks

Hooks become an enforcement layer once you point them at a real convention: one root `SKILL.md` per master skill, with frontmatter-free `references/` leaves. You run a linter against a clean and a broken fixture tree, then build a `PreToolUse` blocker that stops a nested manifest reaching disk and a `PostToolUse` linter that catches what slipped past. You finish with two tested hooks wired into settings and a block message that spells out the correct shape.

---

## Setup

Open Claude Code with `demos/02-harness/03-hooks/skill-guard/` as the working folder. Nothing needs installing: the project is Python standard library only, needs Python 3.9 or newer, and calls a `bash` on PATH (Git Bash on Windows).

```bash
cd demos/02-harness/03-hooks/skill-guard
python -m unittest discover -s tests
```

The three shipped tests must pass before you start. The folder contains a finished reference linter (`scripts/lint-claude-config.sh`), two fixture skill trees, and a test harness that both pipes JSON into a hook script and runs the linter against a fixture.

## Demo Files

| File | What it represents |
|------|--------------------|
| `scripts/lint-claude-config.sh` | The reference linter: walks `.claude/skills/` and `.claude/agents/`, prints one line per defect, exits 1 when any are found |
| `fixtures/clean/.claude/` | A correct tree: one root `SKILL.md`, three frontmatter-free `references/`, one agent with a real description |
| `fixtures/broken/.claude/` | The same tree carrying one of each defect: a nested `forms/SKILL.md`, a reference with frontmatter, a lowercase `skill.md`, an agent with an empty description |
| `.claude/settings.json` | An empty `hooks` object you fill in at Step 4 |

---

## Step 1: See the Convention Break

**Overview:** A convention nobody can see is a convention nobody keeps. Before writing any hook you run the linter against both fixture trees, so the four defects stop being abstract rules and become four lines of real output you can point a hook at.

**Research / Planning / Discussion:**

```text
Read scripts/lint-claude-config.sh in this folder, then list every file under fixtures/clean/.claude and fixtures/broken/.claude.

Answer these four questions:
1. What exactly does the script check for inside a skill folder, and what does it check for inside an agent file?
2. Diff the two fixture trees. Which four files in fixtures/broken violate the convention, and which rule does each one break?
3. The script flags a references/*.md file that carries name or description frontmatter. Why is that frontmatter harmful on a leaf when the same frontmatter is mandatory on the master's SKILL.md?
4. One skill folder in fixtures/broken is named orphan-notes and its manifest is lowercase. The tree lints fine on Windows today. What breaks, and where?

Two or three sentences per answer. Do not write any code yet.
```

**Finding:** Claude should identify the four checks (manifest presence and casing, non-empty `name` and `description`, nested manifests, frontmatter in references) and map each broken file to its rule. On question 3 the answer that matters is discovery: frontmatter is what makes a file get picked up as its own skill, so a leaf that carries it competes with its own master instead of being routed to. On question 4 it should say the lowercase manifest works on case-insensitive Windows and macOS volumes but is invisible on a case-sensitive filesystem, so the skill silently disappears in CI or on a Linux teammate's machine. If Claude treats the lowercase manifest as cosmetic, push back and ask which filesystem the CI runner uses.

**Recipe:**

```text
In demos/02-harness/03-hooks/skill-guard/, run the reference linter against both fixture trees so I can see the contract:

In Bash:
bash scripts/lint-claude-config.sh fixtures/clean; echo "exit=$?"
bash scripts/lint-claude-config.sh fixtures/broken; echo "exit=$?"

In PowerShell, where $? is a boolean and the exit code lives in $LASTEXITCODE:
bash scripts/lint-claude-config.sh fixtures/clean; "exit=$LASTEXITCODE"
bash scripts/lint-claude-config.sh fixtures/broken; "exit=$LASTEXITCODE"

Then write a four-row table mapping each reported defect to the offending file path and to the rule it breaks, and state in one sentence why the script exits 1 rather than 2.
```

**Expected Outcome:** The clean tree passes and the broken tree reports exactly four issues:

```text
Skills (fixtures/clean/.claude/skills):
Agents (fixtures/clean/.claude/agents):

OK — no skill/agent config defects found.
exit=0
```

```text
Skills (fixtures/broken/.claude/skills):
  [!] angular-conventions: nested manifest 'forms/SKILL.md' — leaves must be references/<leaf>.md (no frontmatter), or a top-level peer skill; never a nested SKILL.md
  [!] angular-conventions: reference 'references/signals.md' has name/description frontmatter — references must be plain docs so they are not discovered as skills
  [!] orphan-notes: manifest is 'skill.md' — must be 'SKILL.md' (breaks on case-sensitive FS)
Agents (fixtures/broken/.claude/agents):
  [!] mystery-agent: empty 'description:' (agent cannot be auto-routed)

4 issue(s) found. Fix before relying on skill discovery / auto-delegation.
exit=1
```

The linter is a standalone program, so exit 1 means it found issues. Exit 2 only carries meaning once a hook wraps it, which is Step 3.

---

## Step 2: Refuse the Nested Subskill Before It Lands

**Overview:** The linter reports a violation that already exists on disk. A `PreToolUse` hook reads the same write before it happens, so the nested `SKILL.md` never gets created and Claude is told the correct path in the same breath. This is the step where the payload's `content` field earns its place.

**Research / Planning / Discussion:**

```text
I want a PreToolUse hook that refuses three specific writes under .claude/skills/:
- a SKILL.md nested below a skill folder's root, such as .claude/skills/angular-conventions/forms/SKILL.md
- a root manifest named skill.md in lowercase
- a references/*.md file whose content starts with frontmatter carrying name or description

Reason through the design before coding:
1. The payload gives an absolute file_path plus a cwd. After making the path repo-relative, how do I tell a legal root manifest apart from an illegal nested one using only the path segments?
2. Rule three needs the file's text, not just its path. Which payload field carries it on a Write, and why does that field not exist on an Edit?
3. A blocked write should leave Claude able to fix itself. What must the stderr message contain beyond the word "blocked"?
4. Why is exit 2 the right code here, and what would exit 1 do instead?

Two or three sentences each. No code yet.
```

**Finding:** On question 1 Claude should reach for segment counting: the tail after `skills/` is `[<skill>, SKILL.md]` for a legal manifest and longer for a nested one, which is a path rule needing no filesystem access. On question 2 it must name `tool_input.content` and explain that an `Edit` carries `old_string` and `new_string` instead, so the frontmatter check only applies to `Write`; if Claude claims `content` is present on both, tell it to re-read the payload for `Edit`. On question 3 the answer to hold out for is the corrected path spelled in full (`references/forms.md`), not a generic complaint, because a hook that only says no costs a turn. On question 4 it should say exit 2 blocks the call and surfaces stderr to Claude, while exit 1 is a non-blocking error that lets the write proceed.

**Recipe:**

```text
Create hooks/block_nested_skill.py in demos/02-harness/03-hooks/skill-guard/.

Behaviour:
- Read one JSON object from stdin. If tool_name is not Write or Edit, exit 0.
- Take tool_input.file_path, normalise it to POSIX form, and strip the leading cwd prefix so the path is repo-relative.
- Split into segments. If the path is not under a .claude/skills/ folder, exit 0. Let the segments after "skills" be the tail; if the tail is shorter than two segments, exit 0.
- Block with exit 2 and a one-line reason on stderr in these three cases:
  1. The last segment is SKILL.md in any casing and the tail is longer than two segments: a nested subskill manifest. Name the correct replacement path, .claude/skills/<skill>/references/<nested>.md, and mention promoting it to a top-level skill folder as the alternative.
  2. The last segment is exactly skill.md and the tail is exactly two segments: wrong casing. Say a lowercase manifest is invisible on case-sensitive filesystems.
  3. The second tail segment is "references", the file ends in .md, and tool_input.content starts with a --- frontmatter block containing a name or description key. Say a reference must stay a plain document because frontmatter makes it get discovered as its own skill.
- Otherwise exit 0 with no output.

Constraints: Python standard library only, no try/except. Comment only a line a reader cannot decode at a glance, one short line above it.
```

**Expected Outcome:** `hooks/block_nested_skill.py` exists. Piping a nested manifest in produces exit 2 and a reason that names the replacement path:

```text
Blocked: .claude/skills/angular-conventions/forms/SKILL.md is a nested subskill manifest. A master skill holds exactly one SKILL.md at its root, so write .claude/skills/angular-conventions/references/forms.md as a plain reference instead, or promote the capability to its own top-level skill folder.
exit=2
```

A reference carrying frontmatter blocks the same way, while a plain `references/forms.md` produces no output and `exit=0`.

---

## Step 3: Sweep the Whole Tree After Every Change

**Overview:** The blocker only sees writes that pass through the tool layer. A file copied by a shell command, pulled by git, or edited in another window bypasses it entirely, which is why the preventive layer needs a sweep behind it. You wrap the shipped linter in a `PostToolUse` hook that runs whenever a skill or agent file changes.

**Research / Planning / Discussion:**

```text
I want a PostToolUse hook that runs scripts/lint-claude-config.sh after any Write or Edit to a file under .claude/skills/ or .claude/agents/.

Think through the design:
1. PostToolUse runs after the tool has already executed, so it cannot prevent the write. What does exit 2 actually accomplish on this event, and what is it for?
2. The hook must not run the linter on every write in the repo. What is the cheapest test on the payload that decides whether to run it at all?
3. The linter prints its findings on stdout and signals with its exit code. Which stream must the hook print them on, and why is that different from the linter's own choice?
4. The tests need to point this hook at a fixture tree instead of the real project. What is the least intrusive way to make the lint root overridable?

Two or three sentences each. No code yet.
```

**Finding:** On question 1 Claude should say exit 2 cannot undo the write; it feeds stderr back to Claude so the next turn repairs the file, which makes `PostToolUse` a correction loop rather than a gate. On question 2 it should propose a substring test on the file path, before spawning any subprocess. Question 3 is the one to check carefully: the hook must print on stderr, because Claude Code parses a hook's stdout as JSON control output, so a linter's plain text on stdout is either ignored or misread. On question 4 an environment variable with a sensible default is the expected answer, matching `HOOK_AUDIT_LOG` from the sibling demo.

**Recipe:**

```text
Create hooks/lint_skills.py in demos/02-harness/03-hooks/skill-guard/.

Behaviour:
- Read one JSON object from stdin. If tool_name is not Write or Edit, exit 0.
- Take tool_input.file_path and normalise it to POSIX form. If it contains neither ".claude/skills/" nor ".claude/agents/", exit 0.
- Resolve the lint root from the HOOK_LINT_ROOT environment variable, defaulting to the project folder resolved relative to the script file.
- Run scripts/lint-claude-config.sh against that root with subprocess.
- If the linter exits 0, print "[lint] skill and agent config clean" to stderr and exit 0.
- Otherwise print the linter's stdout to stderr and exit 2.

Portability constraint: invoke bash with a script path relative to the lint root and pass "." as the argument, with cwd set to the lint root. Do not pass absolute paths to bash. The bash at Git\usr\bin\bash.exe on Windows rejects a drive-letter path like D:/repo/scripts/lint.sh and exits 127.

Constraints: Python standard library only, no try/except. Comment only a line a reader cannot decode at a glance, one short line above it.
```

**Expected Outcome:** Pointing the hook at the broken fixture prints the full issue list on stderr and exits 2:

```text
Skills (./.claude/skills):
  [!] angular-conventions: nested manifest 'forms/SKILL.md' — leaves must be references/<leaf>.md (no frontmatter), or a top-level peer skill; never a nested SKILL.md
  [!] angular-conventions: reference 'references/signals.md' has name/description frontmatter — references must be plain docs so they are not discovered as skills
  [!] orphan-notes: manifest is 'skill.md' — must be 'SKILL.md' (breaks on case-sensitive FS)
Agents (./.claude/agents):
  [!] mystery-agent: empty 'description:' (agent cannot be auto-routed)

4 issue(s) found. Fix before relying on skill discovery / auto-delegation.
exit=2
```

Pointing it at the clean fixture prints `[lint] skill and agent config clean` and exits 0, and a write to `src/app.py` prints nothing and exits 0 without ever spawning bash.

---

## Step 4: Wire Both Layers in settings.json

**Overview:** Two hooks on two different events guard the same convention from opposite sides. Wiring them is where the matcher shape matters, because a group placed under the wrong event turns a blocker into a report that arrives too late.

**Research / Planning / Discussion:**

```text
Read .claude/settings.json in this folder, which currently holds an empty hooks object.

Then explain, using the Claude Code hooks documentation:
1. What is the nesting order from the "hooks" key down to a single command entry?
2. Both of my hooks use the matcher "Write|Edit". What does that string match against, and what happens if I put block_nested_skill.py under PostToolUse by mistake?
3. Both hooks re-check tool_name themselves even though the matcher already filters. Why keep that check?
4. What is $CLAUDE_PROJECT_DIR and why is it safer in a command string than a relative path like python hooks/foo.py?

Do not edit the file yet.
```

**Finding:** Claude should describe the nesting as `hooks` object, then event name, then a list of groups, then each group's `matcher` plus a `hooks` array of `type: "command"` entries. On question 2 the point to land is that the blocker under `PostToolUse` would still print its reason but the nested `SKILL.md` would already exist on disk, turning prevention into cleanup. On question 3 a good answer notes that a matcher is a convenience of the wiring, not a property of the script, and that the tests call the scripts directly. On question 4 it should say a hook's working directory is not guaranteed to be the project root.

**Recipe:**

```text
Update .claude/settings.json in demos/02-harness/03-hooks/skill-guard/ so it wires both hooks.

- A PreToolUse group with matcher "Write|Edit" running hooks/block_nested_skill.py.
- A PostToolUse group with matcher "Write|Edit" running hooks/lint_skills.py.

Every command must be of the form: python "$CLAUDE_PROJECT_DIR/hooks/<script>.py"
Use the object-keyed hooks shape: hooks -> event name -> list of groups -> matcher plus a hooks array of {"type": "command", "command": ...}.

Then confirm it is valid JSON by parsing it with python -m json.tool.
```

**Expected Outcome:** `.claude/settings.json` holds a `hooks` object with one `PreToolUse` group and one `PostToolUse` group, each with matcher `Write|Edit`. `python -m json.tool .claude/settings.json` exits 0 and echoes the formatted document.

---

## Step 5: Prove Both Layers with Exit-Code Tests

**Overview:** A guard that has never been proven is a guard you discover was silent during the one session it mattered. The shipped harness already runs the linter against a fixture and pipes JSON into a hook, so the remaining work is asserting the contract each layer promises, including the paths that must stay allowed.

**Research / Planning / Discussion:**

```text
Read tests/hook_harness.py and tests/test_lint_script.py in this folder.

Then plan the coverage for the two hooks I just built:
1. Which exit code does each hook assert, and which cases must assert exit 0 so the guard does not become a wall?
2. block_nested_skill.py blocks on exit 2. Besides the exit code and the stderr text, what else should the test assert about the process output?
3. lint_skills.py shells out to a linter. Which mechanism did I already build in to point it at a fixture instead of the real project, and why does that matter for test isolation?
4. What is the one negative case that proves lint_skills.py does not run the linter on every write in the repo?

List the test cases you would write, one line each. Do not write the tests yet.
```

**Finding:** Claude should propose an allow case for every block case: a legal root `SKILL.md`, a plain reference, a file outside `skills/`, and a non-`Write` tool. On question 2 it must assert stdout is empty, since exit 2 discards stdout and any content there would be a latent bug once a hook starts emitting JSON control output. On question 3 it should reach for `HOOK_LINT_ROOT` pointed at `fixtures/`. On question 4 the case to look for is a write to `src/app.py` asserting exit 0 and empty stderr; if Claude's plan lacks a negative case, say so, because a hook that lints on every write turns every file change into a bash spawn.

**Recipe:**

```text
Add two test modules to demos/02-harness/03-hooks/skill-guard/tests/, following the style of test_lint_script.py and importing run_hook from hook_harness.

tests/test_block_nested_skill.py:
- a root .claude/skills/angular-conventions/SKILL.md passes with exit 0 and empty stderr
- a plain references/forms.md passes with exit 0
- a nested forms/SKILL.md blocks with exit 2, and stderr names the replacement path .claude/skills/angular-conventions/references/forms.md
- a lowercase root skill.md blocks with exit 2 and stderr says it must be named SKILL.md
- a references/signals.md whose content carries name and description frontmatter blocks with exit 2
- a write to src/app.py passes with exit 0
- a Bash call against the nested path is ignored with exit 0
- the blocked case writes nothing to stdout

tests/test_lint_skills.py (set HOOK_LINT_ROOT to a fixtures path per case):
- a skill write against fixtures/clean exits 0 and reports "skill and agent config clean"
- a skill write against fixtures/broken exits 2, stderr contains "nested manifest 'forms/SKILL.md'" and "4 issue(s) found", and stdout is empty
- a write to .claude/agents/mystery-agent.md against fixtures/broken also exits 2
- a write to src/app.py against fixtures/broken exits 0 with empty stderr

Constraints: standard library unittest only, no inline comments. Then run: python -m unittest discover -s tests -v
```

**Expected Outcome:** The suite grows from 3 tests to 14 and passes:

```text
----------------------------------------------------------------------
Ran 14 tests in 1.141s

OK
```

Your timing will differ. The completed reference, with both hooks and the full settings wiring, is in [skill-guard-solution/](skill-guard-solution/readme.md).

---

## Step 6: Promote the Guard to Every Repository

**Overview:** A convention that only holds in the repo where you wrote the hook is a convention you will break in the next repo. Hooks resolve through the same settings hierarchy as everything else in the harness, so moving the guard to user scope makes it apply everywhere without touching a single project.

**Research / Planning / Discussion:**

```text
I want this guard to apply to every repository I open, not just this one.

Reason through what changes:
1. Which settings file holds user-scope hooks, and how do its hook entries combine with a project's own .claude/settings.json: replace, merge, or run both?
2. $CLAUDE_PROJECT_DIR points at the project being worked on, not at my home folder. What does that mean for a command string in a user-scope hook that must reach a script living outside every project?
3. The linter lints the project's .claude folder. When the hook runs from user scope against an arbitrary repo, what should the lint root be, and which payload field gives it?
4. What is the failure mode of a user-scope PreToolUse blocker that is too strict, and what makes this particular one safe to run everywhere?

Two or three sentences each.
```

**Finding:** Claude should say user-scope hooks live in `~/.claude/settings.json` and that hook groups from both scopes are collected and run, so a project cannot silently disable a user-scope guard. On question 2 it must conclude that the command needs an absolute path to a script kept outside the project, typically under `~/.claude/scripts/`, because `$CLAUDE_PROJECT_DIR` moves with each repo. On question 3 the answer is the payload's `cwd`. On question 4 the point to land is blast radius: a global blocker fires in every repo, so its match must be narrow, and this one only triggers on paths already inside `.claude/skills/`, which no repo has by accident.

**Recipe:**

```text
Show me how to promote this guard from project scope to user scope, without changing what it does.

1. Copy scripts/lint-claude-config.sh and both hooks from demos/02-harness/03-hooks/skill-guard/ to ~/.claude/scripts/ and ~/.claude/hooks/, printing the copy commands for both bash and PowerShell.
2. Show the hooks block I would add to ~/.claude/settings.json, using absolute paths under $HOME rather than $CLAUDE_PROJECT_DIR, and explain in one sentence why.
3. Change lint_skills.py so the lint root comes from the payload's cwd when HOOK_LINT_ROOT is not set, so it lints whichever repo is open. Show the diff only.
4. Tell me the one command that verifies the user-scope hook is registered and its script is reachable.

Do not modify anything under ~/.claude yet; show me the commands and the diff first.
```

**Expected Outcome:** Claude prints the copy commands, a `~/.claude/settings.json` hooks block whose commands use absolute `$HOME` paths, and a small diff replacing the `HOOK_LINT_ROOT` default with the payload's `cwd`. For verification it should name `/doctor`, which reports registered hooks and flags a command whose script cannot be found. Apply the change only if you want the guard active in every repo; the demo is complete either way.

