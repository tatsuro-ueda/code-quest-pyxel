"""CJG/structure: src/scenes/ 配下が framework-rule.md M5-1 の構造に揃う。

根拠:
- docs/framework-rule.md M5-1（scene は model/presenter/view 構造を持つ）
- docs/repository-structure.md

各 scene ディレクトリに model.py / presenter.py / view.py が揃う。
town は例外的に scene.py を持たないが、他は scene.py（薄い配線）を持つ。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


SCENES_ROOT = ROOT / "src" / "scenes"
EXPECTED_MPV = ("model.py", "presenter.py", "view.py")


class SceneStructureTest(unittest.TestCase):
    def _scene_dirs(self):
        return sorted(
            p
            for p in SCENES_ROOT.iterdir()
            if p.is_dir() and not p.name.startswith("__")
        )

    def test_every_scene_has_init_py(self):
        for scene_dir in self._scene_dirs():
            with self.subTest(scene=scene_dir.name):
                self.assertTrue((scene_dir / "__init__.py").is_file())

    def test_every_scene_has_model_presenter_view(self):
        for scene_dir in self._scene_dirs():
            for required in EXPECTED_MPV:
                with self.subTest(scene=scene_dir.name, file=required):
                    self.assertTrue(
                        (scene_dir / required).is_file(),
                        f"{scene_dir.name}/{required} が無い",
                    )

    def test_town_scene_has_no_scene_py(self):
        """framework-rule.md M3-2 の縮退形：town は scene.py を持たない。"""
        self.assertFalse(
            (SCENES_ROOT / "town" / "scene.py").exists(),
            "town/scene.py が復活している。M3-2 縮退形が壊れた",
        )

    def test_every_non_town_scene_has_scene_py(self):
        """town 以外は薄い配線として scene.py を持つ。"""
        for scene_dir in self._scene_dirs():
            if scene_dir.name == "town":
                continue
            with self.subTest(scene=scene_dir.name):
                self.assertTrue(
                    (scene_dir / "scene.py").is_file(),
                    f"{scene_dir.name}/scene.py が無い",
                )


class NoExtraFilesInSceneDirsTest(unittest.TestCase):
    """scene ディレクトリに想定外の .py ファイルが混入しない（例: utils.py など）。"""

    _ALLOWED = (
        "__init__.py",
        "scene.py",
        "model.py",
        "presenter.py",
        "view.py",
        "view_model.py",  # town が使用
    )

    def _scene_dirs(self):
        return sorted(
            p
            for p in SCENES_ROOT.iterdir()
            if p.is_dir() and not p.name.startswith("__")
        )

    def test_no_unexpected_py_files_in_scene_dirs(self):
        for scene_dir in self._scene_dirs():
            for child in scene_dir.iterdir():
                if child.is_dir():
                    continue
                if child.suffix != ".py":
                    continue
                with self.subTest(file=str(child.relative_to(ROOT))):
                    self.assertIn(
                        child.name,
                        self._ALLOWED,
                        f"想定外の .py ファイル: {child.relative_to(ROOT)}",
                    )


if __name__ == "__main__":
    unittest.main()
