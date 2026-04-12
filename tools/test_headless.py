#!/usr/bin/env python3
"""G8: ヘッドレス起動テスト

main.py をヘッドレスモードで起動し、初期化から1フレーム描画まで完走できるか検証する。
壊れた版を子どもに届けない最後の防壁。

使い方:
    python tools/test_headless.py

exit 0 = テスト通過、exit 1 = テスト失敗
"""
import sys
import traceback

def main():
    try:
        # Step 1: pyxel.init を headless=True 付きにモンキーパッチ
        import pyxel
        original_init = pyxel.init

        def headless_init(*args, **kwargs):
            kwargs["headless"] = True
            original_init(*args, **kwargs)

        pyxel.init = headless_init

        # Step 2: pyxel.run を「1フレームだけ実行して終了」に差し替え
        # pyxel.run() はブロッキングなゲームループなので、
        # update+draw を1回だけ呼んで正常終了させる
        run_captured = {}

        def fake_run(update_fn, draw_fn):
            run_captured["update"] = update_fn
            run_captured["draw"] = draw_fn

        pyxel.run = fake_run

        # Step 3: main.py を import（構文エラー・importエラーを検出）
        # main.py はモジュールトップレベルで Game() と game.start() を実行する。
        # headless_init と fake_run により、画面なし・ループなしで初期化が完走する。
        sys.path.insert(0, ".")
        import main  # noqa: F401

        # Step 4: update() と draw() を1回ずつ呼ぶ（1フレーム描画）
        if "update" not in run_captured:
            print("ERROR: pyxel.run() が呼ばれませんでした。main.py のエントリポイントを確認してください。")
            return 1

        run_captured["update"]()
        run_captured["draw"]()

        print("OK: ヘッドレス起動テスト通過（初期化 + 1フレーム描画完走）")
        return 0

    except Exception:
        print("FAIL: ヘッドレス起動テスト失敗")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
