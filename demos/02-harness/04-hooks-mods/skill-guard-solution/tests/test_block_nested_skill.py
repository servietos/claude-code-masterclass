import unittest

from hook_harness import run_hook


def write_payload(file_path, content=""):
    return {"tool_name": "Write", "tool_input": {"file_path": file_path, "content": content}}


class BlockNestedSkillTest(unittest.TestCase):
    def test_root_manifest_passes(self):
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            write_payload(".claude/skills/angular-conventions/SKILL.md", "---\nname: angular-conventions\n---\n"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")

    def test_nested_manifest_blocks_and_names_replacement(self):
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            write_payload(".claude/skills/angular-conventions/forms/SKILL.md"),
        )
        self.assertEqual(code, 2)
        self.assertIn(".claude/skills/angular-conventions/references/forms.md", stderr)

    def test_lowercase_root_manifest_blocks(self):
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            write_payload(".claude/skills/angular-conventions/skill.md"),
        )
        self.assertEqual(code, 2)
        self.assertIn("name the manifest SKILL.md", stderr)

    def test_reference_with_frontmatter_blocks(self):
        content = "---\nname: signals\ndescription: Signal patterns\n---\n# Signals\n"
        code, _, stderr = run_hook(
            "block_nested_skill.py",
            write_payload(".claude/skills/angular-conventions/references/signals.md", content),
        )
        self.assertEqual(code, 2)
        self.assertIn("plain document", stderr)

    def test_blocked_write_prints_nothing_to_stdout(self):
        code, stdout, _ = run_hook(
            "block_nested_skill.py",
            write_payload(".claude/skills/angular-conventions/forms/SKILL.md"),
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")


if __name__ == "__main__":
    unittest.main()
