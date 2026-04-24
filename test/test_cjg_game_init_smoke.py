"""CJG smoke: Game() が起動時に crash せず `state = 'splash'` を張れる。

根拠:
- docs/customer-jobs.md Make3「ガードレール: クラッシュで好循環が途絶」
- docs/customer-journeys.md CJ の冒頭「URL を開くだけで即プレイ」想定
- 2026-04-25 までに発覚した crash はすべて Game 初期化後の state 遷移で出たもので、
  初期化そのものが壊れるともっと早く死ぬ（タイトル前に blank で止まる）

pyxel は conftest.py で stub 済み。init→Font→AudioManager→ImageBanks→PlayerModel
→VfxSystem→InputStateTracker→各 scene インスタンス化のパイプラインが
AttributeError / KeyError / ImportError を出さずに完走することを固定化する。

Game() 生成は数秒かかる（setup_image_banks がタイルマップ構築で時間を食う）ので、
setUpClass で 1 回だけ作って全検査で共有する。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


class GameInitSmokeTest(unittest.TestCase):
    _game = None
    _player_model_cls = None

    @classmethod
    def setUpClass(cls):
        from src.runtime.app import Game
        from src.shared.state.player_model import PlayerModel

        cls._game = Game()
        cls._player_model_cls = PlayerModel

    def test_constructor_sets_initial_state_to_splash(self):
        self.assertEqual(self._game.state, "splash")
        self.assertEqual(self._game.prev_state, "map")

    def test_all_dispatcher_scenes_are_attached(self):
        expected_scene_attrs = (
            "splash_scene", "title_scene", "explore_scene", "battle_scene",
            "menu_scene", "settings_scene", "shop_scene", "ai_help_scene",
            "ending_scene", "professor_scene",
        )
        for attr in expected_scene_attrs:
            with self.subTest(attr=attr):
                self.assertTrue(
                    hasattr(self._game, attr),
                    f"Game に {attr} が無い。dispatcher 呼び出しで AttributeError になる",
                )

    def test_town_presenter_and_view_exist_but_not_town_scene(self):
        """town scene.py 廃止後は town_model / town_presenter / town_view が直接属性になる。"""
        self.assertTrue(hasattr(self._game, "town_model"))
        self.assertTrue(hasattr(self._game, "town_presenter"))
        self.assertTrue(hasattr(self._game, "town_view"))
        self.assertFalse(
            hasattr(self._game, "town_scene"),
            "town/scene.py は廃止された。town_scene 属性が復活するのは回帰",
        )

    def test_player_model_is_playermodel_and_no_player_dict(self):
        """player dict は廃止され player_model のみが残る（M4-4 Level 2）。"""
        self.assertIsInstance(self._game.player_model, self._player_model_cls)
        self.assertFalse(
            hasattr(self._game, "player"),
            "game.player dict は廃止済み。PlayerModel のみを正本とする",
        )

    def test_current_town_starts_as_none(self):
        """町に入る前の GameState.current_town は None（shop フォールバック経路の条件）。"""
        self.assertIsNone(self._game.current_town)

    def test_core_game_services_are_attached(self):
        """dispatcher が触る主要サービス属性が揃っていること。"""
        for attr in ("messages", "sfx", "audio", "input_state", "save_store", "font"):
            with self.subTest(attr=attr):
                self.assertTrue(hasattr(self._game, attr), f"Game に {attr} が無い")


if __name__ == "__main__":
    unittest.main()
