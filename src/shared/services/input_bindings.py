"""キーボード + ゲームパッドを論理グループでまとめる入力ヘルパー.

このファイルに含まれる関数・クラス：

- any_btn: グループ内のいずれかのボタンが押下中なら True を返す述語
- any_btnp: グループ内のいずれかのボタンがこのフレームで押されたら True を返す述語
- InputStateTracker: グループ単位で btn / btnp を 1 箇所に集約する Service
  - __init__: 全ボタングループを未押下状態で初期化する
  - update: 毎フレーム Pyxel から入力を取り、held と pressed を更新する
  - btn: 指定グループが押下中か返す（pyxel.btn 互換）
  - btnp: 指定グループがこのフレームで新たに押されたか返す（pyxel.btnp 互換）
  - _scan_groups: 全グループを 1 周して次フレーム分の held/pressed を計算する

Problems:
    - キー定数とゲームパッド定数を呼び出し側に直書きすると、
      「コンソール風（B = 決定 / A = キャンセル）」へ揃える変更で
      全 scene を触ることになる。
    - Pyxel の btn / btnp を毎 frame 直接呼ぶと、scene 側で「同じ判定式」が
      重複して、btn / btnp の差を取り違える事故が起きる。

Solutions:
    - 論理グループ（UP_BUTTONS / CONFIRM_BUTTONS など）を本モジュールに集約し、
      呼び出し側は ``input_state.btnp(CONFIRM_BUTTONS)`` のような述語呼びだけにする。
    - InputStateTracker.update が毎フレーム held / pressed を 1 度だけ算出し、
      btn / btnp はそれをただ返すだけのアクセサに保つ（CR204 ステップ列）。
    - pyxel 互換の述語名 ``btn`` / ``btnp`` / ``any_btn`` / ``any_btnp`` は
      ``# noqa: CR100`` で接頭辞ルールを免除（外部 API 互換のため固定）。
"""
from __future__ import annotations


UP_BUTTONS = ("KEY_UP", "GAMEPAD1_BUTTON_DPAD_UP")
DOWN_BUTTONS = ("KEY_DOWN", "GAMEPAD1_BUTTON_DPAD_DOWN")
LEFT_BUTTONS = ("KEY_LEFT", "GAMEPAD1_BUTTON_DPAD_LEFT")
RIGHT_BUTTONS = ("KEY_RIGHT", "GAMEPAD1_BUTTON_DPAD_RIGHT")
CONFIRM_BUTTONS = ("KEY_Z", "KEY_SPACE", "KEY_RETURN", "GAMEPAD1_BUTTON_B")
CANCEL_BUTTONS = (
    "KEY_X",
    "KEY_ESCAPE",
    "GAMEPAD1_BUTTON_A",
    "GAMEPAD1_BUTTON_BACK")
TITLE_START_BUTTONS = CONFIRM_BUTTONS + ("GAMEPAD1_BUTTON_START",)

BUTTON_GROUPS = (
    UP_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    CONFIRM_BUTTONS,
    CANCEL_BUTTONS,
    TITLE_START_BUTTONS,
)


def any_btn(pyxel_module, button_names) -> bool:  # noqa: CR100
    """グループ内のいずれかのボタンが押下中なら True を返す。

    Args:
        pyxel_module: pyxel 本体、または同 I/F の test fake。
        button_names: ``UP_BUTTONS`` などのボタン名タプル。
    Returns:
        bool: グループの少なくとも 1 個が押下中なら True。
    Policy:
        - 名前は pyxel 慣用（pyxel.btn）に合わせて固定（# noqa: CR100）。
        - 副作用なし。``getattr(pyxel_module, name)`` で名前→コード解決する。
    """
    return any(pyxel_module.btn(getattr(pyxel_module, name))
               for name in button_names)


def any_btnp(pyxel_module, button_names) -> bool:  # noqa: CR100
    """グループ内のいずれかのボタンがこのフレームで押されたなら True を返す。

    Args:
        pyxel_module: pyxel 本体、または同 I/F の test fake。
        button_names: ``CONFIRM_BUTTONS`` などのボタン名タプル。
    Returns:
        bool: グループの少なくとも 1 個がこのフレームで新たに押されたら True。
    Policy:
        - 名前は pyxel 慣用（pyxel.btnp）に合わせて固定（# noqa: CR100）。
        - 副作用なし。``getattr(pyxel_module, name)`` で名前→コード解決する。
    """
    return any(pyxel_module.btnp(getattr(pyxel_module, name))
               for name in button_names)


class InputStateTracker:
    """キー＋ゲームパッドをグループ単位で扱い、自前で btn / btnp を追跡する。"""

    # === Public API ===

    def __init__(self):
        """全ボタングループを未押下状態で初期化する。

        Policy:
            - held / pressed は BUTTON_GROUPS をキーにした dict として保持し、
              初期状態は全 False に揃える。
        """
        self._held = {button_names: False for button_names in BUTTON_GROUPS}
        self._pressed = {
            button_names: False for button_names in BUTTON_GROUPS}

    def update(self, pyxel_module):
        """毎フレーム Pyxel から入力を取り、held と pressed を更新する。

        Args:
            pyxel_module: pyxel 本体、または同 I/F の test fake。
        Policy:
            - 計算は ``_scan_groups`` に閉じ込め、本体は委譲だけのステップ列にする。
            - 1 フレームに 1 回だけ呼ぶ（Pyxel update でセッションに 1 度）。
        """
        next_held, next_pressed = self._scan_groups(pyxel_module)
        self._held = next_held
        self._pressed = next_pressed
        return

    def btn(self, button_names) -> bool:  # noqa: CR100
        """指定グループが押下中か返す（pyxel.btn 互換アクセサ）。

        Args:
            button_names: ``UP_BUTTONS`` などのボタン名タプル。
        Returns:
            bool: 直近の ``update`` 時点でグループが押下中なら True。
        Policy:
            - 名前は pyxel 慣用（pyxel.btn）に合わせて固定（# noqa: CR100）。
            - 内部 dict を読むだけで副作用なし。
        """
        return self._held.get(button_names, False)

    def btnp(self, button_names) -> bool:  # noqa: CR100
        """指定グループがこのフレームで新たに押されたか返す（pyxel.btnp 互換）。

        Args:
            button_names: ``CONFIRM_BUTTONS`` などのボタン名タプル。
        Returns:
            bool: 直前の update でこのフレームに新規押下と判定されていたら True。
        Policy:
            - 名前は pyxel 慣用（pyxel.btnp）に合わせて固定（# noqa: CR100）。
            - 内部 dict を読むだけで副作用なし。
        """
        return self._pressed.get(button_names, False)

    # === Internal helpers (private) ===

    def _scan_groups(self, pyxel_module):
        """全グループを 1 周して次フレーム分の (held, pressed) を返す。

        Args:
            pyxel_module: pyxel 本体、または同 I/F の test fake。
        Returns:
            tuple[dict, dict]: (next_held, next_pressed) の dict ペア。
        Policy:
            - pressed は「今フレーム押下 かつ 前フレームは未押下」とする
              （pyxel.btnp と同じ立ち上がりエッジ）。
        """
        next_held = {}
        next_pressed = {}
        for button_names in BUTTON_GROUPS:
            held = any_btn(pyxel_module, button_names)
            next_held[button_names] = held
            next_pressed[button_names] = (
                held and not self._held[button_names])
        return next_held, next_pressed
