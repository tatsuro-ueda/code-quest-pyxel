from __future__ import annotations

import io
import json
import sys
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path
from zipfile import ZipFile


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
        self.project_root = Path(self.tmp.name) / "project"
        self.serve_dir = Path(self.tmp.name) / "public"
        self.serve_dir.mkdir(parents=True, exist_ok=True)
        (self.project_root / "assets").mkdir(parents=True, exist_ok=True)
        (self.project_root / "assets" / "blockquest.pyxres").write_bytes(b"base-resource")
        (self.serve_dir / "play.html").write_text("<h1>play wrapper</h1>", encoding="utf-8")
        self.db_path = Path(self.tmp.name) / "play_sessions.sqlite3"
        self.import_calls: list[Path] = []
        self.server_mod = load_server_module()
        from src.shared.services.play_session_logging import summarize_sessions

        self.summarize_sessions = summarize_sessions
        try:
            self.server = self.server_mod.make_server(
                self.serve_dir,
                host="127.0.0.1",
                port=0,
                db_path=self.db_path,
                project_root=self.project_root,
                on_codemaker_resource_import=self.on_codemaker_resource_import,
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

    def on_codemaker_resource_import(self, project_root: Path) -> dict[str, object]:
        self.import_calls.append(project_root)
        return {
            "development_available": True,
            "development_play_url": "/development/play.html",
        }

    def post_json(self, path: str, payload: dict[str, object]):
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        return urllib.request.urlopen(request, timeout=5)

    def post_zip(self, path: str, payload: bytes, *, filename: str = "code-maker.zip"):
        request = urllib.request.Request(
            self.base_url + path,
            data=payload,
            headers={
                "Content-Type": "application/zip",
                "X-Filename": filename,
            },
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
                "page_kind": "production",
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
                    "page_kind": "production",
                    "session_count": 1,
                    "avg_active_seconds": 70,
                    "short_sessions": 0,
                    "middle_sessions": 1,
                    "long_sessions": 0,
                }
            ],
        )

    def test_start_records_client_ip_and_user_agent(self):
        import sqlite3

        request = urllib.request.Request(
            self.base_url + "/internal/play-sessions/start",
            data=json.dumps(
                {
                    "session_id": "session-meta",
                    "page_kind": "production",
                    "started_at": "2026-04-13T12:00:00+00:00",
                }
            ).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (TestClient) Chrome/120",
                "X-Forwarded-For": "203.0.113.9, 10.0.0.1",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            self.assertEqual(response.status, 204)

        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT ip_address, user_agent FROM play_sessions WHERE session_id = ?",
                ("session-meta",),
            ).fetchone()
        self.assertEqual(row, ("203.0.113.9", "Mozilla/5.0 (TestClient) Chrome/120"))

    def test_start_falls_back_to_peer_ip_without_forwarded_header(self):
        import sqlite3

        with self.post_json(
            "/internal/play-sessions/start",
            {
                "session_id": "session-peer",
                "page_kind": "production",
                "started_at": "2026-04-13T12:00:00+00:00",
            },
        ) as response:
            self.assertEqual(response.status, 204)

        with sqlite3.connect(self.db_path) as conn:
            ip_address, user_agent = conn.execute(
                "SELECT ip_address, user_agent FROM play_sessions WHERE session_id = ?",
                ("session-peer",),
            ).fetchone()
        self.assertEqual(ip_address, "127.0.0.1")
        self.assertIsNotNone(user_agent)

    def test_accepts_codemaker_zip_and_imports_only_resource(self):
        payload = io.BytesIO()
        with ZipFile(payload, "w") as zf:
            zf.writestr("block-quest/main.py", "print('ignored code')\n")
            zf.writestr("block-quest/my_resource.pyxres", b"edited-resource")

        with self.post_zip("/internal/codemaker-resource-import", payload.getvalue()) as response:
            body = json.loads(response.read().decode("utf-8"))

        imported_path = self.project_root / ".runtime" / "codemaker_resource_imports" / "development" / "my_resource.pyxres"
        manifest_path = self.project_root / ".runtime" / "codemaker_resource_imports" / "development.json"

        self.assertEqual(response.status, 200)
        self.assertEqual(imported_path.read_bytes(), b"edited-resource")
        self.assertTrue(manifest_path.exists())
        self.assertEqual(body["ignored_code_entries"], ["block-quest/main.py"])
        self.assertTrue(body["changed_from_base"])
        self.assertEqual(body["development_play_url"], "/development/play.html")
        self.assertEqual(self.import_calls, [self.project_root])

    def test_reports_codemaker_import_status(self):
        status_url = self.base_url + "/internal/codemaker-resource-import/status"

        with urllib.request.urlopen(status_url, timeout=5) as response:
            before = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, 200)
        self.assertFalse(before["has_imported_resource"])

        payload = io.BytesIO()
        with ZipFile(payload, "w") as zf:
            zf.writestr("block-quest/main.py", "print('ignored code')\n")
            zf.writestr("block-quest/my_resource.pyxres", b"edited-resource")
        with self.post_zip("/internal/codemaker-resource-import", payload.getvalue()):
            pass

        with urllib.request.urlopen(status_url, timeout=5) as response:
            after = json.loads(response.read().decode("utf-8"))

        self.assertEqual(response.status, 200)
        self.assertTrue(after["has_imported_resource"])
        self.assertEqual(after["ignored_code_entries"], ["block-quest/main.py"])
        self.assertEqual(after["source_name"], "code-maker.zip")


if __name__ == "__main__":
    unittest.main()
