import unittest

from hook_harness import run_hook

PAYLOAD = {
    "session_id": "abc123",
    "cwd": "/repo",
    "hook_event_name": "PreToolUse",
    "tool_name": "Write",
    "tool_input": {"file_path": "/repo/src/app.py", "content": "print(1)"},
}


class InspectPayloadTest(unittest.TestCase):
    def test_allows_every_call(self):
        code, _, _ = run_hook("inspect_payload.py", PAYLOAD)
        self.assertEqual(code, 0)

    def test_reports_contract_fields_on_stderr(self):
        _, _, stderr = run_hook("inspect_payload.py", PAYLOAD)
        self.assertIn("event=PreToolUse", stderr)
        self.assertIn("session=abc123", stderr)
        self.assertIn("tool=Write", stderr)
        self.assertIn("tool_input_keys=content,file_path", stderr)

    def test_stdout_stays_empty_so_exit_zero_json_parsing_sees_nothing(self):
        _, stdout, _ = run_hook("inspect_payload.py", PAYLOAD)
        self.assertEqual(stdout, "")


if __name__ == "__main__":
    unittest.main()
