from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.scenes.shop.model import ShopModel
from src.scenes.shop.presenter import ShopPresenter
from src.scenes.shop.view import ShopView


@dataclass
class ShopScene:
    """shop シーン（P1-G5 で Game から 4 メソッドを取り込み）。"""

    name: str = "shop"
    model: ShopModel = field(default_factory=ShopModel)
    view: ShopView = field(default_factory=ShopView)
    game: Any = None

    def __post_init__(self) -> None:
        """model を共有する presenter を生成する。"""
        self.presenter = ShopPresenter(self.model)

    def enter(self, kind: str) -> None:
        """ショップ画面に遷移する。kind は 'weapons' / 'armors' / 'items'。"""
        game = self.game
        import src.runtime.main_runtime as M
        # 町情報は GameState.current_town から受け取る（framework-rule.md M4-3）。
        # shop は town の内部状態（town_model）を直接のぞき込まない。
        if game.current_town is None:
            # フォールバック: 町情報が未設定ならインデックス0の町扱い
            idx = 0
            game.last_town_pos = None
        else:
            idx = game.current_town.index
            game.last_town_pos = game.current_town.pos
        shop = M.SHOP_LIST[idx]
        self.model.kind = kind
        self.model.inventory = list(shop[kind])
        self.model.cursor = 0
        self.model.message = ""
        game.state = "shop"

    def update(self) -> None:
        """配線：入力解釈・遷移決定は Presenter に委譲（M3-2 準拠）。"""
        game = self.game
        if game is None:
            return
        self.presenter.update(game)

    def _try_purchase(self) -> None:
        """既存テスト互換：購入処理を Presenter に委譲。"""
        game = self.game
        if game is None:
            return
        self.presenter.try_purchase(game)

    def draw(self) -> None:
        """ショップ画面を描画する。描画本体は View に委譲（M1-1 準拠）。"""
        game = self.game
        if game is None:
            return self.view.render()
        vm = self.presenter.build_view_model(game)
        self.view.draw(vm, game.messages)
