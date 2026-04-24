"""CJG/dialogue: DIALOGUE_JA と DIALOGUE_EN のシーン集合が揃っている。

根拠:
- docs/product-requirements-narrative.md（日英両対応）
- docs/customer-journeys.md（BDF が読めない環境でも話が進むこと）

日本語版でだけシーンがあると英語モードで `KeyError` で落ちる。逆も然り。
`next:` 参照の全一致（dangling reference 無し）は dialog_runner 側の
_validate_scenes で検出されるが、日英整合はここで固定化する。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.generated.dialogue import DIALOGUE_EN, DIALOGUE_JA


class DialogueLanguageParityTest(unittest.TestCase):
    def test_ja_and_en_have_the_same_scene_names(self):
        ja_scenes = set(DIALOGUE_JA.get("scenes", {}).keys())
        en_scenes = set(DIALOGUE_EN.get("scenes", {}).keys())

        only_ja = ja_scenes - en_scenes
        only_en = en_scenes - ja_scenes

        self.assertEqual(only_ja, set(), f"英語版に無いシーン: {only_ja}")
        self.assertEqual(only_en, set(), f"日本語版に無いシーン: {only_en}")

    def test_ja_and_en_have_the_same_variables(self):
        ja_vars = set(DIALOGUE_JA.get("variables", []))
        en_vars = set(DIALOGUE_EN.get("variables", []))

        self.assertEqual(ja_vars, en_vars, "日英 variables が一致しない")

    def test_at_least_100_scenes_exist(self):
        """ナラティブ量の下限（リファクタ時に誤って大量削除が起きないか）。"""
        self.assertGreaterEqual(len(DIALOGUE_JA.get("scenes", {})), 100)


class DialogueNextReferencesTest(unittest.TestCase):
    """next: で参照されているシーン名が存在する（dangling reference 無し）。"""

    def _collect_next_refs(self, dialogue):
        refs: set[str] = set()
        scenes = dialogue.get("scenes", {})
        for scene in scenes.values():
            if "next" in scene:
                refs.add(scene["next"])
            for variant in scene.get("variants", []):
                if "next" in variant:
                    refs.add(variant["next"])
                for choice in variant.get("choices", []):
                    if isinstance(choice, dict) and "next" in choice:
                        refs.add(choice["next"])
            for choice in scene.get("choices", []):
                if isinstance(choice, dict) and "next" in choice:
                    refs.add(choice["next"])
        return refs

    def test_every_next_reference_in_ja_resolves(self):
        scenes = set(DIALOGUE_JA.get("scenes", {}).keys())
        refs = self._collect_next_refs(DIALOGUE_JA)
        dangling = refs - scenes
        self.assertEqual(dangling, set(), f"JA: next で参照されていて実体が無い: {dangling}")

    def test_every_next_reference_in_en_resolves(self):
        scenes = set(DIALOGUE_EN.get("scenes", {}).keys())
        refs = self._collect_next_refs(DIALOGUE_EN)
        dangling = refs - scenes
        self.assertEqual(dangling, set(), f"EN: next で参照されていて実体が無い: {dangling}")


class DialogueSceneShapeTest(unittest.TestCase):
    """各シーンは text または variants のどちらかを持つ。両方とも空だと描画が空になる。"""

    def test_every_ja_scene_has_text_or_variants(self):
        for name, scene in DIALOGUE_JA.get("scenes", {}).items():
            with self.subTest(scene=name):
                has_text = "text" in scene and scene["text"]
                has_variants = "variants" in scene and scene["variants"]
                self.assertTrue(
                    has_text or has_variants,
                    f"JA scene `{name}` に text も variants も無い",
                )


if __name__ == "__main__":
    unittest.main()
