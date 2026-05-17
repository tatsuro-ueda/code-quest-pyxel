"""town メニューの描画。

Problems:
    - 描画コードに状態判定が混ざると、見た目を変えるだけのつもりが Model 整合性まで考えることになる。
    - Pyxel API が Presenter / Model 側に染み出すとレイヤ境界が崩れ、テストでモックしづらくなる。

Solutions:
    - TownView は ViewModel と Pyxel API だけを扱い、判断は Presenter 側に閉じ込める。
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel

from src.scenes.town.view_model import TownMenuViewModel


@dataclass
class TownView:
    """town メニューの描画（framework-rule.md M2-1 / M1-1）。

    Pyxel API を呼んでよい層。Model / GameState には触らず、
    Presenter から渡された ``TownMenuViewModel`` だけを見て描く。
    """

    # === Public API ===

    game: Any = None

    def render_menu(self, vm: TownMenuViewModel) -> None:
        """町メニュー画面を描画する。

        Args:
            vm: 描画に必要なデータを保持する ViewModel。

        Policy:
            - 探索画面の上にウィンドウを重ねて描く。
        """
        self._render_menu_window(vm)

    # === Internal helpers (private) ===

    def _render_menu_window(self, vm: TownMenuViewModel) -> None:
        """ウィンドウ・ラベル・GOLD表示を一括描画する。

        Args:
            vm: 描画に必要なデータを保持する ViewModel。

        Boundary:
            - game が未設定なら何もしない（テスト時のショートサーキット）。

        Policy:
            - 探索画面の上に半透明ウィンドウを重ねて出す。
        """
        game = self.game
        if game is None:
            return
        # 町メニューは探索画面の上にウィンドウを重ねて出す。
        game.explore_scene.draw()
        game.status_bar.draw()
        x, y, w, h = 20, 40, 216, 170
        pyxel.rect(x, y, w, h, 1)
        pyxel.rectb(x, y, w, h, 7)
        game.messages.text(x + 8, y + 8, vm.title, 7)
        for i, label in enumerate(vm.labels):
            ly = y + 28 + i * 16
            color = 10 if i == vm.cursor else 7
            marker = ">" if i == vm.cursor else " "
            game.messages.text(x + 16, ly, f"{marker} {label}", color)
        game.messages.text(x + 8, y + h - 16, f"GOLD: {vm.gold}", 6)
