"""CJG/shop: 装備中アイテムは下部メッセージ「すでに もっている。」で示す。

根拠:
- steering/20260517-shop-owned-marker-clipping.md（行内 [もっています] が画面右端で切れる）
- docs/customer-jobs.md Job4（ゲームを楽しむ）

ShopPresenter.build_view_model は:
- 行内に [もっています] を出さない（横幅切れ防止）
- カーソル位置の owned アイテム（weapons/armors のみ）を下部 vm.message に表示
- 短期メッセージ（購入/不足/重複購入）が立っていればそちらを優先
- 短期メッセージは MESSAGE_TTL_FRAMES フレーム経過で消える
- items は「装備中」概念が無いので owned 自動表示の対象外
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.shop.presenter import (
    MESSAGE_TTL_FRAMES,
    OWNED_MESSAGE,
    ShopPresenter,
)
from src.scenes.shop.scene import ShopScene
from src.shared.services.game_state import TownContext
from src.shared.services.text_format import TextFormat
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeInputState:
    def btnp(self, *args, **kwargs) -> bool:
        return False


@dataclass
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    current_town: TownContext | None = None
    last_town_pos: tuple[int, int] | None = None
    state: str = "shop"
    has_jp_font: bool = True
    input_state: _FakeInputState = field(default_factory=_FakeInputState)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    text_fmt: TextFormat = field(default_factory=TextFormat)

    def __post_init__(self) -> None:
        self.text_fmt.game = self


def _enter_shop(kind: str) -> tuple[ShopScene, _FakeGame]:
    game = _FakeGame(current_town=TownContext(index=0, pos=(25, 6)))
    scene = ShopScene(game=game)
    scene.enter(kind)
    return scene, game


class ShopOwnedMessageTest(unittest.TestCase):
    def test_rows_never_contain_owned_marker_text(self):
        """シナリオ1の一部 + シナリオ4 共通: どの行にも [もっています] が含まれない。"""
        for kind in ("weapons", "armors", "items"):
            scene, game = _enter_shop(kind)
            # owned 候補にしておく
            if kind == "weapons":
                game.player_model.weapon = scene.model.inventory[0]
            elif kind == "armors":
                game.player_model.armor = scene.model.inventory[0]

            vm = scene.presenter.build_view_model(game)

            for row in vm.rows:
                self.assertNotIn("[もっています]", row.label, f"{kind} 行内に印が残っている")
                self.assertNotIn("もっています", row.label, f"{kind} 行内に印が残っている")

    def test_cursor_on_equipped_weapon_shows_owned_message(self):
        """シナリオ1: 装備中武器にカーソルがあると下部に OWNED_MESSAGE。"""
        scene, game = _enter_shop("weapons")
        game.player_model.weapon = scene.model.inventory[0]
        scene.model.cursor = 0
        scene.model.message = ""
        scene.model.message_ttl = 0

        vm = scene.presenter.build_view_model(game)

        self.assertEqual(vm.message, OWNED_MESSAGE)

    def test_cursor_on_unequipped_weapon_shows_no_message(self):
        """シナリオ2: 未装備の武器に動かすと vm.message が None になる。"""
        scene, game = _enter_shop("weapons")
        # 1 番目を装備、カーソルは 2 番目
        game.player_model.weapon = scene.model.inventory[0]
        scene.model.cursor = 1
        scene.model.message = ""
        scene.model.message_ttl = 0

        vm = scene.presenter.build_view_model(game)

        self.assertIsNone(vm.message)

    def test_purchase_short_message_takes_priority_then_fades(self):
        """シナリオ3: try_purchase 直後は短期 message 優先、ttl 経過後にカーソル判定へ。"""
        scene, game = _enter_shop("weapons")
        game.player_model.weapon = scene.model.inventory[0]
        scene.model.cursor = 0

        scene.presenter.try_purchase(game)
        self.assertEqual(scene.model.message_ttl, MESSAGE_TTL_FRAMES)
        vm_now = scene.presenter.build_view_model(game)
        self.assertEqual(vm_now.message, "すでに もっています")

        for _ in range(MESSAGE_TTL_FRAMES):
            scene.presenter.update(game)

        self.assertEqual(scene.model.message_ttl, 0)
        self.assertEqual(scene.model.message, "")
        vm_after = scene.presenter.build_view_model(game)
        self.assertEqual(vm_after.message, OWNED_MESSAGE)

    def test_items_kind_never_shows_owned_message(self):
        """シナリオ4: items は装備中概念が無いので owned 自動表示の対象外。"""
        scene, game = _enter_shop("items")
        scene.model.cursor = 0
        scene.model.message = ""
        scene.model.message_ttl = 0

        vm = scene.presenter.build_view_model(game)

        self.assertIsNone(vm.message)

    def test_empty_inventory_keeps_empty_message(self):
        """シナリオ5: 在庫なしのときは empty_message が立ち、vm.message は None のまま。"""
        scene, game = _enter_shop("weapons")
        scene.model.inventory = []
        scene.model.message = ""
        scene.model.message_ttl = 0

        vm = scene.presenter.build_view_model(game)

        self.assertIsNotNone(vm.empty_message)
        self.assertEqual(vm.rows, [])
        self.assertIsNone(vm.message)


if __name__ == "__main__":
    unittest.main()
