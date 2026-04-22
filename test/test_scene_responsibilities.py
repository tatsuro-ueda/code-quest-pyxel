from __future__ import annotations

import unittest

from src.app import BlockQuestApp
from src.core.scene_manager import SceneManager
from src.scenes.battle.model import BattleModel
from src.scenes.battle.presenter import BattlePresenter
from src.scenes.battle.scene import BattleScene
from src.scenes.dialog.model import StructuredDialogRunner
from src.scenes.dialog.scene import DialogScene
from src.scenes.explore.model import ExploreModel
from src.scenes.explore.presenter import ExplorePresenter
from src.scenes.explore.scene import ExploreScene
from src.scenes.title.model import TitleModel
from src.scenes.title.presenter import TitlePresenter
from src.scenes.title.scene import TitleScene
from src.shared.ui.dialog_window import DialogWindow
from src.shared.ui.hud import HudLayout
from src.shared.ui.menu_window import MenuWindow


class _FakeScene:
    def __init__(self, name: str):
        self.name = name
        self.updated = 0
        self.drawn = 0

    def update(self) -> None:
        self.updated += 1

    def draw(self) -> dict[str, str]:
        self.drawn += 1
        return {"name": self.name}


class SceneManagerAndAppTest(unittest.TestCase):
    def test_scene_manager_tracks_history_and_previous_scene(self):
        manager = SceneManager()
        title = _FakeScene("title")
        battle = _FakeScene("battle")

        manager.set_scene(title)
        manager.set_scene(battle)

        self.assertEqual(manager.previous_scene_name, "title")
        self.assertEqual(manager.history, ["title"])

    def test_blockquest_app_delegates_to_scene_manager(self):
        manager = SceneManager()
        app = BlockQuestApp(scene_manager=manager)
        title = _FakeScene("title")
        app.set_scene(title)

        app.update()
        result = app.draw()

        self.assertEqual(title.updated, 1)
        self.assertEqual(title.drawn, 1)
        self.assertEqual(result, {"name": "title"})


class TitleSceneTest(unittest.TestCase):
    def test_presenter_wraps_cursor(self):
        model = TitleModel(cursor=0, settings_open=False)
        presenter = TitlePresenter(model)

        presenter.move(-1, item_count=3)

        self.assertEqual(model.cursor, 2)

    def test_scene_draw_returns_title_snapshot(self):
        scene = TitleScene(model=TitleModel(cursor=1, settings_open=True))

        snapshot = scene.draw()

        self.assertEqual(
            snapshot,
            {"title": "Block Quest", "cursor": 1, "settings_open": True},
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


class DialogSceneTest(unittest.TestCase):
    def test_scene_start_and_draw_return_active_step_snapshot(self):
        runner = StructuredDialogRunner(
            {
                "variables": [],
                "scenes": {
                    "hello": {
                        "speaker": "guide",
                        "text": "やあ！",
                        "choices": [{"text": "つぎへ", "next": "next"}],
                    },
                    "next": {"text": "つづきだよ"},
                },
            }
        )
        scene = DialogScene(runner=runner)

        step = scene.start("hello")
        snapshot = scene.draw()

        self.assertEqual(step.text, "やあ！")
        self.assertEqual(
            snapshot,
            {"speaker": "guide", "text": "やあ！", "choices": ["つぎへ"]},
        )

    def test_scene_choose_updates_active_step(self):
        runner = StructuredDialogRunner(
            {
                "variables": [],
                "scenes": {
                    "hello": {
                        "text": "やあ！",
                        "choices": [{"text": "つぎへ", "next": "next"}],
                    },
                    "next": {"text": "つづきだよ"},
                },
            }
        )
        scene = DialogScene(runner=runner)
        scene.start("hello")

        step = scene.choose(0)
        snapshot = scene.draw()

        self.assertEqual(step.text, "つづきだよ")
        self.assertEqual(snapshot, {"speaker": None, "text": "つづきだよ", "choices": []})


class SharedUiTest(unittest.TestCase):
    def test_dialog_window_reports_rect(self):
        self.assertEqual(DialogWindow().rect(), (8, 208, 240, 44))

    def test_menu_window_reports_rect(self):
        self.assertEqual(MenuWindow().rect(), (20, 40, 216, 170))

    def test_hud_layout_reports_origin(self):
        self.assertEqual(HudLayout(top_margin=4, left_margin=12).origin(), (12, 4))


if __name__ == "__main__":
    unittest.main(verbosity=2)
