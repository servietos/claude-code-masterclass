import unittest

from hook_harness import run_hook


def payload(tool_name, file_path):
    return {
        "session_id": "abc123",
        "cwd": "/repo",
        "hook_event_name": "PreToolUse",
        "tool_name": tool_name,
        "tool_input": {"file_path": file_path},
    }


class ProtectPathsTest(unittest.TestCase):
    def test_allows_ordinary_source_file(self):
        code, _, stderr = run_hook("protect_paths.py", payload("Write", "/repo/src/app.py"))
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")

    def test_blocks_generated_docs(self):
        code, _, stderr = run_hook("protect_paths.py", payload("Write", "/repo/docs/generated/api.md"))
        self.assertEqual(code, 2)
        self.assertIn("docs/generated/api.md", stderr)
        self.assertIn("docs/generated/*", stderr)

    def test_blocks_lockfile_edit(self):
        code, _, stderr = run_hook("protect_paths.py", payload("Edit", "/repo/package-lock.lock"))
        self.assertEqual(code, 2)
        self.assertIn("*.lock", stderr)

    def test_ignores_unrelated_tools(self):
        code, _, stderr = run_hook("protect_paths.py", payload("Bash", "/repo/docs/generated/api.md"))
        self.assertEqual(code, 0)
        self.assertEqual(stderr, "")

    def test_block_writes_nothing_to_stdout(self):
        _, stdout, _ = run_hook("protect_paths.py", payload("Write", "/repo/docs/generated/api.md"))
        self.assertEqual(stdout, "")


if __name__ == "__main__":
    unittest.main()
