import unittest

from hook_harness import run_hook


def payload(file_path, content="", tool="Write"):
    return {
        "session_id": "abc123",
        "cwd": "/repo",
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "tool_input": {"file_path": file_path, "content": content},
    }


REFERENCE_WITH_FRONTMATTER = """---
name: angular-signals
description: Signal-based state management.
---

# Signals
"""


class BlockNestedSkillTest(unittest.TestCase):
    def test_root_manifest_passes(self):
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            payload("/repo/.claude/skills/angular-conventions/SKILL.md"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")

    def test_plain_reference_passes(self):
        code, _, _ = run_hook(
            "block_nested_skill.py",
            payload(
                "/repo/.claude/skills/angular-conventions/references/forms.md",
                "# Forms\n\nBuild typed reactive forms.\n",
            ),
        )
        self.assertEqual(code, 0)

    def test_nested_manifest_blocks_and_names_the_reference_path(self):
        code, stdout, stderr = run_hook(
            "block_nested_skill.py",
            payload("/repo/.claude/skills/angular-conventions/forms/SKILL.md"),
        )
        self.assertEqual(code, 2)
        self.assertIn("nested subskill manifest", stderr)
        self.assertIn(".claude/skills/angular-conventions/references/forms.md", stderr)
        self.assertEqual(stdout, "")

    def test_lowercase_root_manifest_blocks(self):
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            payload("/repo/.claude/skills/orphan-notes/skill.md"),
        )
        self.assertEqual(code, 2)
        self.assertIn("must be named SKILL.md", stderr)

    def test_reference_with_frontmatter_blocks(self):
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            payload(
                "/repo/.claude/skills/angular-conventions/references/signals.md",
                REFERENCE_WITH_FRONTMATTER,
            ),
        )
        self.assertEqual(code, 2)
        self.assertIn("name and description frontmatter", stderr)

    def test_file_outside_skills_passes(self):
        code, _, _ = run_hook("block_nested_skill.py", payload("/repo/src/app.py", "print(1)"))
        self.assertEqual(code, 0)

    def test_bash_call_is_ignored(self):
        code, _, _ = run_hook(
            "block_nested_skill.py",
            payload("/repo/.claude/skills/angular-conventions/forms/SKILL.md", tool="Bash"),
        )
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
