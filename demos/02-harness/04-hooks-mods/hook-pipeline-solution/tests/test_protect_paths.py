import unittest

from hook_harness import run_hook

PAYLOAD = {
    "session_id": "abc123",
    "cwd": "/repo",
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {"file_path": "/repo/docs/generated/api.md", "content": "# api"},
}


class ProtectPathsTest(unittest.TestCase):
    def test_blocks_generated_docs_with_exit_two(self):
        code, _, _ = run_hook("protect_paths.py", PAYLOAD)
        self.assertEqual(code, 2)

    def test_stderr_names_path_and_pattern(self):
        _, _, stderr = run_hook("protect_paths.py", PAYLOAD)
        self.assertIn("docs/generated/api.md", stderr)
        self.assertIn("docs/generated/*", stderr)

    def test_blocked_call_writes_nothing_to_stdout(self):
        _, stdout, _ = run_hook("protect_paths.py", PAYLOAD)
        self.assertEqual(stdout, "")


if __name__ == "__main__":
    unittest.main()
