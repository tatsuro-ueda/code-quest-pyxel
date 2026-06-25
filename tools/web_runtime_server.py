"""Block Quest web 配信と play session 内部 API をまとめる HTTP サーバー。

このファイルに含まれる関数・クラス：

- rebuild_after_codemaker_resource_import: import 後に web 配信を再ビルドする
- make_server: ThreadingHTTPServer を組み立てて返すファクトリ
- ensure_dist_build: 起動時に dist/ artifacts が無ければビルドする systemd フック
- _WebRuntimeHandlerBase: Block Quest web 配信 + 内部 API を扱う handler の基底クラス
  - __init__: SimpleHTTPRequestHandler に serve_directory を渡して初期化する
  - do_GET: http.server 互換の GET ハンドラ（ルートだけ dispatch する）
  - do_POST: http.server 互換の POST ハンドラ（ルート別 handler に dispatch する）
  - _read_json_body: Content-Length 分だけ body を読み JSON として decode する
  - _send_no_content: 204 No Content を返す
  - _read_raw_body: Content-Length 分だけ raw body を読み bytes で返す
  - _send_json: payload を JSON にして指定 status で返す
  - _handle_start: /internal/play-sessions/start を SQLite に書く
  - _handle_heartbeat: /internal/play-sessions/heartbeat を更新する
  - _handle_end: /internal/play-sessions/end を確定する
  - _handle_codemaker_import_status: codemaker import 可否を返す
  - _handle_codemaker_resource_import: archive を取り込み再ビルドする
- run_main: CLI entry（systemd autostart / 手動起動共通）
- start_main_alias: 互換のため残す run_main の薄いエイリアス

Problems:
    - dev / prod の 2 系統サーバーを別々に走らせていたが、artifact が 1 本になっても
      手動起動と systemd autostart で挙動を分けると、リカバリ手順が増える。
    - Code Maker から resource を投入したあと、配信用 dist/ の再ビルドを
      別 CLI で叩く運用にしていると人為的なミスで「import したのに反映されない」事故が起きる。
    - HTTP handler の制御フローと play session SQLite I/O を 1 ファイルに直書きすると、
      ルーティングと永続化の責務が交差して読み解きづらい。

Solutions:
    - 単一 entry に統一し、make_server / ensure_dist_build / rebuild_after_*
      に役割を分けて systemd 起動と手動起動の差を消す。
    - resource import を受けたら自動で build_web_release を回し、API レスポンスに
      新しい play.html の URL を含めて返す。
    - HTTP handler は SimpleHTTPRequestHandler の派生 class に閉じ、
      JSON I/O とルート別 handler を private helper メソッドへ切り分ける。
"""
from __future__ import annotations

import argparse
import http.server
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.codemaker_resource_store import (  # noqa: E402
    apply_imported_resource,
)
from src.shared.services.play_session_logging import (  # noqa: E402
    end_session,
    heartbeat_session,
    start_session,
)


# === Public API ===


def rebuild_after_codemaker_resource_import(
        project_root: Path) -> dict[str, object]:
    """P3-E: import 後は本番を 1 本だけ再ビルドする（dev staging 廃止）。

    Args:
        project_root: リポジトリ root のパス。

    Returns:
        新しい dist play URL を含む dict（API レスポンスへ merge される）。

    Policy:
        - build_web_release 呼び出しと結果 dict 生成を private helper に委譲する。
    """
    return _run_rebuild_and_get_play_url(project_root)


