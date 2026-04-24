"""pytest グローバルフック：pyxel を早期に stub する。

`pyxel.init()` なしで `pyxel.rect` などを呼ぶと Rust 側で panic する。
既存テスト（`test_damage_vfx` 等）は個別に `sys.modules['pyxel']` を差し替えて
いたが、別テストが `import pyxel` を先に走らせていると stub を入れる機会を
逃してしまう（pollution 発生）。

conftest で collection より先に stub を仕込み、どの順序でテストが走っても
real pyxel が走り出さないようにする。実機 pyxel が必要なテストは、内部で
独自の Fake を patch するので影響はない。
"""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock


def _install_pyxel_stub() -> None:
    if "pyxel" in sys.modules:
        mod = sys.modules["pyxel"]
        if getattr(mod, "__IS_TEST_STUB__", False):
            return
        # 実 pyxel がロード済みの場合も上書きする（init なしで panic するため）
    stub = types.ModuleType("pyxel")
    stub.__IS_TEST_STUB__ = True  # type: ignore[attr-defined]

    # ---- 関数・メソッド（描画 / 入力 / 音）----
    for fn_name in (
        "init", "run", "load", "quit", "cls", "rect", "rectb", "circ", "circb",
        "line", "pset", "blt", "bltm", "text", "play", "playm", "stop",
        "btn", "btnp",
    ):
        setattr(stub, fn_name, MagicMock(return_value=False))

    # ---- コレクション（MagicMock で十分。個別テストで上書き）----
    stub.sounds = [MagicMock() for _ in range(64)]
    stub.musics = [MagicMock() for _ in range(8)]
    stub.channels = [MagicMock() for _ in range(4)]
    stub.images = [MagicMock() for _ in range(4)]
    stub.tilemaps = [MagicMock() for _ in range(8)]

    # ---- 定数（KEY_* / GAMEPAD*）----
    for key in (
        "KEY_RETURN", "KEY_SPACE", "KEY_UP", "KEY_DOWN", "KEY_LEFT", "KEY_RIGHT",
        "KEY_ESCAPE", "KEY_BACKSPACE", "KEY_X", "KEY_Z", "KEY_S", "KEY_D", "KEY_W",
        "KEY_A", "KEY_M", "KEY_Q", "KEY_F1",
    ):
        setattr(stub, key, 0)
    for key in (
        "GAMEPAD1_BUTTON_A", "GAMEPAD1_BUTTON_B", "GAMEPAD1_BUTTON_X",
        "GAMEPAD1_BUTTON_Y", "GAMEPAD1_BUTTON_DPAD_UP", "GAMEPAD1_BUTTON_DPAD_DOWN",
        "GAMEPAD1_BUTTON_DPAD_LEFT", "GAMEPAD1_BUTTON_DPAD_RIGHT",
        "GAMEPAD1_BUTTON_START",
    ):
        setattr(stub, key, 0)

    # ---- 描画/入力系の状態変数 ----
    stub.mouse_x = 0
    stub.mouse_y = 0
    stub.frame_count = 0
    stub.width = 256
    stub.height = 256

    # ---- Font クラス（pyxel.Font("path")）----
    stub.Font = MagicMock()

    sys.modules["pyxel"] = stub


_install_pyxel_stub()
