from __future__ import annotations

import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_main_module():
    source = (ROOT / "main.py").read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType("main_for_dungeon_boss_trigger_test")
    module.__file__ = str((ROOT / "main.py").resolve())
    sys.modules[module.__name__] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


class DungeonBossTriggerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.main = load_main_module()

    def make_game(self):
        game = self.main.Game.__new__(self.main.Game)
        game.player = {"in_dungeon": True, "boss_defeated": False}
        game._start_battle = MagicMock()
        return game

    def test_generate_dungeon_places_single_boss_trigger_in_last_room(self):
        grid, rooms = self.main.generate_dungeon(seed=99)

        boss_tiles = [
            (x, y)
            for y, row in enumerate(grid)
            for x, tile in enumerate(row)
            if tile == self.main.T_BOSS_TRIGGER
        ]

        self.assertEqual(len(boss_tiles), 1)
        bx, by = boss_tiles[0]
        rx, ry, rw, rh = rooms[-1]
        self.assertTrue(rx <= bx < rx + rw)
        self.assertTrue(ry <= by < ry + rh)

        sx = rooms[0][0] + 1
        sy = rooms[0][1] + 1
        self.assertNotEqual((bx, by), (sx, sy))

    def test_check_tile_events_starts_boss_battle_on_boss_trigger(self):
        game = self.make_game()

        self.main.Game._check_tile_events(game, self.main.T_BOSS_TRIGGER, 7, 8)

        game._start_battle.assert_called_once_with(
            self.main.BOSS_DATA,
            is_boss=True,
        )

    def test_check_tile_events_ignores_boss_trigger_after_boss_defeated(self):
        game = self.make_game()
        game.player["boss_defeated"] = True

        self.main.Game._check_tile_events(game, self.main.T_BOSS_TRIGGER, 7, 8)

        game._start_battle.assert_not_called()


if __name__ == "__main__":
    unittest.main()
