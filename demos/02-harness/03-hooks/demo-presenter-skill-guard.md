---
presents: demo-skill-guard.md
budget: 6 min
beats: 6
---

# Present: Enforce a Skill Folder Convention with Hooks

A blocker and a linter built around one skill-folder convention, each tested against a broken fixture tree. A room walks away seeing prevention and correction as two layers, and knowing why a block message has to spell out the fix.

------

## Beats

### Beat 1: the convention is a path rule, so it needs no filesystem access (1 min)

**Open:** [`block_nested_skill.py`](skill-guard-solution/hooks/block_nested_skill.py) · the `tail` slice and the `len(tail) < 2` guard · [`fixtures/clean/.claude/skills/angular-conventions/SKILL.md`](skill-guard-solution/fixtures/clean/.claude/skills/angular-conventions/SKILL.md)
**Say:** Some conventions are settled entirely by where a file sits, which is what makes a check on every write affordable. A guard must recognise what is none of its business as confidently as a violation.

```python
tail = parts[root + 2:]

if len(tail) < 2:
    sys.exit(0)

skill = tail[0]
leaf = tail[-1]
```

**Result:** [`tests/test_block_nested_skill.py`](skill-guard-solution/tests/test_block_nested_skill.py) pins both halves; the starter ships no `hooks/` folder for either

```python
    def test_root_manifest_passes(self):
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            payload("/repo/.claude/skills/angular-conventions/SKILL.md"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
```

**Gotcha:** everything the blocker decides comes from counting segments after `skills`: exactly two is a legal master, and anything longer ending in a manifest is a nested subskill.

### Beat 2: a block that only says no costs a turn (1 min)

**Open:** [`block_nested_skill.py`](skill-guard-solution/hooks/block_nested_skill.py) · the nested-manifest branch and its stderr message · [`fixtures/broken/.claude/skills/angular-conventions/forms/SKILL.md`](skill-guard-solution/fixtures/broken/.claude/skills/angular-conventions/forms/SKILL.md)
**Say:** A refusal is the input to the next attempt, not the end of one. A message citing the rule buys a question; a message naming the corrected shape buys the fix.

```python
if leaf.lower() == "skill.md" and len(tail) > 2:
    nested = "/".join(tail[1:-1])
    print(
        f"Blocked: {target} is a nested subskill manifest. A master skill holds exactly one "
        f"SKILL.md at its root, so write .claude/skills/{skill}/references/{nested}.md as a plain "
        "reference instead, or promote the capability to its own top-level skill folder.",
        file=sys.stderr,
    )
    # exit 2 is the only code that blocks the write, any other non-zero code just warns
    sys.exit(2)
```

**Result:** no file, a refusal: piping a nested manifest in produces exit 2 and a reason that names the replacement path

```text
Blocked: .claude/skills/angular-conventions/forms/SKILL.md is a nested subskill manifest. A master skill holds exactly one SKILL.md at its root, so write .claude/skills/angular-conventions/references/forms.md as a plain reference instead, or promote the capability to its own top-level skill folder.
exit=2
```

**Gotcha:** that is the whole reason exit 2 feeds stderr to Claude: the next turn should be the fix, not a question.

### Beat 3: `content` exists on a Write and not on an Edit (1 min)

**Open:** [`block_nested_skill.py`](skill-guard-solution/hooks/block_nested_skill.py) · the `references` branch reading `tool_input.content` · [`fixtures/broken/.claude/skills/angular-conventions/references/signals.md`](skill-guard-solution/fixtures/broken/.claude/skills/angular-conventions/references/signals.md) · [`fixtures/clean/.claude/skills/angular-conventions/references/signals.md`](skill-guard-solution/fixtures/clean/.claude/skills/angular-conventions/references/signals.md)
**Say:** A rule that reads a file is bounded by what the payload carries, and that varies with the tool. Discovery frontmatter is what promotes a file into a skill, so a reference carrying it competes with its own master.

```python
if tail[1:2] == ["references"] and leaf.endswith(".md"):
    content = tool_input.get("content", "")
    lines = content.splitlines()
    if lines[:1] == ["---"]:
        block = lines[1:]
        end = block.index("---") if "---" in block else len(block)
        keys = [line.split(":", 1)[0].strip().lower() for line in block[:end] if ":" in line]
        found = [key for key in ("name", "description") if key in keys]
```

**Result:** no file, two exit codes: the broken fixture's `references/signals.md` blocks with exit 2, and the clean fixture's copy of the same path produces no output and exit 0

**Gotcha:** an `Edit` carries `old_string` and `new_string` instead of `content`, so correct anyone who claims `content` is on both payloads.

