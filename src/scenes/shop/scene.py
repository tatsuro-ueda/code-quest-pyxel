"""shop scene 本体（Model / View / Presenter の配線）。

Problems:
    - Scene に入力解釈と描画ロジックを直書きすると、レイヤが崩れて
      テスト時に Pyxel まで起動する必要が出る。
    - シーンごとに生成・配線手順がばらばらだと、新しいシーンを
      追加する時に何を持たせるか毎回考え直すことになる。

Solutions:
    - shop の Scene は Model / View / Presenter を保持し、
      update / draw を Presenter / View へ委譲する薄い配線に保つ。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.shop.model import ShopModel
from src.scenes.shop.presenter import ShopPresenter
from src.scenes.shop.view import ShopView


@dataclass
class ShopScene:
    """shop シーン（P1-G5 で Game から 4 メソッドを取り込み）。"""

    # === Public API ===

    name: str = "shop"
    model: ShopModel = field(default_factory=ShopModel)
    view: ShopView = field(default_factory=ShopView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self.presenter = ShopPresenter(self.model)

    def enter(self, kind: str) -> None:
        """ショップ画面に遷移する。kind は 'weapons' / 'armors' / 'items'。

        Args:
            kind: kind の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_enter(kind)

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        self._run_update()

    def draw(self) -> None:
        """ショップ画面を描画する。描画本体は View に委譲（M1-1 準拠）。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        return self._run_draw()

    # === Internal helpers (private) ===

    def _run_enter(self, kind: str) -> None:
        """_run_enter() の実装本体。

        Args:
            kind: kind の値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        import src.runtime.main_runtime as M
        # 町情報は GameState.current_town から受け取る（framework-rule.md M4-3）。
        # shop は town の内部状態（town_model）を直接のぞき込まない。
        if game.current_town is None:
            # フォールバック: 町情報が未設定ならインデックス0の町扱い
            index = 0
            game.last_town_pos = None
        else:
            index = game.current_town.index
            game.last_town_pos = game.current_town.pos
        shop = M.SHOP_LIST[index]
        self.model.kind = kind
        self.model.inventory = list(shop[kind])
        self.model.cursor = 0
        self.model.message = ""
        game.state = "shop"

    def _run_update(self) -> None:
        """_run_update() の実装本体。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def _run_draw(self) -> None:
        """_run_draw() の実装本体。

        Returns:
            関数の戻り値。
        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return self.view.render()
        vm = self.presenter.build_view_model(game)
        self.view.draw(vm, game.messages)

    def _try_purchase(self) -> None:
        """既存テスト互換：購入処理を Presenter に委譲。

        Postconditions:
            - 副作用とモデル更新は実装どおり。
        """
        game = self.game
        if game is None:
            return
        self.presenter.try_purchase(game)
