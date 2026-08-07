import json
import tempfile
import unittest
from pathlib import Path

from hook_harness import run_hook

ROWS = [
    {"ts": "2026-01-01T00:00:00+00:00", "session_id": "abc123", "tool": "Write", "file_path": "/repo/src/a.py", "bytes": 3},
    {"ts": "2026-01-01T00:00:01+00:00", "session_id": "abc123", "tool": "Edit", "file_path": "/repo/src/a.py", "bytes": 5},
    {"ts": "2026-01-01T00:00:02+00:00", "session_id": "other", "tool": "Write", "file_path": "/repo/src/z.py", "bytes": 9},
]


class SessionSummaryTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.log = Path(self.tmp.name) / "audit.jsonl"
        self.env = {"HOOK_AUDIT_LOG": str(self.log)}

    def tearDown(self):
        self.tmp.cleanup()

    def write_log(self):
        self.log.write_text("\n".join(json.dumps(row) for row in ROWS) + "\n", encoding="utf-8")

    def test_summarises_only_the_current_session(self):
        self.write_log()
        code, _, stderr = run_hook("session_summary.py", {"session_id": "abc123", "hook_event_name": "Stop"}, env=self.env)
        self.assertEqual(code, 0)
        self.assertIn("2 writes, 1 files, 8 bytes", stderr)
        self.assertIn("Write x1", stderr)
        self.assertIn("Edit x1", stderr)
        self.assertNotIn("/repo/src/z.py", stderr)

    def test_reports_empty_session(self):
        self.write_log()
        _, _, stderr = run_hook("session_summary.py", {"session_id": "nothing", "hook_event_name": "Stop"}, env=self.env)
        self.assertIn("no file writes recorded", stderr)

    def test_missing_log_is_not_an_error(self):
        code, _, stderr = run_hook("session_summary.py", {"session_id": "abc123", "hook_event_name": "Stop"}, env=self.env)
        self.assertEqual(code, 0)
        self.assertIn("no file writes recorded", stderr)


if __name__ == "__main__":
    unittest.main()
