"""CJG/play_session_logging: エッジケース（非 aware datetime / 重複 start / 未開始 end）。

根拠:
- docs/customer-journeys.md CJ43（実プレイの記録）
- steering/done/20260422-play-session-ip-ua-browser.md

start_session を同じ ID で 2 回呼んでも 2 重行にならない（INSERT OR IGNORE）。
heartbeat_session / end_session は存在しない ID に対して silent no-op。
naive datetime（tzinfo なし）は UTC 扱いで保存される。
"""

from __future__ import annotations

import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services import play_session_logging as psl


class DuplicateStartTest(unittest.TestCase):
    def test_same_session_id_inserted_twice_does_not_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            base = datetime(2026, 4, 25, 12, 0, 0, tzinfo=timezone.utc)

            psl.start_session(db, session_id="s1", page_kind="production", started_at=base)
            psl.start_session(
                db, session_id="s1", page_kind="production",
                started_at=base + timedelta(seconds=60),
            )

            with sqlite3.connect(db) as conn:
                rows = conn.execute(
                    "SELECT COUNT(*) FROM play_sessions WHERE session_id = 's1'"
                ).fetchone()
            self.assertEqual(rows[0], 1)


class OrphanEventsTest(unittest.TestCase):
    def test_heartbeat_on_unknown_session_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            base = datetime(2026, 4, 25, 12, 0, 0, tzinfo=timezone.utc)

            # 例外を投げなければ合格
            psl.heartbeat_session(db, session_id="nonexistent", seen_at=base)

    def test_end_on_unknown_session_is_noop(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            base = datetime(2026, 4, 25, 12, 0, 0, tzinfo=timezone.utc)

            psl.end_session(
                db, session_id="nonexistent", ended_at=base, ended_cleanly=True,
            )


class NaiveDatetimeTest(unittest.TestCase):
    def test_naive_datetime_is_normalized_to_utc(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"
            # naive datetime (tzinfo なし)
            naive = datetime(2026, 4, 25, 12, 0, 0)

            psl.start_session(db, session_id="s1", page_kind="production", started_at=naive)

            summary = psl.summarize_sessions(db)
            self.assertEqual(len(summary), 1)
            self.assertEqual(summary[0]["date"], "2026-04-25")


class SummarizeEmptyTest(unittest.TestCase):
    def test_empty_db_returns_empty_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"

            summary = psl.summarize_sessions(db)

            self.assertEqual(summary, [])

    def test_empty_db_browser_summary_is_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "test.sqlite3"

            browser = psl.summarize_sessions_by_browser(db)

            self.assertEqual(browser, [])


if __name__ == "__main__":
    unittest.main()