### Beat 4: `PostToolUse` catches what never went through the tool layer (1 min)

**Open:** [`lint_skills.py`](skill-guard-solution/hooks/lint_skills.py) · the path filter and the two exit branches · [`skill-guard/.claude/settings.json`](skill-guard/.claude/settings.json) · the starter's empty `hooks` block
**Say:** A guard wired to a tool event sees only what passed through that tool, and a shell command or a git pull does not. Prevention and detection cover different populations of change.

```python
if ".claude/skills/" not in target and ".claude/agents/" not in target:
    sys.exit(0)
...
if result.returncode == 0:
    print("[lint] skill and agent config clean", file=sys.stderr)
    sys.exit(0)

# stdout is parsed as json control output, so the linter's report has to be re-emitted on stderr
print(result.stdout.strip(), file=sys.stderr)
# exit 2 cannot undo the write, it hands that report to claude so the next turn repairs it
sys.exit(2)
```

**Result:** the run wired both layers in [`skill-guard-solution/.claude/settings.json`](skill-guard-solution/.claude/settings.json), and pointed at the broken fixture the hook re-emits the whole issue list on stderr and exits 2

```text
Skills (./.claude/skills):
  [!] angular-conventions: nested manifest 'forms/SKILL.md' — leaves must be references/<leaf>.md (no frontmatter), or a top-level peer skill; never a nested SKILL.md
...
4 issue(s) found. Fix before relying on skill discovery / auto-delegation.
exit=2
```

**Gotcha:** the linter's stdout is re-emitted on stderr because Claude Code parses a hook's stdout as JSON control output, where plain text is ignored or misread.

### Beat 5: the portability trap is real, and it exits 127 (1 min)

**Open:** [`lint_skills.py`](skill-guard-solution/hooks/lint_skills.py) · the `subprocess.run` call with `cwd=root` · [`scripts/lint-claude-config.sh`](skill-guard-solution/scripts/lint-claude-config.sh) · [`fixtures/clean`](skill-guard-solution/fixtures/clean)
**Say:** A hook that shells out inherits every assumption of the shell it invokes, and on a mixed team that shell is not the same program on every machine. A guard that runs on only some machines is worse than none.

```python
root = Path(os.environ.get("HOOK_LINT_ROOT", PROJECT))
# relative and posix, because the bash shipped with git for windows rejects a drive-letter path with exit 127
linter = Path(os.path.relpath(LINTER, root)).as_posix()
result = subprocess.run(
    ["bash", linter, "."],
    cwd=root,
    capture_output=True,
    text=True,
)
```

**Result:** no file, the clean verdict: pointed at the clean fixture the same hook prints `[lint] skill and agent config clean` and exits 0

**Gotcha:** the obvious implementation passes an absolute script path to bash and fails on a common Windows setup, where the `bash` shipped at `Git\usr\bin\bash.exe` rejects a drive-letter path like `D:/repo/scripts/lint.sh` with exit 127.

### Beat 6: the case that proves the sweep stays cheap (1 min)

**Open:** [`tests/test_lint_skills.py`](skill-guard-solution/tests/test_lint_skills.py) · `test_unrelated_write_skips_the_lint` · [`fixtures/broken`](skill-guard-solution/fixtures/broken)
**Say:** A short-circuit is a behavioural claim, so it needs proving. Point the expensive path at data that would certainly fail, then assert nothing happened.

```python
    def test_unrelated_write_skips_the_lint(self):
        code, _, stderr = run_hook(
            "lint_skills.py",
            payload("/repo/src/app.py"),
            env={"HOOK_LINT_ROOT": str(FIXTURES / "broken")},
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
```

**Result:** two test modules the starter has no counterpart for, in [`skill-guard-solution/tests`](skill-guard-solution/tests), and the whole suite green

```text
----------------------------------------------------------------------
Ran 14 tests in 1.141s

OK
```

**Gotcha:** the lint root is deliberately the broken fixture, so this case only passes if the path filter short-circuits before the linter ever runs.

## If the room asks

| Question | Answer |
|---|---|
| Why not just run the linter and skip the blocker? | The linter reports a violation already on disk; the blocker refuses the write, so the nested `SKILL.md` never lands. |
| Is a lowercase `skill.md` really a defect? | Yes, it resolves on case-insensitive Windows and macOS volumes and vanishes on a case-sensitive filesystem, so it breaks in CI. |
| Can I promote this guard to every repo? | Yes, user-scope hooks live in `~/.claude/settings.json` and both scopes' groups run; use absolute `$HOME` script paths, since `$CLAUDE_PROJECT_DIR` moves per repo. |
