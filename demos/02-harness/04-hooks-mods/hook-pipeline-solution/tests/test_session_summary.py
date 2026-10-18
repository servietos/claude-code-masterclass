import json
import tempfile
import unittest
from pathlib import Path

from hook_harness import run_hook

ROWS = [
    {"ts": "2026-10-17T10:00:00+00:00", "session_id": "abc123", "tool": "Write", "file_path": "src/a.py", "bytes": 3},
    {"ts": "2026-10-17T10:01:00+00:00", "session_id": "abc123", "tool": "Edit", "file_path": "src/a.py", "bytes": 5},
    {"ts": "2026-10-17T10:02:00+00:00", "session_id": "other", "tool": "Write", "file_path": "other.md", "bytes": 99},
]

STOP = {"session_id": "abc123", "hook_event_name": "Stop"}


class SessionSummaryTest(unittest.TestCase):
    def run_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            log = Path(tmp) / "audit.jsonl"
            log.write_text("".join(json.dumps(row) + "\n" for row in ROWS), encoding="utf-8")
            _, _, stderr = run_hook("session_summary.py", STOP, {"HOOK_AUDIT_LOG": str(log)})
        return stderr

    def test_header_counts_only_this_session(self):
        self.assertIn("[summary] session abc123: 2 writes, 1 files, 8 bytes", self.run_summary())

    def test_lists_tool_counts(self):
        stderr = self.run_summary()
        self.assertIn("  Write x1", stderr)
        self.assertIn("  Edit x1", stderr)

    def test_never_mentions_other_session(self):
        stderr = self.run_summary()
        self.assertNotIn("other.md", stderr)
        self.assertNotIn("99", stderr)


if __name__ == "__main__":
    unittest.main()
