#!/usr/bin/env python3
"""G11: Web 版動作テスト（Playwright + ランタイムサーバ）の CLI。

このファイルに含まれる関数・クラス：

- start_server: ランタイムサーバ (web_runtime_server.make_server) を起動して返す
- run_web_compat: Playwright で dist/play.html を開き致命的エラーが無いかを判定する
- main: run_web_compat の互換エイリアス（exit code をそのまま伝える）

Problems:
    - Web 配布版 (dist/play.html) に対する自動テストが無いと、Pyxel 側 / ランタイム
      サーバ側 / ビルド成果物のどこで壊れたか手作業で切り分けるしかない。
    - playwright や dist が無い CI / 環境で「テスト失敗」になると、本来見たい
      失敗（実装由来のクラッシュ・コンソールエラー）が埋もれる。

Solutions:
    - tools/test_web_compat.py を CLI として用意し、make build 後の
      dist/play.html を chromium-headless で開き、コンソールエラー / クラッシュ
      の有無で OK / FAIL を返す。
    - 必須前提（HTML 不在・playwright 未導入）は SKIP として exit 0 を返し、
      他の失敗を見やすくする。
"""
import sys
import threading
import time
import traceback
from pathlib import Path

from web_runtime_server import make_server


# === Public API ===


ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "dist" / "play.html"
SERVE_DIR = ROOT
PORT = 8899
WAIT_SECONDS = 10  # ゲーム初期化を待つ秒数
DB_PATH = ROOT / ".build" / "test_web_compat" / "play_sessions.sqlite3"


def start_server():
    """バックグラウンドで HTTP ランタイムサーバを起動して返す。

    Returns:
        http.server.HTTPServer: serve_forever 可能な状態のサーバ。

    Policy:
        - 副作用は make_server 側に閉じ、本体は委譲のみ。
    """
    return make_server(SERVE_DIR, host="127.0.0.1", port=PORT, db_path=DB_PATH)


def run_web_compat() -> int:
    """Web 版互換性テストを実行して exit code を返す。

    Returns:
        int: 0=通過 or SKIP、1=失敗。

    Policy:
        - 前提不足 (HTML 不在・playwright 未導入) は SKIP として 0 を返す。
        - 本体は委譲だけ。SKIP 判定と本処理は _dispatch_web_compat 内で行う。
    """
    return _dispatch_web_compat()


def main() -> int:  # noqa: CR100
    """run_web_compat の互換エイリアス（CLI 入口名を維持する）。

    Returns:
        int: run_web_compat と同じ exit code。

    Policy:
        - 実体は run_web_compat に委譲する。
    """
    return run_web_compat()


# === Internal helpers (private) ===


def _dispatch_web_compat() -> int:
    """SKIP 判定を順に行い、本処理へ委譲する private 本体。

    Returns:
        int: 0=通過 or SKIP、1=失敗。

    Policy:
        - HTML 不在 / playwright 未導入を SKIP として早期 return する。
    """
    if not HTML_PATH.exists():
        _print_missing_html()
        return 0
    if not _can_import_playwright():
        print("SKIP: playwright がインストールされていません")
        return 0
    return _run_playwright_compat_check()


def _print_missing_html() -> None:
    """dist/play.html が無いときの SKIP メッセージを出す。

    Policy:
        - ビルド未実施でも CI を止めないことを利用者に伝える。
    """
    print(f"SKIP: Web版HTMLが見つかりません: {HTML_PATH}")
    print("先に python tools/build_web_release.py を実行してください。")


def _can_import_playwright() -> bool:
    """playwright.sync_api が import 可能かを返す。

    Returns:
        bool: import 成功なら True。

    Policy:
        - 失敗は ImportError のみを SKIP の根拠として扱う。
    """
    try:
        import playwright.sync_api  # noqa: F401
    except ImportError:
        return False
    return True


def _run_playwright_compat_check() -> int:
    """サーバ起動 + Playwright 検査 + 後始末を 1 回ぶんやる。

    Returns:
        int: 0=通過、1=失敗。

    Policy:
        - finally でサーバを必ず閉じ、例外は traceback を吐いて FAIL=1 を返す。
    """
    httpd = start_server()
    server_thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    server_thread.start()
    try:
        return _execute_playwright_session()
    except Exception:
        print("FAIL: Web版テスト実行中に例外発生")
        traceback.print_exc()
        return 1
    finally:
        httpd.server_close()


