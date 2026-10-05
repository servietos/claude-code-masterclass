# Skill Guard Solution

The completed reference for [../demo-skill-guard.md](../demo-skill-guard.md): both hooks, the full `.claude/settings.json` wiring, and 14 passing tests.

## What is here

| Path | Purpose |
|------|---------|
| `hooks/block_nested_skill.py` | `PreToolUse` blocker: nested `SKILL.md`, lowercase `skill.md`, and frontmatter in a reference all exit 2 |
| `hooks/lint_skills.py` | `PostToolUse` hook: runs the linter when a skill or agent file changes, exits 2 with the issue list |
| `scripts/lint-claude-config.sh` | The linter both the hook and the tests call |
| `fixtures/clean/`, `fixtures/broken/` | A correct skill tree and the same tree carrying one of each defect |
| `.claude/settings.json` | Wires the blocker to `PreToolUse` and the linter to `PostToolUse`, both with matcher `Write|Edit` |
| `tests/` | The harness plus three test modules covering the linter and both hooks |

## Run the tests

```bash
python -m unittest discover -s tests -v
```

```text
Ran 14 tests in 1.141s

OK
```

## The two layers

The blocker is preventive and content-aware: it reads `tool_input.content` and refuses the write before it lands, so a nested subskill never reaches disk. The linter is a sweep: it runs after the write and catches everything the blocker cannot see, including defects introduced by a shell command, a file copy, or an editor outside the session. Exit 2 on `PostToolUse` does not undo the write; it feeds the issue list back to Claude so the next turn repairs it.

## Portability note

`lint_skills.py` invokes the linter with a relative script path and `cwd` set to the lint root. The `bash` shipped at `Git\usr\bin\bash.exe` on Windows rejects drive-letter paths like `D:/repo/scripts/lint.sh` with exit 127, so an absolute path works on Linux and macOS and fails on a common Windows setup.