def make_server(serve_dir: Path,
                *,
                host: str = "127.0.0.1",
                port: int = 8000,
                db_path: Path | None = None,
                project_root: Path | None = None,
                on_codemaker_resource_import: Callable[
                    [Path], dict[str, object]] | None
                = rebuild_after_codemaker_resource_import,
                ) -> http.server.ThreadingHTTPServer:  # noqa: CR100,CR202
    """ThreadingHTTPServer を組み立てて返す（std lib 互換シグネチャ）。

    Args:
        serve_dir: 静的ファイルを配信するディレクトリ。
        host: bind するホスト名。
        port: bind するポート番号。
        db_path: play_sessions SQLite のパス（None なら .runtime/ 下を既定）。
        project_root: リポジトリ root（None なら本ファイル基準の ROOT）。
        on_codemaker_resource_import: import 完了時に呼ぶ callback。

    Returns:
        起動準備済みの ThreadingHTTPServer。

    Policy:
        - default 引数解決と handler factory 呼び出しを private helper に委譲し、
          本体は値の組み立てと return のみで構成する。
    """
    return _assemble_threading_server(
        serve_dir,
        host=host,
        port=port,
        db_path=db_path,
        project_root=project_root,
        on_codemaker_resource_import=on_codemaker_resource_import,
    )


def ensure_dist_build(project_root: Path, serve_dir: Path) -> None:
    """起動時に dist/ artifacts が無ければビルドする（systemd autostart 用）。

    Args:
        project_root: リポジトリ root のパス。
        serve_dir: 静的ファイル配信ディレクトリ。

    Policy:
        - dist/index.html の存在判定とビルド実行を private helper に委譲する。
        - systemd で常駐させた際、fresh checkout や artifacts 未生成でも selector を
          配信できるよう、初回ビルドをここで走らせる。
    """
    _ensure_initial_dist_build(project_root, serve_dir)


def run_main() -> None:
    """CLI entry。引数解析と server 起動を順に行う。

    Policy:
        - 引数解析 → 初回ビルド → server 起動 → serve_forever ループの順に
          private helper へ委譲するステップ列。
    """
    args = _parse_main_args()
    _start_initial_build_if_needed(args)
    _start_serving(args)


def start_main_alias() -> None:
    """run_main の互換エイリアス（systemd unit や Make から呼ばれる経路を維持する）。

    Policy:
        - 実体は run_main に委譲する。
    """
    run_main()


# 既存呼び出し互換のための `main` 名（`from tools.web_runtime_server import main` 用）。
main = run_main  # noqa: E305


