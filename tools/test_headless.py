#!/usr/bin/env python3
"""G8: ヘッドレス起動テスト CLI。

Problems:
    - 子どもに届ける版が「import 通った／1 フレーム描画できる」最低保証を
      満たしているかは、Pyxel runtime を手で立ち上げないと確認できない。
    - main.py を実際に走らせると GUI ループに入ってしまい、CI でも
      回せる軽量ガードにならない。

Solutions:
    - pyxel.init と pyxel.run を一時的にモンキーパッチし、headless モードで
      初期化 → 1 フレーム描画まで完走できるかを確認する CLI を提供する。
    - exit 0 / 1 のみを返す簡潔な防壁とし、CI / release flow から呼べる
      ヘッドレス防壁として位置づける。

使い方:
    python tools/test_headless.py

exit 0 = テスト通過、exit 1 = テスト失敗
"""
from __future__ import annotations

import sys
import traceback
from typing import Any


# === Public API ===


def run_test() -> int:
    """ヘッドレス起動テストを実行し exit code を返す。

    Returns:
        int: 0=通過 / 1=失敗。

    Policy:
        - 例外は trace を出して 1 を返す。正常時は 1 フレーム update/draw を呼ぶ。
    """
    return _try_headless_probe()


# === Internal helpers (private) ===


def _try_headless_probe() -> int:
    """_run_headless_probe を try/except でラップし trace 出力に責任を持つ。

    Returns:
        int: 0=通過 / 1=失敗。

    Policy:
        - 例外を全部つかんで FAIL ログと traceback を残し 1 を返す。
    """
    try:
        return _run_headless_probe()
    except Exception:
        print("FAIL: ヘッドレス起動テスト失敗")
        traceback.print_exc()
        return 1


def _run_headless_probe() -> int:
    """pyxel をパッチして main.py を走らせ、1 フレーム描画して 0 を返す。

    Returns:
        int: 0=描画成功 / 1=pyxel.run 未呼び出し。

    Policy:
        - patch → import → run check → 1 frame の 4 ステップに分割する。
    """
    run_captured = _patch_pyxel_for_headless()
    _import_main(run_captured)
    if not _has_captured_run(run_captured):
        return _report_no_run()
    _exercise_one_frame(run_captured)
    print("OK: ヘッドレス起動テスト通過（初期化 + 1フレーム描画完走）")
    return 0


def _patch_pyxel_for_headless() -> dict[str, Any]:
    """pyxel.init / pyxel.run を headless 用に差し替え、捕捉 dict を返す。

    Returns:
        dict[str, Any]: pyxel.run の引数 (update / draw) を入れる dict。

    Policy:
        - 元の pyxel.init は headless=True 付きで呼び、pyxel.run はループしない。
    """
    import pyxel
    run_captured: dict[str, Any] = {}
    headless_init = _make_headless_init(pyxel.init)
    fake_run = _make_fake_run(run_captured)
    pyxel.init = headless_init
    pyxel.run = fake_run
    return run_captured


def _make_headless_init(original_init):
    """headless=True 強制で original_init を呼ぶラッパを返す。

    Args:
        original_init: 元の pyxel.init。

    Returns:
        Callable: kwargs に headless=True を強制してから委譲する関数。

    Policy:
        - 既存の引数はそのまま渡し、headless キーだけ上書きする。
    """
    def headless_init(*args, **kwargs) -> None:  # noqa: CR100
        """pyxel.init を headless=True 強制で呼ぶラッパ。

        Args:
            *args: pyxel.init に渡す位置引数。
            **kwargs: pyxel.init に渡すキーワード引数。

        Policy:
            - kwargs["headless"] を True に上書きしてから委譲する。
        """
        kwargs["headless"] = True
        original_init(*args, **kwargs)
    return headless_init


def _make_fake_run(run_captured: dict[str, Any]):
    """pyxel.run を 1 フレームも回さない fake_run を返す。

    Args:
        run_captured: 捕捉先の dict。

    Returns:
        Callable: update / draw を run_captured に詰めるだけの関数。

    Policy:
        - 後で 1 度だけ呼ぶために run_captured に保存する。
    """
    def fake_run(update_fn, draw_fn) -> None:
        """update / draw を保持するだけのダミー pyxel.run。

        Args:
            update_fn: 通常の update 関数。
            draw_fn: 通常の draw 関数。

        Policy:
            - 受け取った 2 つを run_captured に保存して即終了する。
        """
        run_captured["update"] = update_fn
        run_captured["draw"] = draw_fn
    return fake_run


def _import_main(run_captured: dict[str, Any]) -> None:
    """main.py を import し、必須なら main.run() で初期化を完走させる。

    Args:
        run_captured: pyxel.run が呼ばれたかを保持する dict。

    Policy:
        - main トップで game.start() が呼ばれない設計向けに run() フォールバックを残す。
    """
    sys.path.insert(0, ".")
    import main

    if _can_apply_run_fallback(run_captured, main):
        main.run()


def _can_apply_run_fallback(
    run_captured: dict[str, Any],
    main_module: Any,
) -> bool:
    """main.run() を後追いで呼ぶ必要があるかを判定する。

    Args:
        run_captured: pyxel.run が呼ばれたかを保持する dict。
        main_module: import 済みの main モジュール。

    Returns:
        bool: pyxel.run が未捕捉で main.run があれば True。

    Policy:
        - import 中に pyxel.run が呼ばれたなら fallback 不要。
    """
    if "update" in run_captured:
        return False
    return hasattr(main_module, "run")


def _has_captured_run(run_captured: dict[str, Any]) -> bool:
    """pyxel.run が捕捉済みかを判定する。

    Args:
        run_captured: pyxel.run の引数を入れる dict。

    Returns:
        bool: update が登録されていれば True。

    Policy:
        - update / draw は同時に登録される前提で update キーで代表させる。
    """
    return "update" in run_captured


def _report_no_run() -> int:
    """pyxel.run が呼ばれなかったときのエラーメッセージを出し 1 を返す。

    Returns:
        int: 失敗コード 1。

    Policy:
        - main.py 側のエントリ不備を読み手に伝える。
    """
    print(
        "ERROR: pyxel.run() が呼ばれませんでした。"
        "main.py のエントリポイントを確認してください。"
    )
    return 1


def _exercise_one_frame(run_captured: dict[str, Any]) -> None:
    """捕捉した update / draw を 1 度ずつ呼んで 1 フレーム分の描画を走らせる。

    Args:
        run_captured: pyxel.run が呼ばれたときに保存された関数を持つ dict。

    Policy:
        - 例外時は呼び出し元の try/except で trace を出す前提で素朴に呼ぶ。
    """
    run_captured["update"]()
    run_captured["draw"]()


if __name__ == "__main__":
    sys.exit(run_test())
