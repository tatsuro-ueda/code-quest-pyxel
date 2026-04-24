"""CJG/professor: ProfessorScene.phase / battle_phase の純粋ロジックを固定化。

根拠:
- docs/product-requirements-narrative.md（Professor の進行度によるセリフ分岐）
- docs/product-requirements-battle.md（ボス HP 帯での演出・発話切替）

phase() は PlayerModel の glitch_lord_defeated / max_zone_reached から
"early" / "mid" / "late" を返す純粋関数。battle_phase(ratio) は HP 比率を
閾値（10/25/40/55/70/85）で区切り、対応する文字列キーを返す。これらは
ダイアログ辞書のキーとして使われるため、境界値を変えると台詞が出なく
なる（KeyError にはならないが体験が静かに壊れる）。
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.scenes.professor.scene import ProfessorScene
from src.shared.state.player_model import PlayerModel


@dataclass
class _FakeGame:
    player_model: PlayerModel = field(default_factory=PlayerModel.new_game)


class ProfessorPhaseTest(unittest.TestCase):
    def test_phase_early_when_no_progress(self):
        game = _FakeGame()
        game.player_model.max_zone_reached = 0
        scene = ProfessorScene(game=game)

        self.assertEqual(scene.phase(), "early")

    def test_phase_mid_when_max_zone_reached_1_or_2(self):
        for zone in (1, 2):
            with self.subTest(zone=zone):
                game = _FakeGame()
                game.player_model.max_zone_reached = zone
                scene = ProfessorScene(game=game)

                self.assertEqual(scene.phase(), "mid")

    def test_phase_late_when_max_zone_reached_3_or_more(self):
        for zone in (3, 4, 5):
            with self.subTest(zone=zone):
                game = _FakeGame()
                game.player_model.max_zone_reached = zone
                scene = ProfessorScene(game=game)

                self.assertEqual(scene.phase(), "late")

    def test_phase_late_overrides_everything_when_glitch_lord_defeated(self):
        game = _FakeGame()
        game.player_model.max_zone_reached = 0
        game.player_model.glitch_lord_defeated = True
        scene = ProfessorScene(game=game)

        self.assertEqual(scene.phase(), "late")


class ProfessorBattlePhaseTest(unittest.TestCase):
    """battle_phase(ratio) が 10 / 25 / 40 / 55 / 70 / 85 / 100 で区切られる。"""

    def _battle_phase(self, ratio: float) -> str:
        game = _FakeGame()
        return ProfessorScene(game=game).battle_phase(ratio)

    def test_full_hp_returns_100(self):
        # 1.0 は 100% → すべての閾値を上回る
        self.assertEqual(self._battle_phase(1.0), "100")

    def test_below_10_percent_returns_10(self):
        self.assertEqual(self._battle_phase(0.05), "10")

    def test_just_below_each_threshold(self):
        for threshold in (10, 25, 40, 55, 70, 85):
            ratio = (threshold - 0.5) / 100.0  # 閾値を 0.5% 下回る
            with self.subTest(threshold=threshold):
                self.assertEqual(self._battle_phase(ratio), str(threshold))

    def test_exactly_threshold_goes_to_next_bucket(self):
        """`pct < thr` なので pct==thr は thr 枠に入らず次の枠に進む。"""
        # 10% ちょうど → 25 枠（pct < 10 が False → pct < 25 が True）
        self.assertEqual(self._battle_phase(0.10), "25")
        # 85% ちょうど → 100 枠
        self.assertEqual(self._battle_phase(0.85), "100")

    def test_ratio_zero_returns_10(self):
        """HP 0%（撃破寸前）でも "10" を返す（関数が "0" を返すと未定義キーになる）。"""
        self.assertEqual(self._battle_phase(0.0), "10")


if __name__ == "__main__":
    unittest.main()
