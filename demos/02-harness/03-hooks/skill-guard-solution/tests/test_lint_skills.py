import unittest
from pathlib import Path

from hook_harness import run_hook

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures"


def payload(file_path, tool="Write"):
    return {
        "session_id": "abc123",
        "cwd": "/repo",
        "hook_event_name": "PostToolUse",
        "tool_name": tool,
        "tool_input": {"file_path": file_path},
        "tool_response": {"file_path": file_path},
    }


SKILL_WRITE = payload("/repo/.claude/skills/angular-conventions/references/forms.md")


class LintSkillsTest(unittest.TestCase):
    def test_clean_tree_exits_zero(self):
        code, _, stderr = run_hook(
            "lint_skills.py",
            SKILL_WRITE,
            env={"HOOK_LINT_ROOT": str(FIXTURES / "clean")},
        )
        self.assertEqual(code, 0)
        self.assertIn("skill and agent config clean", stderr)

    def test_broken_tree_blocks_and_reports_every_issue(self):
        code, stdout, stderr = run_hook(
            "lint_skills.py",
            SKILL_WRITE,
            env={"HOOK_LINT_ROOT": str(FIXTURES / "broken")},
        )
        self.assertEqual(code, 2)
        self.assertIn("nested manifest 'forms/SKILL.md'", stderr)
        self.assertIn("4 issue(s) found", stderr)
        self.assertEqual(stdout, "")

    def test_agent_write_also_triggers_the_lint(self):
        code, _, _ = run_hook(
            "lint_skills.py",
            payload("/repo/.claude/agents/mystery-agent.md"),
            env={"HOOK_LINT_ROOT": str(FIXTURES / "broken")},
        )
        self.assertEqual(code, 2)

    def test_unrelated_write_skips_the_lint(self):
        code, _, stderr = run_hook(
            "lint_skills.py",
            payload("/repo/src/app.py"),
            env={"HOOK_LINT_ROOT": str(FIXTURES / "broken")},
        )
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")


if __name__ == "__main__":
    unittest.main()
