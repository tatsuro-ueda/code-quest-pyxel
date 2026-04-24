"""CJG/report: report_play_sessions のレンダラー。

根拠:
- steering/done/20260422-play-session-ip-ua-browser.md（SQLite ログ分析）

render_summary / render_browser_summary は dict のリストを文字列に整形する
純粋関数。行数が rows と一致し、各行に expected な key/value が含まれる。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from tools.report_play_sessions import render_browser_summary, render_summary


class RenderSummaryTest(unittest.TestCase):
    def test_empty_rows_returns_placeholder_string(self):
        result = render_summary([])

        self.assertIn("No play sessions", result)

    def test_single_row_rendering(self):
        rows = [{
            "date": "2026-04-25",
            "page_kind": "production",
            "session_count": 5,
            "avg_active_seconds": 120,
            "short_sessions": 2,
            "middle_sessions": 2,
            "long_sessions": 1,
        }]

        result = render_summary(rows)

        self.assertIn("2026-04-25", result)
        self.assertIn("production", result)
        self.assertIn("sessions=5", result)
        self.assertIn("avg=120s", result)

    def test_multi_row_rendering_joins_with_newlines(self):
        rows = [
            {
                "date": "2026-04-25",
                "page_kind": "production",
                "session_count": 1,
                "avg_active_seconds": 10,
                "short_sessions": 1,
                "middle_sessions": 0,
                "long_sessions": 0,
            },
            {
                "date": "2026-04-25",
                "page_kind": "development",
                "session_count": 2,
                "avg_active_seconds": 30,
                "short_sessions": 0,
                "middle_sessions": 2,
                "long_sessions": 0,
            },
        ]

        result = render_summary(rows)

        self.assertEqual(result.count("\n"), 1)  # 2 行 → 改行 1 つ
        self.assertIn("production", result)
        self.assertIn("development", result)


class RenderBrowserSummaryTest(unittest.TestCase):
    def test_empty_rows_returns_placeholder(self):
        result = render_browser_summary([])

        self.assertIn("No browser data", result)

    def test_renders_browser_counts(self):
        rows = [
            {"browser": "Chrome", "session_count": 15, "avg_active_seconds": 200},
            {"browser": "Safari", "session_count": 3, "avg_active_seconds": 100},
        ]

        result = render_browser_summary(rows)

        self.assertIn("Chrome", result)
        self.assertIn("sessions=15", result)
        self.assertIn("avg=200s", result)
        self.assertIn("Safari", result)


if __name__ == "__main__":
    unittest.main()