def _execute_playwright_session() -> int:
    """Playwright で 1 ページを開き、クラッシュ / 致命的エラーを判定する。

    Returns:
        int: 0=通過、1=失敗。

    Policy:
        - sync_playwright コンテキストの中で browser を開閉する。
        - エラー収集 / クラッシュ検出は private helper に委譲する。
    """
    from playwright.sync_api import sync_playwright
    errors: list[str] = []
    warnings: list[str] = []
    crash_detected: list[bool] = []
    with sync_playwright() as runner:
        browser = runner.chromium.launch(headless=True)
        page = browser.new_page()
        _attach_console_listener(page, errors, warnings)
        _attach_crash_listener(page, crash_detected)
        _open_and_wait_play_html(page)
        if crash_detected:
            print("FAIL: ページがクラッシュしました")
            browser.close()
            return 1
        fatal_errors = _filter_fatal_errors(errors)
        browser.close()
    return _report_compat_result(fatal_errors, warnings)


def _attach_console_listener(page, errors: list[str],
                             warnings: list[str]) -> None:
    """console イベントから error / warning を 2 つの list に詰める。

    Args:
        page: Playwright の Page オブジェクト。
        errors: error メッセージを破壊的に append する list。
        warnings: warning メッセージを破壊的に append する list。

    Policy:
        - msg.type が "error" / "warning" 以外は無視する。
    """
    def on_console(msg) -> None:  # noqa: CR100,CR203,CR204
        """console イベントを受け取って種類別に振り分ける。

        Args:
            msg: Playwright が渡す ConsoleMessage オブジェクト。

        Policy:
            - Playwright API 互換のため名前を on_console から変えない。
            - error / warning 以外の type は無視する。
        """
        if msg.type == "error":
            errors.append(msg.text)
        elif msg.type == "warning":
            warnings.append(msg.text)
    page.on("console", on_console)


def _attach_crash_listener(page, crash_detected: list[bool]) -> None:
    """page crash イベントを受け取って crash_detected に True を追加する。

    Args:
        page: Playwright の Page オブジェクト。
        crash_detected: クラッシュ検出フラグの list（破壊的に append）。

    Policy:
        - 何回 crash しても 1 回でも append されていれば検出扱い。
    """
    def on_crash() -> None:  # noqa: CR100
        """crash イベントハンドラ（Playwright API 互換名）。

        Policy:
            - 何度発火しても crash_detected に True を append するだけ。
        """
        crash_detected.append(True)
    page.on("crash", on_crash)


def _open_and_wait_play_html(page) -> None:
    """dist/play.html を開いて初期化待ち sleep する。

    Args:
        page: Playwright の Page オブジェクト。

    Policy:
        - wait_until="domcontentloaded" + sleep(WAIT_SECONDS) で
          ゲームループの起動完了を粗く待つ。
    """
    url = f"http://127.0.0.1:{PORT}/dist/play.html"
    print(f"Opening {url} ...")
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    print(f"Waiting {WAIT_SECONDS}s for game initialization...")
    time.sleep(WAIT_SECONDS)


def _filter_fatal_errors(errors: list[str]) -> list[str]:
    """環境依存の警告を除いた致命的エラーだけを返す。

    Args:
        errors: 収集済みのエラーメッセージ列。

    Returns:
        list[str]: ALSA / favicon / SharedArrayBuffer 等の警告を除外したもの。

    Policy:
        - 既知のノイズ文字列は skip list で定義する。
    """
    skip_tokens = (
        "ALSA",
        "favicon.ico",
        "SharedArrayBuffer",
        "Cross-Origin-Opener-Policy",
    )
    return [
        msg for msg in errors
        if not any(token in msg for token in skip_tokens)
    ]


def _report_compat_result(fatal_errors: list[str],
                          warnings: list[str]) -> int:
    """fatal_errors / warnings を出力し、exit code を決める。

    Args:
        fatal_errors: 致命的エラーメッセージ列。
        warnings: 警告メッセージ列。

    Returns:
        int: 致命的エラーがあれば 1、無ければ 0。

    Policy:
        - 警告は最大 5 件まで頭出しし、本テスト自体は通過扱いにする。
    """
    if fatal_errors:
        print(f"FAIL: Web版でコンソールエラー検出 ({len(fatal_errors)}件)")
        for msg in fatal_errors:
            print(f"  ERROR: {msg}")
        return 1
    if warnings:
        print(f"WARNING: {len(warnings)}件の警告（テストは通過）")
        for warn_msg in warnings[:5]:
            print(f"  WARN: {warn_msg}")
    print(
        f"OK: Web版テスト通過（{WAIT_SECONDS}秒間クラッシュ"
        "・致命的エラーなし）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
