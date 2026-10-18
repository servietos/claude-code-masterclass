import json
import tempfile
import unittest
from pathlib import Path

from hook_harness import run_hook

FIRST = {
    "session_id": "abc123",
    "tool_name": "Write",
    "tool_input": {"file_path": "src/a.py"},
    "tool_response": {"content": "print(1)"},
}

SECOND = {
    "session_id": "abc123",
    "tool_name": "Edit",
    "tool_input": {"file_path": "src/b.py"},
    "tool_response": {"content": "print(22)"},
}


class AuditWriteTest(unittest.TestCase):
    def test_two_calls_append_two_lines_with_correct_second_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "audit.jsonl"
            env = {"HOOK_AUDIT_LOG": str(log)}
            run_hook("audit_write.py", FIRST, env)
            run_hook("audit_write.py", SECOND, env)
            lines = log.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual(json.loads(lines[1])["bytes"], len(SECOND["tool_response"]["content"]))


if __name__ == "__main__":
    unittest.main()
