"""CJG/explore: 魔王グリッチ撃破後の洞窟 encounter がグリッチクローンへ切り替わる。"""

from __future__ import annotations

import types
import unittest
from unittest.mock import MagicMock, patch

import src.runtime.main_runtime as M
from src.scenes.explore.model import ExploreModel
from src.scenes.explore.presenter import ExplorePresenter
from src.shared.state.player_model import PlayerModel


def _make_game(
    *,
    in_dungeon: bool,
    glitch_lord_defeated: bool,
    y: int = 0,
) -> types.SimpleNamespace:
    player = PlayerModel()
    player.in_dungeon = in_dungeon
    player.glitch_lord_defeated = glitch_lord_defeated
    player.y = y
    return types.SimpleNamespace(
        debug_mode=False,
        player_model=player,
        battle_scene=types.SimpleNamespace(start=MagicMock()),
    )


class DungeonPostBossCloneSpawnTest(unittest.TestCase):
    def setUp(self) -> None:
        self.presenter = ExplorePresenter(ExploreModel())

    def test_post_boss_dungeon_encounter_starts_glitch_clone(self) -> None:
        game = _make_game(in_dungeon=True, glitch_lord_defeated=True)

        with patch(
            "src.scenes.explore.presenter.random.random",
            return_value=0.0,
        ):
            self.presenter._check_random_encounter(game, M.T_FLOOR)

        game.battle_scene.start.assert_called_once_with(
            M.GLITCH_CLONE_DATA,
            is_glitch_lord=False,
        )

    def test_pre_boss_dungeon_encounter_keeps_zone_four_enemy(self) -> None:
        game = _make_game(in_dungeon=True, glitch_lord_defeated=False)
        expected_enemy = M.ZONE_ENEMIES[4][0]

        with patch(
            "src.scenes.explore.presenter.random.random",
            return_value=0.0,
        ), patch(
            "src.scenes.explore.presenter.random.choice",
            return_value=expected_enemy,
        ) as choice_mock:
            self.presenter._check_random_encounter(game, M.T_FLOOR)

        choice_mock.assert_called_once_with(M.ZONE_ENEMIES[4])
        game.battle_scene.start.assert_called_once_with(
            expected_enemy,
            is_glitch_lord=False,
        )

    def test_world_encounter_stays_on_zone_enemies(self) -> None:
        game = _make_game(in_dungeon=False, glitch_lord_defeated=True, y=0)
        expected_enemy = M.ZONE_ENEMIES[0][0]

        with patch(
            "src.scenes.explore.presenter.random.random",
            return_value=0.0,
        ), patch(
            "src.scenes.explore.presenter.random.choice",
            return_value=expected_enemy,
        ) as choice_mock:
            self.presenter._check_random_encounter(game, M.T_GRASS)

        choice_mock.assert_called_once_with(M.ZONE_ENEMIES[0])
        game.battle_scene.start.assert_called_once_with(
            expected_enemy,
            is_glitch_lord=False,
        )


if __name__ == "__main__":
    unittest.main()
