from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from src.play_session_logging import end_session, start_session


def load_report_module():
    try:
        import report_play_sessions
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/report_play_sessions.py is missing: {exc}") from exc
    return report_play_sessions


class ReportPlaySessionsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "play_sessions.sqlite3"
        self.base = datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc)
        self.report_mod = load_report_module()

    def tearDown(self):
        self.tmp.cleanup()

    def seed_sessions(self):
        start_session(
            self.db_path,
            session_id="short-current",
            page_kind="current",
            started_at=self.base,
        )
        end_session(
            self.db_path,
            session_id="short-current",
            ended_at=self.base + timedelta(seconds=45),
            ended_cleanly=True,
        )
        start_session(
            self.db_path,
            session_id="long-preview",
            page_kind="preview",
            started_at=self.base + timedelta(hours=1),
        )
        end_session(
            self.db_path,
            session_id="long-preview",
            ended_at=self.base + timedelta(hours=1, seconds=360),
            ended_cleanly=True,
        )

    def test_render_summary_includes_counts_and_buckets(self):
        self.seed_sessions()
        rows = self.report_mod.summarize_sessions(self.db_path)

        rendered = self.report_mod.render_summary(rows)

        self.assertIn("2026-04-13", rendered)
        self.assertIn("current", rendered)
        self.assertIn("preview", rendered)
        self.assertIn("short=1", rendered)
        self.assertIn("long=1", rendered)
        self.assertIn("avg=45s", rendered)
        self.assertIn("avg=360s", rendered)

    def test_main_prints_empty_message_when_no_sessions_exist(self):
        stdout = io.StringIO()

        with redirect_stdout(stdout):
            self.report_mod.main(["--db-path", str(self.db_path)])

        self.assertIn("No play sessions recorded.", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
