from __future__ import annotations

import argparse
import json
from datetime import datetime
import http.server
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.play_session_logging import end_session, heartbeat_session, start_session


def _parse_timestamp(raw: str) -> datetime:
    return datetime.fromisoformat(raw)


def _make_handler(serve_dir: Path, db_path: Path) -> type[http.server.SimpleHTTPRequestHandler]:
    class WebRuntimeHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(serve_dir), **kwargs)

        def do_POST(self) -> None:
            routes = {
                "/internal/play-sessions/start": self._handle_start,
                "/internal/play-sessions/heartbeat": self._handle_heartbeat,
                "/internal/play-sessions/end": self._handle_end,
            }
            handler = routes.get(self.path)
            if handler is None:
                self.send_error(404, "Not Found")
                return
            handler()

        def _read_json_body(self) -> dict[str, object]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            return json.loads(raw) if raw else {}

        def _send_no_content(self) -> None:
            self.send_response(204)
            self.end_headers()

        def _handle_start(self) -> None:
            payload = self._read_json_body()
            start_session(
                db_path,
                session_id=str(payload["session_id"]),
                page_kind=str(payload["page_kind"]),
                started_at=_parse_timestamp(str(payload["started_at"])),
            )
            self._send_no_content()

        def _handle_heartbeat(self) -> None:
            payload = self._read_json_body()
            heartbeat_session(
                db_path,
                session_id=str(payload["session_id"]),
                seen_at=_parse_timestamp(str(payload["seen_at"])),
            )
            self._send_no_content()

        def _handle_end(self) -> None:
            payload = self._read_json_body()
            end_session(
                db_path,
                session_id=str(payload["session_id"]),
                ended_at=_parse_timestamp(str(payload["ended_at"])),
                ended_cleanly=bool(payload["ended_cleanly"]),
            )
            self._send_no_content()

    return WebRuntimeHandler


def make_server(
    serve_dir: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    db_path: Path | None = None,
) -> http.server.ThreadingHTTPServer:
    serve_dir = Path(serve_dir).resolve()
    db_path = (db_path or (ROOT / ".runtime" / "play_sessions.sqlite3")).resolve()
    handler = _make_handler(serve_dir, db_path)
    return http.server.ThreadingHTTPServer((host, port), handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="Serve Block Quest web files and internal play session logging")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--serve-dir", default=str(ROOT))
    parser.add_argument("--db-path", default=str(ROOT / ".runtime" / "play_sessions.sqlite3"))
    args = parser.parse_args()

    server = make_server(
        Path(args.serve_dir),
        host=args.host,
        port=args.port,
        db_path=Path(args.db_path),
    )
    print(f"Serving {Path(args.serve_dir).resolve()} on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
