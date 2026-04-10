"""Tests for tools/build_web_release.py preview/promote features."""

from __future__ import annotations

import json
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from tools.build_web_release import (  # noqa: E402
    collect_release_paths,
    generate_selector,
    promote,
)


class TestGenerateSelector(unittest.TestCase):
    """selector.html テンプレートから index.html を生成するテスト"""

    def test_generates_index_with_change_list(self):
        build_dir = ROOT / ".build" / "test_selector"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            changes = ["スライムの HP を へらしたよ", "あたらしい まほう を ついか したよ"]
            result = generate_selector(
                build_dir, ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-preview.html",
                changes=changes,
            )
            self.assertTrue(result.exists())
            content = result.read_text(encoding="utf-8")
            self.assertIn("スライムの HP を へらしたよ", content)
            self.assertIn("あたらしい まほう を ついか したよ", content)
            self.assertIn("play-preview.html", content)
            self.assertIn("play.html", content)
            self.assertIn("おためしばん", content)
            self.assertIn("もとのままばん", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_empty_changes_still_generates(self):
        build_dir = ROOT / ".build" / "test_selector_empty"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir, ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-preview.html",
                changes=[],
            )
            self.assertTrue(result.exists())
            content = result.read_text(encoding="utf-8")
            self.assertIn("おためしばん", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)


class TestPreviewBuildPrerequisites(unittest.TestCase):
    """--preview ビルドの前提条件テスト"""

    def test_preview_requires_main_preview_py(self):
        """main_preview.py が存在しないとき FileNotFoundError"""
        fake_root = ROOT / ".build" / "test_no_preview"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            # main_preview.py が存在しないことを確認
            preview_path = fake_root / "main_preview.py"
            if preview_path.exists():
                preview_path.unlink()
            with self.assertRaises(FileNotFoundError):
                from tools.build_web_release import validate_preview_files
                validate_preview_files(fake_root)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)


class TestPromote(unittest.TestCase):
    """--promote コマンドのテスト"""

    def setUp(self):
        self.work_dir = ROOT / ".build" / "test_promote"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        # main.py を作成
        (self.work_dir / "main.py").write_text("# original", encoding="utf-8")
        # main_preview.py を作成
        (self.work_dir / "main_preview.py").write_text("# preview", encoding="utf-8")
        # preview_meta.json を作成
        (self.work_dir / "preview_meta.json").write_text(
            json.dumps({"changes": ["test"]}), encoding="utf-8"
        )

    def tearDown(self):
        shutil.rmtree(self.work_dir, ignore_errors=True)

    def test_promote_preview_replaces_main(self):
        promote(self.work_dir, choice="preview")
        main_content = (self.work_dir / "main.py").read_text(encoding="utf-8")
        self.assertEqual(main_content, "# preview")
        self.assertFalse((self.work_dir / "main_preview.py").exists())
        self.assertFalse((self.work_dir / "preview_meta.json").exists())

    def test_promote_current_removes_preview(self):
        promote(self.work_dir, choice="current")
        main_content = (self.work_dir / "main.py").read_text(encoding="utf-8")
        self.assertEqual(main_content, "# original")
        self.assertFalse((self.work_dir / "main_preview.py").exists())
        self.assertFalse((self.work_dir / "preview_meta.json").exists())


if __name__ == "__main__":
    unittest.main()
