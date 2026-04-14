from __future__ import annotations

import json
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def load_server_module():
    try:
        import web_runtime_server
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/web_runtime_server.py is missing: {exc}") from exc
    return web_runtime_server


class WebRuntimeServerTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.serve_dir = Path(self.tmp.name) / "public"
        self.serve_dir.mkdir(parents=True, exist_ok=True)
        (self.serve_dir / "play.html").write_text("<h1>play wrapper</h1>", encoding="utf-8")
        self.db_path = Path(self.tmp.name) / "play_sessions.sqlite3"
        self.server_mod = load_server_module()
        from src.play_session_logging import summarize_sessions

        self.summarize_sessions = summarize_sessions
        try:
            self.server = self.server_mod.make_server(
                self.serve_dir,
                host="127.0.0.1",
                port=0,
                db_path=self.db_path,
            )
        except PermissionError as exc:
            self.tmp.cleanup()
            self.skipTest(f"socket creation is not allowed in this sandbox: {exc}")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)
        self.tmp.cleanup()

    def post_json(self, path: str, payload: dict[str, object]):
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urllib.request.urlopen(request, timeout=5)

    def test_serves_static_files_from_same_server(self):
        with urllib.request.urlopen(self.base_url + "/play.html", timeout=5) as response:
            content = response.read().decode("utf-8")

        self.assertEqual(response.status, 200)
        self.assertIn("play wrapper", content)

    def test_accepts_play_session_events_and_updates_summary(self):
        with self.post_json(
            "/internal/play-sessions/start",
            {
                "session_id": "session-1",
                "page_kind": "current",
                "started_at": "2026-04-13T12:00:00+00:00",
            },
        ) as response:
            self.assertEqual(response.status, 204)

        with self.post_json(
            "/internal/play-sessions/heartbeat",
            {
                "session_id": "session-1",
                "seen_at": "2026-04-13T12:00:45+00:00",
            },
        ) as response:
            self.assertEqual(response.status, 204)

        with self.post_json(
            "/internal/play-sessions/end",
            {
                "session_id": "session-1",
                "ended_at": "2026-04-13T12:01:10+00:00",
                "ended_cleanly": True,
            },
        ) as response:
            self.assertEqual(response.status, 204)

        summary = self.summarize_sessions(self.db_path)

        self.assertEqual(
            summary,
            [
                {
                    "date": "2026-04-13",
                    "page_kind": "current",
                    "session_count": 1,
                    "avg_active_seconds": 70,
                    "short_sessions": 0,
                    "middle_sessions": 1,
                    "long_sessions": 0,
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
