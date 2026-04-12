#!/usr/bin/env python3
"""G11: Web版動作テスト (Playwright)

Web版をローカルHTTPサーバで起動し、Playwright (Chromium Headless) で
ページを開いてコンソールエラーがないか検証する。

使い方:
    python tools/test_web_compat.py

exit 0 = テスト通過、exit 1 = テスト失敗
"""
import http.server
import sys
import threading
import time
import traceback
from pathlib import Path

# Web版のHTMLファイル
ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "pyxel.html"
SERVE_DIR = ROOT
PORT = 8899
WAIT_SECONDS = 10  # ゲーム初期化を待つ秒数


def start_server():
    """バックグラウンドでHTTPサーバを起動"""
    handler = http.server.SimpleHTTPRequestHandler
    httpd = http.server.HTTPServer(("127.0.0.1", PORT), handler)
    httpd.timeout = 1
    return httpd


def main():
    if not HTML_PATH.exists():
        print(f"SKIP: Web版HTMLが見つかりません: {HTML_PATH}")
        print("先に python tools/build_web_release.py を実行してください。")
        return 0  # ビルドがなければスキップ（失敗ではない）

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("SKIP: playwright がインストールされていません")
        return 0

    # HTTPサーバをバックグラウンドで起動
    import os
    original_dir = os.getcwd()
    os.chdir(SERVE_DIR)
    httpd = start_server()
    server_thread = threading.Thread(target=lambda: [httpd.handle_request() for _ in range(300)], daemon=True)
    server_thread.start()
    os.chdir(original_dir)

    errors = []
    warnings = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            # コンソールメッセージを収集
            def on_console(msg):
                if msg.type == "error":
                    errors.append(msg.text)
                elif msg.type == "warning":
                    warnings.append(msg.text)

            page.on("console", on_console)

            # ページクラッシュを検出
            crash_detected = []

            def on_crash():
                crash_detected.append(True)

            page.on("crash", on_crash)

            # ページを開く
            url = f"http://127.0.0.1:{PORT}/pyxel.html"
            print(f"Opening {url} ...")
            page.goto(url, wait_until="domcontentloaded", timeout=30000)

            # ゲーム初期化を待つ
            print(f"Waiting {WAIT_SECONDS}s for game initialization...")
            time.sleep(WAIT_SECONDS)

            if crash_detected:
                print("FAIL: ページがクラッシュしました")
                browser.close()
                return 1

            # 致命的なエラーをフィルタリング（ALSA等の環境依存警告は除外）
            fatal_errors = [
                e for e in errors
                if not any(skip in e for skip in [
                    "ALSA",
                    "favicon.ico",
                    "SharedArrayBuffer",
                    "Cross-Origin-Opener-Policy",
                ])
            ]

            browser.close()

            if fatal_errors:
                print(f"FAIL: Web版でコンソールエラー検出 ({len(fatal_errors)}件)")
                for e in fatal_errors:
                    print(f"  ERROR: {e}")
                return 1

            if warnings:
                print(f"WARNING: {len(warnings)}件の警告（テストは通過）")
                for w in warnings[:5]:
                    print(f"  WARN: {w}")

            print(f"OK: Web版テスト通過（{WAIT_SECONDS}秒間クラッシュ・致命的エラーなし）")
            return 0

    except Exception:
        print("FAIL: Web版テスト実行中に例外発生")
        traceback.print_exc()
        return 1
    finally:
        httpd.server_close()


if __name__ == "__main__":
    sys.exit(main())
