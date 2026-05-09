from __future__ import annotations

import unittest

from src.scenes.battle.model import BattleModel
from src.scenes.battle.presenter import BattlePresenter
from src.scenes.battle.scene import BattleScene
from src.shared.services.dialog_runner import StructuredDialogRunner
from src.scenes.explore.model import ExploreModel
from src.scenes.explore.presenter import ExplorePresenter
from src.scenes.explore.scene import ExploreScene
from src.scenes.title.model import TitleModel
from src.scenes.title.presenter import TitlePresenter
from src.scenes.title.scene import TitleScene
from src.shared.services.scene_manager import SceneManager
from src.shared.ui.dialog_window import DialogWindow
from src.shared.ui.hud import HudLayout
from src.shared.ui.menu_window import MenuWindow


class SharedSceneManagerTest(unittest.TestCase):
    def test_scene_manager_tracks_previous_scene_name(self):
        manager = SceneManager()

        manager.set("title")
        manager.set("battle")

        self.assertEqual(manager.previous, "title")
        self.assertEqual(manager.current, "battle")


class TitleSceneTest(unittest.TestCase):
    def test_presenter_wraps_cursor(self):
        # 2026-05-07 改訂（CJ44 確定版）：settings_open は撤去済（設定画面廃止）
        model = TitleModel(cursor=0)
        presenter = TitlePresenter(model)

        presenter.move(-1, item_count=2)

        self.assertEqual(model.cursor, 1)

    def test_scene_draw_returns_title_snapshot(self):
        scene = TitleScene(model=TitleModel(cursor=1))

        snapshot = scene.draw()

        self.assertEqual(
            snapshot,
            {"title": "Block Quest", "cursor": 1},
        )


class ExploreSceneTest(unittest.TestCase):
    def test_presenter_changes_mode(self):
        model = ExploreModel(mode="map")
        presenter = ExplorePresenter(model)

        presenter.change_mode("shop")

        self.assertEqual(model.mode, "shop")

    def test_scene_draw_returns_mode_snapshot(self):
        scene = ExploreScene(model=ExploreModel(mode="save"))

        snapshot = scene.draw()

        self.assertEqual(snapshot, {"mode": "save"})


class BattleSceneTest(unittest.TestCase):
    def test_presenter_changes_phase(self):
        model = BattleModel(phase="command")
        presenter = BattlePresenter(model)

        presenter.change_phase("result")

        self.assertEqual(model.phase, "result")

    def test_scene_draw_returns_phase_snapshot(self):
        scene = BattleScene(model=BattleModel(phase="enemy_attack"))

        snapshot = scene.draw()

        self.assertEqual(snapshot, {"phase": "enemy_attack"})


# J53 Q1A: DialogScene / DialogPresenter / DialogView は解体された。
# dialog は shared/services/dialog_runner.py の StructuredDialogRunner として
# scene から呼ばれる utility になる。旧 DialogSceneTest は削除。


class SharedUiTest(unittest.TestCase):
    def test_dialog_window_reports_rect(self):
        self.assertEqual(DialogWindow().rect(), (8, 208, 240, 44))

    def test_menu_window_reports_rect(self):
        self.assertEqual(MenuWindow().rect(), (20, 40, 216, 170))

    def test_hud_layout_reports_origin(self):
        self.assertEqual(HudLayout(top_margin=4, left_margin=12).origin(), (12, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
