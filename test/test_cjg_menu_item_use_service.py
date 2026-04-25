"""CJG/crash regression: menu からの item 使用は item_use サービスを呼ぶ。

根拠:
- docs/customer-jobs.md Make3「ガードレール: Buy3 の壊れた出力を子どもに届けない」
- steering/done/20260425-shop-keyerror-shop-list-unpack.md（副次バグ）

かつて menu/scene.py:96 が `game.use_item(item_data)` を呼んでいたが、
Game クラスに `use_item` メソッドは存在せず AttributeError で落ちていた。
battle/scene.py と同じく `src.shared.services.item_use.use_item` 経由にする。
"""

from __future__ import annotations

import re
import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.item_use import use_item as use_item_fn
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeSfx:
    played: list[str] = field(default_factory=list)

    def play(self, name: str) -> None:
        self.played.append(name)


@dataclass
class _FakeMessages:
    def dialog_text(self, key: str, **kwargs: Any) -> str:
        # item_use は呼び出し結果の文字列を表示するだけなので
        # key 由来の一意な文字列を返せば十分。
        return f"{key}::{sorted(kwargs.items())}"


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)
    sfx: _FakeSfx = field(default_factory=_FakeSfx)
    messages: _FakeMessages = field(default_factory=_FakeMessages)
    last_town_pos: tuple[int, int] | None = None


class ItemUseServiceTest(unittest.TestCase):
    def test_heal_item_applies_hp_and_returns_message(self):
        game = _FakeGame()
        game.player_model.hp = 5  # 満タンでない
        item = {"type": "heal", "name": "やくそう", "value": 20}

        msg = use_item_fn(game, item)

        self.assertGreater(game.player_model.hp, 5)
        self.assertIn("heal", msg)
        self.assertIn("heal", game.sfx.played)

    def test_heal_item_returns_empty_when_hp_full(self):
        game = _FakeGame()
        pm = game.player_model
        pm.hp = pm.max_hp
        item = {"type": "heal", "name": "やくそう", "value": 20}

        msg = use_item_fn(game, item)

        self.assertEqual(msg, "")
        self.assertNotIn("heal", game.sfx.played)

    def test_mp_heal_item_applies_mp_and_returns_message(self):
        game = _FakeGame()
        game.player_model.mp = 0
        item = {"type": "mp_heal", "name": "まりょくのたね", "value": 10}

        msg = use_item_fn(game, item)

        self.assertEqual(game.player_model.mp, 10)
        self.assertIn("mp_heal", msg)

    def test_cure_poison_when_not_poisoned_returns_neutral_message(self):
        game = _FakeGame()
        game.player_model.poisoned = False
        item = {"type": "cure_poison", "name": "どくけしそう"}

        msg = use_item_fn(game, item)

        self.assertIn("必要なかった", msg)

    def test_warp_item_restores_town_position(self):
        game = _FakeGame(last_town_pos=(10, 20))
        pm = game.player_model
        pm.in_dungeon = True
        item = {"type": "warp", "name": "まちのいし"}

        msg = use_item_fn(game, item)

        self.assertEqual((pm.x, pm.y), (10, 20))
        self.assertFalse(pm.in_dungeon)
        self.assertIn("まちのいし", msg)


class MenuUsesServiceNotGameShimTest(unittest.TestCase):
    """menu/scene.py が `game.use_item(` のような存在しない shim を呼んでいないこと。"""

    def test_menu_does_not_call_game_use_item(self):
        # menu/scene.py と presenter.py の両方で `game.use_item(` が呼ばれて
        # いないことを確認する（M3-2 で update() ロジックは presenter に
        # 移譲されたため presenter 側もチェック対象）。
        for filename in ("scene.py", "presenter.py"):
            path = ROOT / "src" / "scenes" / "menu" / filename
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            self.assertIsNone(
                re.search(r"\bgame\.use_item\(", text),
                f"menu/{filename} は item_use サービスを直接呼ぶ形でなければならない。"
                " `game.use_item(` は存在しない shim で、呼ぶと AttributeError で落ちる。",
            )

    def test_menu_imports_item_use_service(self):
        # M3-2 で update() ロジックが presenter に集約されたため、
        # `from src.shared.services.item_use import use_item` の
        # import は presenter.py または scene.py のどちらかに存在すれば OK。
        scene_text = (ROOT / "src" / "scenes" / "menu" / "scene.py").read_text(encoding="utf-8")
        presenter_text = (ROOT / "src" / "scenes" / "menu" / "presenter.py").read_text(encoding="utf-8")
        pattern = r"from\s+src\.shared\.services\.item_use\s+import\s+use_item"
        self.assertTrue(
            re.search(pattern, scene_text) or re.search(pattern, presenter_text),
            "menu/scene.py または menu/presenter.py は item_use サービスを import する形で書く。",
        )


if __name__ == "__main__":
    unittest.main()
