import json
import tempfile
import unittest
from pathlib import Path

from hook_harness import run_hook


def payload(tool_name, file_path, content):
    return {
        "session_id": "abc123",
        "cwd": "/repo",
        "hook_event_name": "PostToolUse",
        "tool_name": tool_name,
        "tool_input": {"file_path": file_path},
        "tool_response": {"file_path": file_path, "content": content},
    }


class AuditWriteTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = Path(self.tmp.name) / "logs" / "audit.jsonl"
        self.env = {"HOOK_AUDIT_LOG": str(self.log)}

    def tearDown(self):
        self.tmp.cleanup()

    def read_lines(self):
        return [json.loads(line) for line in self.log.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_appends_one_line_per_write(self):
        run_hook("audit_write.py", payload("Write", "/repo/src/a.py", "abc"), env=self.env)
        run_hook("audit_write.py", payload("Edit", "/repo/src/b.py", "defgh"), env=self.env)
        entries = self.read_lines()
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]["tool"], "Write")
        self.assertEqual(entries[1]["bytes"], 5)

    def test_entry_carries_the_contract_fields(self):
        run_hook("audit_write.py", payload("Write", "/repo/src/a.py", "abc"), env=self.env)
        entry = self.read_lines()[0]
        self.assertEqual(set(entry), {"ts", "session_id", "tool", "file_path", "bytes"})
        self.assertEqual(entry["session_id"], "abc123")
        self.assertEqual(entry["file_path"], "/repo/src/a.py")

    def test_never_blocks(self):
        code, _, _ = run_hook("audit_write.py", payload("Write", "/repo/src/a.py", "abc"), env=self.env)
        self.assertEqual(code, 0)

    def test_skips_non_write_tools(self):
        code, _, _ = run_hook("audit_write.py", payload("Bash", "", ""), env=self.env)
        self.assertEqual(code, 0)
        self.assertFalse(self.log.exists())


if __name__ == "__main__":
    unittest.main()