class _WebRuntimeHandlerBase(http.server.SimpleHTTPRequestHandler):
    """Block Quest web 配信 + 内部 API を扱う handler の基底クラス。"""

    # === Public API ===

    serve_directory: Path = Path(".")
    db_path: Path = Path(".")
    project_root: Path = Path(".")
    on_codemaker_resource_import: (
        Callable[[Path], dict[str, object]] | None) = None

    def __init__(self, *args, **kwargs):
        """SimpleHTTPRequestHandler に serve_directory を渡して初期化する。

        Args:
            *args: SimpleHTTPRequestHandler への位置引数。
            **kwargs: SimpleHTTPRequestHandler への kwargs。

        Policy:
            - directory 引数をクラス属性 serve_directory で固定する。
        """
        super().__init__(
            *args, directory=str(self.serve_directory), **kwargs)

    def do_GET(self) -> None:  # noqa: CR100,CR203,CR204
        """http.server 互換の GET ハンドラ（ルートだけ dispatch する）。

        Policy:
            - /internal/codemaker-resource-import/status 以外は親クラスに委ねる。
        """
        route = self.path.split("?", 1)[0]
        if route == "/internal/codemaker-resource-import/status":
            self._handle_codemaker_import_status()
            return
        self._apply_public_dist_alias(route)
        super().do_GET()

    def do_HEAD(self) -> None:
        """http.server 互換の HEAD ハンドラ（公開 alias だけ dispatch する）。"""
        route = self.path.split("?", 1)[0]
        self._apply_public_dist_alias(route)
        super().do_HEAD()

    def do_POST(self) -> None:  # noqa: CR100,CR203,CR204
        """http.server 互換の POST ハンドラ（ルート別 handler に dispatch する）。

        Policy:
            - 既知ルート以外は 404 を返す。
        """
        routes = {
            "/internal/play-sessions/start": self._handle_start,
            "/internal/play-sessions/heartbeat": self._handle_heartbeat,
            "/internal/play-sessions/end": self._handle_end,
            "/internal/codemaker-resource-import":
                self._handle_codemaker_resource_import,
        }
        route = self.path.split("?", 1)[0]
        handler = routes.get(route)
        if handler is None:
            self.send_error(404, "Not Found")
            return
        handler()

    # === Internal helpers (private) ===

    def _apply_public_dist_alias(self, route: str) -> None:
        """dist 内の公開 HTML をルート直下 URL でも配信する。"""
        if route != "/land-area-calculator.html":
            return
        self.path = self.path.replace(
            "/land-area-calculator.html",
            "/dist/land-area-calculator.html",
            1,
        )

    def _read_json_body(self) -> dict[str, object]:
        """Content-Length 分だけ body を読み JSON として decode する。

        Returns:
            decode 結果の dict（空 body のときは空 dict）。

        Policy:
            - Content-Length ヘッダが無いときは 0 として扱う。
        """
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def _send_no_content(self) -> None:
        """204 No Content を返す。

        Policy:
            - body は付けず、ヘッダだけで完結する。
        """
        self.send_response(204)
        self.end_headers()

    def _read_raw_body(self) -> bytes:
        """Content-Length 分だけ raw body を読み bytes で返す。

        Returns:
            read 結果の bytes（Content-Length が 0 のときは b""）。

        Policy:
            - JSON decode はしない。バイナリ archive の入力経路用。
        """
        length = int(self.headers.get("Content-Length", "0"))
        return self.rfile.read(length) if length else b""

    def _send_json(self,
                   payload: dict[str, object],
                   *,
                   status: int = 200) -> None:
        """payload を JSON にして指定 status で返す。

        Args:
            payload: JSON 化する dict。
            status: HTTP status code。

        Policy:
            - ensure_ascii=False で UTF-8 のまま送信する。
        """
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header(
            "Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _handle_start(self) -> None:
        """/internal/play-sessions/start: SQLite に session 開始行を入れる。

        Policy:
            - JSON body から session_id / page_kind / started_at を取り出して
              start_session に渡し、204 を返す。
        """
        payload = self._read_json_body()
        start_session(
            self.db_path,
            session_id=str(payload["session_id"]),
            page_kind=str(payload["page_kind"]),
            started_at=_parse_timestamp(str(payload["started_at"])),
            ip_address=_resolve_client_ip(self),
            user_agent=self.headers.get("User-Agent"),
        )
        self._send_no_content()

    def _handle_heartbeat(self) -> None:
        """/internal/play-sessions/heartbeat: heartbeat 行を更新する。

        Policy:
            - JSON body から session_id / seen_at を取り出して heartbeat_session
              に渡し、204 を返す。
        """
        payload = self._read_json_body()
        heartbeat_session(
            self.db_path,
            session_id=str(payload["session_id"]),
            seen_at=_parse_timestamp(str(payload["seen_at"])),
        )
        self._send_no_content()

    def _handle_end(self) -> None:
        """/internal/play-sessions/end: session 終了行を確定する。

        Policy:
            - ended_cleanly フラグを含めて end_session に委譲し、204 を返す。
        """
        payload = self._read_json_body()
        end_session(
            self.db_path,
            session_id=str(payload["session_id"]),
            ended_at=_parse_timestamp(str(payload["ended_at"])),
            ended_cleanly=bool(payload["ended_cleanly"]),
        )
        self._send_no_content()

    def _handle_codemaker_import_status(self) -> None:
        """/internal/codemaker-resource-import/status: import 可否を返す。

        Policy:
            - P3-E: staging 経路を廃止したので manifest は返さず、available のみ。
        """
        self._send_json({"available": True})

    def _handle_codemaker_resource_import(self) -> None:
        """/internal/codemaker-resource-import: archive を取り込み再ビルドする。

        Policy:
            - apply_imported_resource を呼んだあと、callback で再ビルドを発火する。
            - ValueError は 400 として返す。
        """
        archive_bytes = self._read_raw_body()
        filename = self.headers.get("X-Filename", "code-maker.zip")
        try:
            payload = apply_imported_resource(
                self.project_root,
                archive_bytes,
                source_name=filename,
            )
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=400)
            return

        callback = self.on_codemaker_resource_import
        if callback is not None:
            payload.update(callback(self.project_root))
        self._send_json(payload)


