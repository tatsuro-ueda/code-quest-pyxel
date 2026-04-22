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
        from src.shared.services import play_session_logging
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(
            f"src.shared.services.play_session_logging is missing: {exc}"
        ) from exc
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
            page_kind="production",
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
                    "page_kind": "production",
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
            page_kind="production",
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
            page_kind="production",
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
            page_kind="development",
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
                    "page_kind": "development",
                    "session_count": 1,
                    "avg_active_seconds": 300,
                    "short_sessions": 0,
                    "middle_sessions": 0,
                    "long_sessions": 1,
                },
                {
                    "date": "2026-04-13",
                    "page_kind": "production",
                    "session_count": 2,
                    "avg_active_seconds": 179,
                    "short_sessions": 0,
                    "middle_sessions": 2,
                    "long_sessions": 0,
                },
            ],
        )

    def test_ip_address_and_user_agent_are_persisted(self):
        self.mod.start_session(
            self.db_path,
            session_id="s-meta",
            page_kind="production",
            started_at=self.base,
            ip_address="203.0.113.42",
            user_agent="Mozilla/5.0 (TestAgent) Chrome/120",
        )

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT ip_address, user_agent FROM play_sessions WHERE session_id = ?",
                ("s-meta",),
            ).fetchone()
        self.assertEqual(row, ("203.0.113.42", "Mozilla/5.0 (TestAgent) Chrome/120"))

    def test_start_session_without_metadata_stores_null(self):
        self.mod.start_session(
            self.db_path,
            session_id="s-plain",
            page_kind="production",
            started_at=self.base,
        )

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT ip_address, user_agent FROM play_sessions WHERE session_id = ?",
                ("s-plain",),
            ).fetchone()
        self.assertEqual(row, (None, None))

    def test_existing_db_without_metadata_columns_is_migrated(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE play_sessions (
                    session_id TEXT PRIMARY KEY,
                    page_kind TEXT NOT NULL,
                    started_at TEXT NOT NULL,
                    last_seen_at TEXT NOT NULL,
                    ended_at TEXT,
                    active_seconds INTEGER NOT NULL DEFAULT 0,
                    ended_cleanly INTEGER NOT NULL DEFAULT 0
                )
                """
            )

        self.mod.start_session(
            self.db_path,
            session_id="s-migrated",
            page_kind="production",
            started_at=self.base,
            ip_address="198.51.100.7",
            user_agent="Mozilla/5.0 (Migrated)",
        )

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT ip_address, user_agent FROM play_sessions WHERE session_id = ?",
                ("s-migrated",),
            ).fetchone()
        self.assertEqual(row, ("198.51.100.7", "Mozilla/5.0 (Migrated)"))

    def test_browser_summary_classifies_known_user_agents(self):
        cases = [
            ("s-chrome", "Mozilla/5.0 Chrome/120 Safari/537"),
            ("s-edge", "Mozilla/5.0 Chrome/120 Edg/120"),
            ("s-safari", "Mozilla/5.0 (iPhone) Version/17 Safari/604"),
            ("s-firefox", "Mozilla/5.0 Firefox/125"),
            ("s-unknown", ""),
        ]
        for idx, (session_id, ua) in enumerate(cases):
            self.mod.start_session(
                self.db_path,
                session_id=session_id,
                page_kind="production",
                started_at=self.base + timedelta(minutes=idx),
                user_agent=ua or None,
            )

        summary = {
            row["browser"]: row["session_count"]
            for row in self.mod.summarize_sessions_by_browser(self.db_path)
        }
        self.assertEqual(summary.get("Chrome"), 1)
        self.assertEqual(summary.get("Edge"), 1)
        self.assertEqual(summary.get("Safari"), 1)
        self.assertEqual(summary.get("Firefox"), 1)
        self.assertEqual(summary.get("Unknown"), 1)

    def test_last_seen_time_is_used_when_end_event_never_arrives(self):
        self.mod.start_session(
            self.db_path,
            session_id="s-open",
            page_kind="production",
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
