"""test_runtime_shim: Phase 1.5-E の gherkin シナリオ 2（monolith 残留ゼロ）を固定。

`src/runtime/main_runtime.py` は re-export shim のはず。Game クラスや inlined
コピーが再出現していないかを grep 式で検査し、行数が 50 未満に保たれていることを
assert する。
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIN_RUNTIME = ROOT / "src" / "runtime" / "main_runtime.py"


class RuntimeShimTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = MAIN_RUNTIME.read_text(encoding="utf-8")
        self.lines = self.text.splitlines()

    def test_line_count_is_under_50(self):
        """main_runtime.py は 50 行未満に保つ（P1-gherkin シナリオ 2）。"""
        self.assertLess(
            len(self.lines),
            50,
            f"main_runtime.py is {len(self.lines)} lines; expected < 50",
        )

    def test_no_game_class_definition(self):
        """Game クラスは src/runtime/app.py に移動済み。main_runtime.py に再出現していないこと。"""
        self.assertNotRegex(
            self.text,
            r"(?m)^class Game\b",
            "Game class should not be defined in main_runtime.py (moved to src/runtime/app.py)",
        )

    def test_no_inlined_service_classes(self):
        """サービス系クラスは shared/services/* に集約済み。main_runtime.py に定義が残っていないこと。"""
        forbidden = [
            "InputStateTracker",
            "SaveStore",
            "AudioManager",
            "StructuredDialogRunner",
            "SfxSystem",
            "LandmarkEvent",
            "InMemorySaveStore",
            "FileSaveStore",
            "LocalStorageSaveStore",
        ]
        for name in forbidden:
            self.assertNotRegex(
                self.text,
                rf"(?m)^class {re.escape(name)}\b",
                f"{name} class should not be defined in main_runtime.py",
            )

    def test_no_inlined_module_functions(self):
        """world/battle/audio の module-level 関数は shared に集約済み。"""
        forbidden = [
            "any_btn",
            "any_btnp",
            "generate_world_map",
            "generate_dungeon",
            "load_enemies",
            "choose_bgm_scene",
            "create_initial_player",
            "stage_browser_imported_resource",
        ]
        for name in forbidden:
            # function DEFINITION (top-level `def foo(...)`)
            pattern = rf"(?m)^def {re.escape(name)}\s*\("
            self.assertNotRegex(
                self.text,
                pattern,
                f"{name}() should not be defined in main_runtime.py",
            )

    def test_app_run_re_exported(self):
        """`run` entry point は app.run の thin wrapper として残っている。"""
        self.assertIn("from src.runtime.app import", self.text)
        self.assertIn("def run(", self.text)

    def test_imports_scenes_and_services(self):
        """shim が scene / service を適切に再エクスポートしている。"""
        for expected in (
            "from src.shared.services.input_bindings",
            "from src.shared.services.audio_system",
            "from src.shared.constants.tile_data",
            "from src.shared.services.world_generation",
            "from src.scenes.battle.scene import BattleScene",
            "from src.runtime.app import Game",
        ):
            self.assertIn(expected, self.text)


if __name__ == "__main__":
    unittest.main()
