from __future__ import annotations

import ast
import sys
import types
import unittest
from pathlib import Path


PYXEL_ROOT = Path(__file__).resolve().parent.parent
MAIN_RUNTIME = PYXEL_ROOT / "src" / "runtime" / "main_runtime.py"
SCENE_PREFIXES = {"battle", "boss", "castle", "dungeon", "ending", "landmark", "town"}


def load_bundled_module(path: Path, module_name: str):
    source = path.read_text(encoding="utf-8")
    source = source.replace("\ngame = Game()\ngame.start()\n", "\n")
    module = types.ModuleType(module_name)
    module.__file__ = str(path.resolve())
    sys.modules[module_name] = module
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    return module


def extract_dialog_scene_ids(path: Path) -> set[str]:
    scene_ids: set[str] = set()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant) or not isinstance(node.value, str):
            continue
        value = node.value
        parts = value.split(".")
        if len(parts) < 3:
            continue
        if parts[0] not in SCENE_PREFIXES:
            continue
        if "{" in value or value.endswith("_"):
            continue
        if not all(part.replace("_", "").isalnum() for part in parts):
            continue
        scene_ids.add(value)
    return scene_ids


class DialogueIntegrationTest(unittest.TestCase):
    def assert_bundled_dialogue_covers_runtime_scene_ids(
        self,
        filename: str,
        module_name: str,
    ):
        path = PYXEL_ROOT / filename
        module = load_bundled_module(path, module_name)
        scene_ids = extract_dialog_scene_ids(path)

        missing_ja = sorted(scene for scene in scene_ids if scene not in module.DIALOGUE_JA["scenes"])
        missing_en = sorted(scene for scene in scene_ids if scene not in module.DIALOGUE_EN["scenes"])

        self.assertEqual(missing_ja, [], f"{filename} missing JA scenes: {missing_ja}")
        self.assertEqual(missing_en, [], f"{filename} missing EN scenes: {missing_en}")

    def test_main_references_scene_names_instead_of_runtime_text(self):
        """main.py とその scene モジュールがダイアログシーン名を参照していること。

        J53 P1-G 以降、runtime の責務は scenes/ / shared/services/ に分散している。
        main_runtime.py 単体ではなく、scenes を含めた集合でシンボル参照を検証する。
        """
        main_text = MAIN_RUNTIME.read_text(encoding="utf-8")
        landmark_text = (PYXEL_ROOT / "src" / "shared" / "services" / "landmark_events.py").read_text(
            encoding="utf-8"
        )
        # J53 P1-G: scenes/ と shared/services/ に移動したシンボルも集める
        # J53 P1.5: shared/constants/ と runtime/app.py にも一部シンボルが移動
        extra_texts: list[str] = []
        for scene_dir in (PYXEL_ROOT / "src" / "scenes").iterdir():
            if scene_dir.is_dir():
                for py in scene_dir.glob("*.py"):
                    extra_texts.append(py.read_text(encoding="utf-8"))
        for svc in (PYXEL_ROOT / "src" / "shared" / "services").glob("*.py"):
            extra_texts.append(svc.read_text(encoding="utf-8"))
        for const in (PYXEL_ROOT / "src" / "shared" / "constants").glob("*.py"):
            extra_texts.append(const.read_text(encoding="utf-8"))
        extra_texts.append((PYXEL_ROOT / "src" / "runtime" / "app.py").read_text(encoding="utf-8"))
        combined_text = main_text + "\n".join(extra_texts)

        for expected in (
            "find_landmark_event",
            "landmarkTreeSeen",
            "landmarkTowerSeen",
            "castle.professor.entry",
            "dungeon.glitch.enter",
            "dungeon.glitch.exit",
            "battle.normal.run.success",
            "battle.normal.run.fail",
            "battle.normal.item.heal",
            "battle.normal.item.mp_heal",
            "battle.normal.enemy_hit.sequential",
            "battle.normal.victory.early",
            "battle.normal.victory.mid",
            "battle.normal.victory.late",
            "battle.normal.defeat",
            "ending.main.line01",
            "castle.professor.intro_01",
            "castle.professor.silent_victory",
            "castle.professor.epilogue_01",
            "castle.professor.accepted_01",
            "castle.professor.revisit_intro_01",
            "castle.professor.revisit_epilogue_01",
            "TOWN_NPC_LINES",
        ):
            self.assertIn(expected, combined_text)

        for scene_name in (
            "landmark.tree.first",
            "landmark.tower.first",
        ):
            self.assertIn(scene_name, landmark_text)

    # P3-A: preview/development 関連テストは dev 版削除に伴い削除済み
    # （test_main_preview_* 3 件、test_main_inlined_dialogue_covers 1 件）

    def test_main_inlined_dialogue_covers_runtime_scene_ids(self):
        self.assert_bundled_dialogue_covers_runtime_scene_ids(
            "src/runtime/main_runtime.py",
            "main_dialogue_scene_coverage_test",
        )

    def test_main_uses_shared_input_bindings(self):
        """main.py が入力バインディングのシンボルを使っていること。

        P1.5 後は main_runtime.py は re-export shim なので、app.py や scene も
        含めてシンボルを探索する。
        """
        main_text = MAIN_RUNTIME.read_text(encoding="utf-8")
        main_text += "\n" + (PYXEL_ROOT / "src" / "runtime" / "app.py").read_text(encoding="utf-8")
        for scene_dir in (PYXEL_ROOT / "src" / "scenes").iterdir():
            if scene_dir.is_dir():
                for py in scene_dir.glob("*.py"):
                    main_text += "\n" + py.read_text(encoding="utf-8")
        main_text += "\n" + (PYXEL_ROOT / "src" / "shared" / "services" / "input_bindings.py").read_text(encoding="utf-8")

        for expected in (
            "UP_BUTTONS",
            "DOWN_BUTTONS",
            "LEFT_BUTTONS",
            "RIGHT_BUTTONS",
            "CONFIRM_BUTTONS",
            "CANCEL_BUTTONS",
            "TITLE_START_BUTTONS",
            "InputStateTracker",
            "any_btn",
        ):
            self.assertIn(expected, main_text)

    def test_main_uses_view_direct_playm_for_bgm(self):
        """2026-05-07 改訂（CJ44 確定版・追加整理）：BGM は各 scene の view.py が
        ``audio_system.play_bgm_track(target)`` を呼ぶことで pyxel.playm を
        冪等に発火する。AudioManager / choose_bgm_scene 等の中央集権は撤去済、
        ``Game.current_bgm`` のような中央集権状態も持たない。
        """
        scenes_root = PYXEL_ROOT / "src" / "scenes"
        bgm_callers = []
        for view_file in scenes_root.glob("*/view.py"):
            text = view_file.read_text(encoding="utf-8")
            # 直接 pyxel.playm を呼ぶ legacy パターンと、play_bgm_track を
            # 経由する CJ44 追加整理パターンの両方を許容する。
            if "pyxel.playm(" in text or "play_bgm_track(" in text:
                bgm_callers.append(view_file.name)
        # 主要 BGM シーンの view が BGM 発火点を持つこと（title/explore/battle/ending）
        self.assertGreaterEqual(
            len(bgm_callers), 4,
            f"title/explore/battle/ending の view.py が play_bgm_track or pyxel.playm を呼ぶこと: {bgm_callers}",
        )

    def test_view_does_not_persist_bgm_state_on_game(self):
        """CJ44 確定版（追加整理）：view.py は ``game.current_bgm`` のような
        Game への状態書き込みをしないこと。BGM の冪等性は audio_system が一手に持つ。
        """
        scenes_root = PYXEL_ROOT / "src" / "scenes"
        offenders = []
        for view_file in scenes_root.glob("*/view.py"):
            text = view_file.read_text(encoding="utf-8")
            # 「game.current_bgm = ...」のような代入や読み取りは禁止。
            # docstring 中の説明文（バッククォートや「持たない」等）は許可。
            for line in text.splitlines():
                stripped = line.lstrip()
                if stripped.startswith("#"):
                    continue
                if "game.current_bgm" in line and "``" not in line:
                    offenders.append(f"{view_file.name}: {line.strip()}")
        self.assertEqual(
            offenders, [],
            f"view.py は game.current_bgm に触れてはいけない: {offenders}",
        )

    def test_main_no_longer_hardcodes_dialogue_body_text(self):
        """main.py のダイアログ辞書 *外* にテキスト本文がハードコードされていないこと。

        main.py には DIALOGUE_JA / DIALOGUE_EN がインラインで含まれるため、
        辞書定義部分（'text': '...' 形式）は除外して検査する。
        """
        lines = MAIN_RUNTIME.read_text(encoding="utf-8").splitlines()
        # ダイアログ辞書の 'text': '...' 行を除外
        non_dialogue_text = "\n".join(
            line for line in lines if "'text':" not in line
        )

        for phrase in (
            "はじめの村へようこそ！",
            "町に立ち寄り、装備を整えよう。",
            "うまく逃げ切れた！",
            "逃げられない！",
            "まだ整理できていない…コインが半分になった。",
            "おめでとう！",
            "まおうグリッチをたおした！",
        ):
            self.assertNotIn(phrase, non_dialogue_text)

        self.assertNotIn("ATTACK_TEXTS = [", non_dialogue_text)


