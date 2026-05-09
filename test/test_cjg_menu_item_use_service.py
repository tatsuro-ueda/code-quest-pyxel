"""CJG/crash regression: menu からの item 使用は PlayerModel ルールを使う。

根拠:
- docs/customer-jobs.md Make3「ガードレール: Buy3 の壊れた出力を子どもに届けない」
- steering/done/20260425-shop-keyerror-shop-list-unpack.md（副次バグ）

かつて menu/scene.py:96 が `game.use_item(item_data)` を呼んでいたが、
Game クラスに `use_item` メソッドは存在せず AttributeError で落ちていた。
その後 item_use service を経由していたが、M4-4 後半では PlayerModel に
ルールを集約し、scene 側は `game.player_model.use_item(...)` を使う。
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


class MenuUsesPlayerModelNotGameShimTest(unittest.TestCase):
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

    def test_menu_uses_player_model_rule_directly(self):
        scene_text = (ROOT / "src" / "scenes" / "menu" / "scene.py").read_text(encoding="utf-8")
        presenter_text = (ROOT / "src" / "scenes" / "menu" / "presenter.py").read_text(encoding="utf-8")
        pattern = r"player_model\.use_item\("
        self.assertTrue(
            re.search(pattern, scene_text) or re.search(pattern, presenter_text),
            "menu/scene.py または menu/presenter.py は game.player_model.use_item(...) を使う。",
        )


if __name__ == "__main__":
    unittest.main()