# === Internal helpers (private) ===


def _run_rebuild_and_get_play_url(project_root: Path) -> dict[str, object]:
    """build_web_release を呼んでから dist play URL dict を返す。

    Args:
        project_root: リポジトリ root のパス。

    Returns:
        dist_play_url キーのみを持つ dict。

    Policy:
        - tools.build_web_release は lazy import（循環回避と起動高速化）。
    """
    from tools.build_web_release import build_web_release

    build_web_release(project_root)
    return {
        "dist_play_url": "/dist/play.html",
    }


def _parse_timestamp(raw: str) -> datetime:
    """ISO8601 文字列を datetime に変換する。

    Args:
        raw: ISO8601 形式の日時文字列。

    Returns:
        変換済みの datetime（tz は文字列に従う）。

    Policy:
        - datetime.fromisoformat の薄いラッパ。
    """
    return datetime.fromisoformat(raw)


def _resolve_client_ip(
        request: http.server.BaseHTTPRequestHandler) -> str | None:
    """X-Forwarded-For ヘッダか client_address から IP 文字列を返す。

    Args:
        request: 処理中の HTTP request handler。

    Returns:
        IP アドレス文字列。取得できなければ None。

    Policy:
        - X-Forwarded-For があれば先頭エントリを採用し、無ければ socket の
          peer address に fallback する。
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",", 1)[0].strip() or None
    try:
        return request.client_address[0]
    except (AttributeError, IndexError):
        return None


def _make_handler(
    serve_dir: Path,
    db_path: Path,
    *,
    project_root: Path,
    on_codemaker_resource_import: Callable[[Path], dict[str, object]] | None,
) -> type[http.server.SimpleHTTPRequestHandler]:
    """設定済みの WebRuntimeHandler サブクラスを生成して返す。

    Args:
        serve_dir: 静的ファイル配信ディレクトリ。
        db_path: play_sessions SQLite のパス。
        project_root: リポジトリ root。
        on_codemaker_resource_import: import 完了時に呼ぶ callback。

    Returns:
        SimpleHTTPRequestHandler の派生クラス（クラス属性で設定を保持）。

    Policy:
        - 引数をクラス属性として束縛したサブクラスを type() で動的生成する。
    """
    attrs: dict[str, object] = {
        "serve_directory": serve_dir,
        "db_path": db_path,
        "project_root": project_root,
        "on_codemaker_resource_import": (
            staticmethod(on_codemaker_resource_import)
            if on_codemaker_resource_import is not None else None),
    }
    return type("WebRuntimeHandler", (_WebRuntimeHandlerBase,), attrs)


def _assemble_threading_server(
        serve_dir: Path,
        *,
        host: str,
        port: int,
        db_path: Path | None,
        project_root: Path | None,
        on_codemaker_resource_import: Callable[
            [Path], dict[str, object]] | None,
) -> http.server.ThreadingHTTPServer:
    """make_server の本体。default 解決と handler 生成を行う。

    Args:
        serve_dir: 静的ファイルを配信するディレクトリ。
        host: bind するホスト名。
        port: bind するポート番号。
        db_path: play_sessions SQLite のパス（None で既定値）。
        project_root: リポジトリ root（None で本ファイル基準）。
        on_codemaker_resource_import: import 完了時に呼ぶ callback。

    Returns:
        起動準備済みの ThreadingHTTPServer。

    Policy:
        - default 値の解決と _make_handler 呼び出しを順に行うだけ。
    """
    serve_dir = Path(serve_dir).resolve()
    db_path = _resolve_db_path(db_path)
    project_root = (project_root or ROOT).resolve()
    handler = _make_handler(
        serve_dir,
        db_path,
        project_root=project_root,
        on_codemaker_resource_import=on_codemaker_resource_import,
    )
    return http.server.ThreadingHTTPServer((host, port), handler)


def _resolve_db_path(db_path: Path | None) -> Path:
    """db_path が None のとき既定の SQLite パスを返す。

    Args:
        db_path: 明示指定された SQLite パス（None 可）。

    Returns:
        絶対パスに正規化した SQLite パス。

    Policy:
        - 既定は ROOT/.runtime/play_sessions.sqlite3。
    """
    default_path = ROOT / ".runtime" / "play_sessions.sqlite3"
    return (db_path or default_path).resolve()


def _ensure_initial_dist_build(project_root: Path, serve_dir: Path) -> None:
    """dist/index.html が無ければ build_web_release を実行する。

    Args:
        project_root: リポジトリ root。
        serve_dir: 静的ファイル配信ディレクトリ。

    Policy:
        - 既にビルド済みなら何もしない。失敗してもサーバーは起動させる。
    """
    dist_index = serve_dir / "dist" / "index.html"
    if dist_index.is_file():
        return
    print(
        "[web_runtime_server] dist/ artifacts not found;"
        " running initial build")
    _run_initial_build(project_root)


def _run_initial_build(project_root: Path) -> None:
    """build_web_release を try で囲んで呼ぶ。

    Args:
        project_root: リポジトリ root。

    Policy:
        - 失敗時は print のみで再 raise しない（サーバー起動を止めない）。
    """
    from tools.build_web_release import build_web_release

    try:
        build_web_release(project_root)
        print("[web_runtime_server] initial build completed")
    except Exception as exc:  # noqa: BLE001
        print(f"[web_runtime_server] initial build failed: {exc}")


def _parse_main_args() -> argparse.Namespace:
    """CLI 引数を解析して Namespace を返す。

    Returns:
        argparse の解析結果。

    Policy:
        - 既存 CLI 互換のため引数名と default 値を維持する。
    """
    parser = argparse.ArgumentParser(
        description=(
            "Serve Block Quest web files and"
            " internal play session logging"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--serve-dir", default=str(ROOT))
    parser.add_argument(
        "--db-path",
        default=str(ROOT / ".runtime" / "play_sessions.sqlite3"))
    parser.add_argument(
        "--skip-initial-build",
        action="store_true",
        help="dist/ 不在時の初回ビルドを行わない（test 用）",
    )
    return parser.parse_args()


def _start_initial_build_if_needed(args: argparse.Namespace) -> None:
    """--skip-initial-build が無いときだけ初回ビルドを起動する。

    Args:
        args: argparse の解析結果。

    Policy:
        - serve-dir を絶対パスに正規化したうえで ensure_dist_build に委ねる。
    """
    if args.skip_initial_build:
        return
    serve_dir = Path(args.serve_dir).resolve()
    ensure_dist_build(ROOT, serve_dir)


def _start_serving(args: argparse.Namespace) -> None:
    """ThreadingHTTPServer を起動し serve_forever ループに入る。

    Args:
        args: argparse の解析結果。

    Policy:
        - KeyboardInterrupt で停止し、最後に server_close を必ず呼ぶ。
    """
    serve_dir = Path(args.serve_dir).resolve()
    server = make_server(
        serve_dir,
        host=args.host,
        port=args.port,
        db_path=Path(args.db_path),
    )
    print(f"Serving {serve_dir} on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    run_main()
