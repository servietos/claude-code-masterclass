import unittest

from hook_harness import run_linter


class LintScriptTest(unittest.TestCase):
    def test_clean_fixture_passes(self):
        code, stdout, _ = run_linter("clean")
        self.assertEqual(code, 0)
        self.assertIn("no skill/agent config defects found", stdout)

    def test_broken_fixture_fails_with_four_issues(self):
        code, stdout, _ = run_linter("broken")
        self.assertEqual(code, 1)
        self.assertIn("4 issue(s) found", stdout)

    def test_broken_fixture_names_every_defect(self):
        _, stdout, _ = run_linter("broken")
        self.assertIn("nested manifest 'forms/SKILL.md'", stdout)
        self.assertIn("reference 'references/signals.md'", stdout)
        self.assertIn("manifest is 'skill.md'", stdout)
        self.assertIn("mystery-agent: empty 'description:'", stdout)


if __name__ == "__main__":
    unittest.main()
