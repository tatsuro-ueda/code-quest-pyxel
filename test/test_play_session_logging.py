from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_logging_module():
    try:
        from src import play_session_logging
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"src.play_session_logging is missing: {exc}") from exc
    return play_session_logging


class PlaySessionLoggingTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "play_sessions.sqlite3"
        self.base = datetime(2026, 4, 13, 12, 0, 0, tzinfo=timezone.utc)
        self.mod = load_logging_module()

    def tearDown(self):
        self.tmp.cleanup()

    def test_short_session_under_60_seconds_is_classified_as_short(self):
        self.mod.start_session(
            self.db_path,
            session_id="s-short",
            page_kind="current",
            started_at=self.base,
        )
        self.mod.end_session(
            self.db_path,
            session_id="s-short",
            ended_at=self.base + timedelta(seconds=59),
            ended_cleanly=True,
        )

        summary = self.mod.summarize_sessions(self.db_path)

        self.assertEqual(
            summary,
            [
                {
                    "date": "2026-04-13",
                    "page_kind": "current",
                    "session_count": 1,
                    "avg_active_seconds": 59,
                    "short_sessions": 1,
                    "middle_sessions": 0,
                    "long_sessions": 0,
                }
            ],
        )

    def test_boundary_values_split_middle_and_long_correctly(self):
        self.mod.start_session(
            self.db_path,
            session_id="s-60",
            page_kind="current",
            started_at=self.base,
        )
        self.mod.end_session(
            self.db_path,
            session_id="s-60",
            ended_at=self.base + timedelta(seconds=60),
            ended_cleanly=True,
        )
        self.mod.start_session(
            self.db_path,
            session_id="s-299",
            page_kind="current",
            started_at=self.base + timedelta(minutes=10),
        )
        self.mod.end_session(
            self.db_path,
            session_id="s-299",
            ended_at=self.base + timedelta(minutes=10, seconds=299),
            ended_cleanly=True,
        )
        self.mod.start_session(
            self.db_path,
            session_id="s-300",
            page_kind="preview",
            started_at=self.base + timedelta(minutes=20),
        )
        self.mod.end_session(
            self.db_path,
            session_id="s-300",
            ended_at=self.base + timedelta(minutes=25),
            ended_cleanly=True,
        )

        summary = self.mod.summarize_sessions(self.db_path)

        self.assertEqual(
            summary,
            [
                {
                    "date": "2026-04-13",
                    "page_kind": "current",
                    "session_count": 2,
                    "avg_active_seconds": 179,
                    "short_sessions": 0,
                    "middle_sessions": 2,
                    "long_sessions": 0,
                },
                {
                    "date": "2026-04-13",
                    "page_kind": "preview",
                    "session_count": 1,
                    "avg_active_seconds": 300,
                    "short_sessions": 0,
                    "middle_sessions": 0,
                    "long_sessions": 1,
                },
            ],
        )

    def test_last_seen_time_is_used_when_end_event_never_arrives(self):
        self.mod.start_session(
            self.db_path,
            session_id="s-open",
            page_kind="current",
            started_at=self.base,
        )
        self.mod.heartbeat_session(
            self.db_path,
            session_id="s-open",
            seen_at=self.base + timedelta(seconds=45),
        )

        summary = self.mod.summarize_sessions(self.db_path)

        self.assertEqual(summary[0]["avg_active_seconds"], 45)
        self.assertEqual(summary[0]["short_sessions"], 1)

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT ended_cleanly, active_seconds
                FROM play_sessions
                WHERE session_id = ?
                """,
                ("s-open",),
            ).fetchone()
        self.assertEqual(row, (0, 45))


if __name__ == "__main__":
    unittest.main()
