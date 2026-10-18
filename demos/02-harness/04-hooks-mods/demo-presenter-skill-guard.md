---
presents: demo-skill-guard.md
budget: 4 min
beats: 4
---

# Present: Enforce a Skill Folder Convention with Hooks

A blocker and a linter built around one skill-folder convention, each tested against a broken fixture tree. A room walks away seeing prevention and correction as two layers, and knowing why a block message has to spell out the fix.

------

## Beats

### Beat 1: a block that only says no costs a turn (1 min)

**Open:** [`block_nested_skill.py`](skill-guard-solution/hooks/block_nested_skill.py) · the nested-manifest branch and its stderr message · [`fixtures/broken/.claude/skills/angular-conventions/forms/SKILL.md`](skill-guard-solution/fixtures/broken/.claude/skills/angular-conventions/forms/SKILL.md)
**Say:** A refusal is the input to the next attempt. A message citing the rule buys a question; a message naming the corrected shape buys the fix.

```python
if name.lower() == "skill.md" and len(tail) > 2:
    block(
        f"nested subskill manifest {path}: write .claude/skills/{skill}/references/{nested}.md instead, "
        f"or promote it to a top-level skill folder"
    )
```

**Result:** no file, a refusal: piping a nested manifest in produces exit 2 and a reason that names the replacement path

```text
nested subskill manifest .claude/skills/angular-conventions/forms/SKILL.md: write .claude/skills/angular-conventions/references/forms.md instead, or promote it to a top-level skill folder
exit=2
```

**Gotcha:** that is the whole reason exit 2 feeds stderr to Claude: the next turn should be the fix.

### Beat 2: `content` exists on a Write and not on an Edit (1 min)

**Open:** [`block_nested_skill.py`](skill-guard-solution/hooks/block_nested_skill.py) · the `references` branch reading `tool_input.content` · [`fixtures/broken/.claude/skills/angular-conventions/references/signals.md`](skill-guard-solution/fixtures/broken/.claude/skills/angular-conventions/references/signals.md) · [`fixtures/clean/.claude/skills/angular-conventions/references/signals.md`](skill-guard-solution/fixtures/clean/.claude/skills/angular-conventions/references/signals.md)
**Say:** A rule that reads a file is bounded by what the payload carries, and that varies with the tool. Discovery frontmatter is what promotes a file into a skill, so a reference carrying it competes with its own master.

```python
if nested == "references" and name.endswith(".md") and has_identity_frontmatter(tool_input.get("content", "")):
    block(
        f"{path}: a reference must stay a plain document, because frontmatter with a name or description "
        f"makes it get discovered as its own skill"
    )
```

**Result:** no file, two exit codes: the broken fixture's `references/signals.md` blocks with exit 2, and the clean fixture's copy of the same path produces no output and exit 0

**Gotcha:** an `Edit` carries `old_string` and `new_string`, so `content` is on a Write alone. Correct anyone who claims it is on both payloads.

### Beat 3: `PostToolUse` catches what never went through the tool layer (1 min)

**Open:** [`lint_skills.py`](skill-guard-solution/hooks/lint_skills.py) · the path filter and the two exit branches · [`skill-guard/.claude/settings.json`](skill-guard/.claude/settings.json) · the starter's empty `hooks` block
**Say:** A guard wired to a tool event sees only what passed through that tool, and a shell command or a git pull does not. Prevention and detection cover different populations of change.

```python
if ".claude/skills/" not in path and ".claude/agents/" not in path:
    sys.exit(0)
...
if result.returncode == 0:
    print("[lint] skill and agent config clean", file=sys.stderr)
    sys.exit(0)

# exit 2 makes Claude Code refuse the write and show stderr to Claude
print(result.stdout, file=sys.stderr)
sys.exit(2)
```

**Result:** the run wired both layers in [`skill-guard-solution/.claude/settings.json`](skill-guard-solution/.claude/settings.json), and pointed at the broken fixture the hook re-emits the whole issue list on stderr and exits 2

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

**Gotcha:** the linter's stdout is re-emitted on stderr because Claude Code parses a hook's stdout as JSON control output, where plain text is ignored or misread.

### Beat 4: the case that proves the sweep stays cheap (1 min)

**Open:** [`tests/test_lint_skills.py`](skill-guard-solution/tests/test_lint_skills.py) · `test_non_skill_path_is_not_linted` · [`fixtures/broken`](skill-guard-solution/fixtures/broken)
**Say:** A short-circuit is a behavioural claim, so it needs proving. Point the expensive path at data that would certainly fail, then assert nothing happened.

```python
    def test_non_skill_path_is_not_linted(self):
        code, _, stderr = run_hook(
            "lint_skills.py",
            write_payload("src/app.py"),
            env={"HOOK_LINT_ROOT": fixture_root("broken")},
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")
```

**Result:** two test modules the starter has no counterpart for, in [`skill-guard-solution/tests`](skill-guard-solution/tests), and the whole suite green

```text
----------------------------------------------------------------------
Ran 11 tests in 1.032s

OK
```

**Gotcha:** the lint root is deliberately the broken fixture, so this case only passes if the path filter short-circuits before the linter ever runs.

## If the room asks

| Question | Answer |
|---|---|
| Why not just run the linter and skip the blocker? | The linter reports a violation already on disk; the blocker refuses the write, so the nested `SKILL.md` never lands. |
| Is a lowercase `skill.md` really a defect? | Yes, it resolves on case-insensitive Windows and macOS volumes and vanishes on a case-sensitive filesystem, so it breaks in CI. |