class ProfessorDialogueTest(unittest.TestCase):
    def setUp(self):
        from src.shared.services.dialog_runner import StructuredDialogRunner
        from src.game_data import DIALOGUE_JA
        self.runner = StructuredDialogRunner(DIALOGUE_JA)

    def test_intro_chains_to_choice_prompt(self):
        lines = self.runner.load_all_lines("castle.professor.intro_01")
        self.assertGreaterEqual(len(lines), 7)
        self.assertEqual(lines[-1], "どうする？")

    def test_revisit_intro_chains_to_choice_prompt(self):
        lines = self.runner.load_all_lines("castle.professor.revisit_intro_01")
        self.assertEqual(lines[-1], "どうする？")

    def test_epilogue_ends_with_encouragement(self):
        lines = self.runner.load_all_lines("castle.professor.epilogue_01")
        self.assertIn("まちがって", lines[-1])

    def test_accepted_ending_final_line(self):
        lines = self.runner.load_all_lines("castle.professor.accepted_01")
        self.assertEqual(len(lines), 4)
        self.assertIn("そうして", lines[-1])
        self.assertIn("おとなになっていくのだ", lines[-1])

    def test_all_phase_keys_exist(self):
        for thr in ("85", "70", "55", "40", "25", "10"):
            self.assertIn(f"castle.professor.phase_{thr}", self.runner.scenes)

    def test_silent_victory_scene_exists(self):
        self.assertIn("castle.professor.silent_victory", self.runner.scenes)


class GlitchLordDialogueTest(unittest.TestCase):
    def setUp(self):
        from src.shared.services.dialog_runner import StructuredDialogRunner
        from src.game_data import DIALOGUE_JA
        self.runner = StructuredDialogRunner(DIALOGUE_JA)

    def test_prebattle_intro_chains_multiple_lines(self):
        lines = self.runner.load_all_lines("boss.glitch.prebattle_01")
        self.assertGreaterEqual(len(lines), 3)
        self.assertTrue(all(lines))


if __name__ == "__main__":
    unittest.main(verbosity=2)
