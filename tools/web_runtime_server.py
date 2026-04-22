from __future__ import annotations

import argparse
import json
from datetime import datetime
import http.server
from pathlib import Path
import sys
from typing import Callable


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.codemaker_resource_store import (
    import_codemaker_resource_zip,
    load_imported_resource_manifest,
)
from src.shared.services.play_session_logging import (
    end_session,
    heartbeat_session,
    start_session,
)


def _parse_timestamp(raw: str) -> datetime:
    return datetime.fromisoformat(raw)


def _client_ip(request: http.server.BaseHTTPRequestHandler) -> str | None:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip() or None
    try:
        return request.client_address[0]
    except (AttributeError, IndexError):
        return None


def rebuild_after_codemaker_resource_import(project_root: Path) -> dict[str, object]:
    from tools.build_web_release import build_development_release, build_web_release

    try:
        build_development_release(project_root)
        return {
            "development_available": True,
            "development_play_url": "/development/play.html",
        }
    except ValueError:
        build_web_release(project_root)
        return {
            "development_available": False,
            "development_play_url": None,
        }


def _make_handler(
    serve_dir: Path,
    db_path: Path,
    *,
    project_root: Path,
    on_codemaker_resource_import: Callable[[Path], dict[str, object]] | None,
) -> type[http.server.SimpleHTTPRequestHandler]:
    class WebRuntimeHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(serve_dir), **kwargs)

        def do_GET(self) -> None:
            route = self.path.split("?", 1)[0]
            if route == "/internal/codemaker-resource-import/status":
                self._handle_codemaker_import_status()
                return
            super().do_GET()

        def do_POST(self) -> None:
            routes = {
                "/internal/play-sessions/start": self._handle_start,
                "/internal/play-sessions/heartbeat": self._handle_heartbeat,
                "/internal/play-sessions/end": self._handle_end,
                "/internal/codemaker-resource-import": self._handle_codemaker_resource_import,
            }
            route = self.path.split("?", 1)[0]
            handler = routes.get(route)
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

        def _read_raw_body(self) -> bytes:
            length = int(self.headers.get("Content-Length", "0"))
            return self.rfile.read(length) if length else b""

        def _send_json(self, payload: dict[str, object], *, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _handle_start(self) -> None:
            payload = self._read_json_body()
            start_session(
                db_path,
                session_id=str(payload["session_id"]),
                page_kind=str(payload["page_kind"]),
                started_at=_parse_timestamp(str(payload["started_at"])),
                ip_address=_client_ip(self),
                user_agent=self.headers.get("User-Agent"),
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

        def _handle_codemaker_import_status(self) -> None:
            manifest = load_imported_resource_manifest(project_root)
            payload: dict[str, object] = {
                "available": True,
                "has_imported_resource": manifest is not None,
            }
            if manifest is not None:
                payload.update(
                    {
                        "source_name": manifest.get("source_name", ""),
                        "ignored_code_entries": manifest.get("ignored_code_entries", []),
                        "changed_from_base": bool(manifest.get("changed_from_base", False)),
                        "imported_at": manifest.get("imported_at", ""),
                    }
                )
            self._send_json(payload)

        def _handle_codemaker_resource_import(self) -> None:
            archive_bytes = self._read_raw_body()
            filename = self.headers.get("X-Filename", "code-maker.zip")
            try:
                payload = import_codemaker_resource_zip(
                    project_root,
                    archive_bytes,
                    source_name=filename,
                )
            except ValueError as exc:
                self._send_json({"error": str(exc)}, status=400)
                return

            if on_codemaker_resource_import is not None:
                payload.update(on_codemaker_resource_import(project_root))
            self._send_json(payload)

    return WebRuntimeHandler


def make_server(
    serve_dir: Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8000,
    db_path: Path | None = None,
    project_root: Path | None = None,
    on_codemaker_resource_import: Callable[[Path], dict[str, object]] | None = rebuild_after_codemaker_resource_import,
) -> http.server.ThreadingHTTPServer:
    serve_dir = Path(serve_dir).resolve()
    db_path = (db_path or (ROOT / ".runtime" / "play_sessions.sqlite3")).resolve()
    project_root = (project_root or ROOT).resolve()
    handler = _make_handler(
        serve_dir,
        db_path,
        project_root=project_root,
        on_codemaker_resource_import=on_codemaker_resource_import,
    )
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
