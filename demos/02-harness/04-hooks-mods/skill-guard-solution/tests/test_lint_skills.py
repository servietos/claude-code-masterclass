import os
import unittest

from hook_harness import PROJECT, run_hook


def write_payload(file_path):
    return {"tool_name": "Write", "tool_input": {"file_path": file_path, "content": ""}}


def fixture_root(name):
    return os.path.join(PROJECT, "fixtures", name)


class LintSkillsTest(unittest.TestCase):
    def test_clean_fixture_passes_silently_with_message(self):
        code, _, stderr = run_hook(
            "lint_skills.py",
            write_payload(".claude/skills/angular-conventions/SKILL.md"),
            env={"HOOK_LINT_ROOT": fixture_root("clean")},
        )
        self.assertEqual(code, 0)
        self.assertIn("skill and agent config clean", stderr)

    def test_broken_fixture_blocks_with_issue_list(self):
        code, stdout, stderr = run_hook(
            "lint_skills.py",
            write_payload(".claude/skills/angular-conventions/SKILL.md"),
            env={"HOOK_LINT_ROOT": fixture_root("broken")},
        )
        self.assertEqual(code, 2)
        self.assertIn("nested manifest 'forms/SKILL.md'", stderr)
        self.assertIn("4 issue(s) found", stderr)
        self.assertEqual(stdout, "")

    def test_non_skill_path_is_not_linted(self):
        code, _, stderr = run_hook(
            "lint_skills.py",
            write_payload("src/app.py"),
            env={"HOOK_LINT_ROOT": fixture_root("broken")},
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
