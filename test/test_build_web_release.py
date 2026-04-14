"""Tests for tools/build_web_release.py preview/promote features."""

from __future__ import annotations

import json
import os
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
    generate_top_selector,
    generate_wrapper,
    load_top_page_changes,
    promote,
    validate_preview_files,
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


class TestTopPageChanges(unittest.TestCase):
    def test_load_top_page_changes_reads_json(self):
        fake_root = ROOT / ".build" / "test_top_changes"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            (fake_root / "top_changes.json").write_text(
                json.dumps({"changes": ["ボスを ついか", "さいごの へやを しゅうせい"]}),
                encoding="utf-8",
            )
            changes = load_top_page_changes(fake_root)
            self.assertEqual(changes, ["ボスを ついか", "さいごの へやを しゅうせい"])
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_generate_top_selector_uses_top_changes_json(self):
        fake_root = ROOT / ".build" / "test_top_selector_root"
        build_dir = ROOT / ".build" / "test_top_selector_out"
        (fake_root / "templates").mkdir(parents=True, exist_ok=True)
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(ROOT / "templates" / "selector.html", fake_root / "templates" / "selector.html")
            (fake_root / "top_changes.json").write_text(
                json.dumps({"changes": ["ボスを ついか", "さいごの へやで たたかえる"]}),
                encoding="utf-8",
            )

            result = generate_top_selector(
                build_dir,
                fake_root,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-preview.html",
            )

            content = result.read_text(encoding="utf-8")
            self.assertIn("ボスを ついか", content)
            self.assertIn("さいごの へやで たたかえる", content)
            self.assertIn('href="play.html"', content)
            self.assertIn('href="play-preview.html"', content)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_load_top_page_changes_rejects_stale_json(self):
        fake_root = ROOT / ".build" / "test_stale_top_changes"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            top_changes = fake_root / "top_changes.json"
            main_py = fake_root / "main.py"
            top_changes.write_text(
                json.dumps({"changes": ["ふるい せつめい"]}),
                encoding="utf-8",
            )
            main_py.write_text("# newer gameplay change", encoding="utf-8")
            os.utime(top_changes, (1_000_000_000, 1_000_000_000))
            os.utime(main_py, (1_000_000_100, 1_000_000_100))

            with self.assertRaises(ValueError):
                load_top_page_changes(fake_root)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)


class TestSelectorDoesNotLinkDirectlyToPyxelHtml(unittest.TestCase):
    """選択ページが pyxel*.html に直リンクせず wrapper 経由であること"""

    def test_selector_links_to_wrappers_not_raw_pyxel(self):
        build_dir = ROOT / ".build" / "test_selector_links"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir, ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-preview.html",
                changes=["test"],
            )
            content = result.read_text(encoding="utf-8")
            # wrapper 経由のリンクが存在する
            self.assertIn('href="play.html"', content)
            self.assertIn('href="play-preview.html"', content)
            # pyxel.html / pyxel-preview.html への直リンクがない
            self.assertNotIn('href="pyxel.html"', content)
            self.assertNotIn('href="pyxel-preview.html"', content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)


class TestWrapperEmbedsCorrectPyxelHtml(unittest.TestCase):
    """wrapper が正しい pyxel HTML を iframe で埋め込むこと"""

    def test_wrapper_for_current_embeds_pyxel_html(self):
        build_dir = ROOT / ".build" / "test_wrapper_current"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_wrapper(build_dir, ROOT, pyxel_html_name="pyxel.html")
            content = result.read_text(encoding="utf-8")
            self.assertIn('src="pyxel.html"', content)
            self.assertIn("allowfullscreen", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_wrapper_for_preview_embeds_pyxel_preview_html(self):
        build_dir = ROOT / ".build" / "test_wrapper_preview"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_wrapper(build_dir, ROOT, pyxel_html_name="pyxel-preview.html")
            content = result.read_text(encoding="utf-8")
            self.assertIn('src="pyxel-preview.html"', content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_wrapper_embeds_play_session_logging_config(self):
        build_dir = ROOT / ".build" / "test_wrapper_logging"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_wrapper(
                build_dir,
                ROOT,
                pyxel_html_name="pyxel.html",
                page_kind="current",
                session_api_base="/internal/play-sessions",
            )
            content = result.read_text(encoding="utf-8")
            self.assertIn('data-page-kind="current"', content)
            self.assertIn("/internal/play-sessions", content)
            self.assertIn("/start", content)
            self.assertIn("/heartbeat", content)
            self.assertIn("/end", content)
            self.assertIn("navigator.sendBeacon", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)


class TestPreviewLinkChain(unittest.TestCase):
    """selector → wrapper → pyxel のリンクチェーン全体が整合すること"""

    def test_full_link_chain(self):
        """selector→play.html→pyxel.html, selector→play-preview.html→pyxel-preview.html"""
        build_dir = ROOT / ".build" / "test_chain"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            # selector
            selector = generate_selector(
                build_dir, ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-preview.html",
                changes=["てすと"],
            )
            selector_content = selector.read_text(encoding="utf-8")

            # wrappers
            wrapper_dir = build_dir / "wrappers"
            wrapper_dir.mkdir(exist_ok=True)
            w_current = generate_wrapper(wrapper_dir, ROOT, pyxel_html_name="pyxel.html")
            w_preview_dir = build_dir / "wrappers_p"
            w_preview_dir.mkdir(exist_ok=True)
            w_preview = generate_wrapper(w_preview_dir, ROOT, pyxel_html_name="pyxel-preview.html")

            w_current_content = w_current.read_text(encoding="utf-8")
            w_preview_content = w_preview.read_text(encoding="utf-8")

            # chain: selector → play.html → pyxel.html
            self.assertIn('href="play.html"', selector_content)
            self.assertIn('src="pyxel.html"', w_current_content)

            # chain: selector → play-preview.html → pyxel-preview.html
            self.assertIn('href="play-preview.html"', selector_content)
            self.assertIn('src="pyxel-preview.html"', w_preview_content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)


class TestPreviewBuildPrerequisites(unittest.TestCase):
    """--preview ビルドの前提条件テスト"""

    def test_preview_requires_main_preview_py(self):
        """main_preview.py が存在しないとき FileNotFoundError"""
        fake_root = ROOT / ".build" / "test_no_preview"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            preview_path = fake_root / "main_preview.py"
            if preview_path.exists():
                preview_path.unlink()
            with self.assertRaises(FileNotFoundError):
                validate_preview_files(fake_root)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_preview_reads_changes_from_meta_json(self):
        """preview_meta.json から変更リストを読めること"""
        fake_root = ROOT / ".build" / "test_meta"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            (fake_root / "main_preview.py").write_text("# preview", encoding="utf-8")
            (fake_root / "preview_meta.json").write_text(
                json.dumps({"changes": ["HP を へらした", "まほう を ついか"]}),
                encoding="utf-8",
            )
            _, changes = validate_preview_files(fake_root)
            self.assertEqual(changes, ["HP を へらした", "まほう を ついか"])
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_preview_rejects_stale_meta_json(self):
        """main_preview.py のほうが新しいのに preview_meta.json が古いと失敗する"""
        fake_root = ROOT / ".build" / "test_stale_meta"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            preview_py = fake_root / "main_preview.py"
            meta_json = fake_root / "preview_meta.json"
            preview_py.write_text("# newer preview", encoding="utf-8")
            meta_json.write_text(
                json.dumps({"changes": ["ふるい せつめい"]}),
                encoding="utf-8",
            )
            os.utime(meta_json, (1_000_000_000, 1_000_000_000))
            os.utime(preview_py, (1_000_000_100, 1_000_000_100))

            with self.assertRaises(ValueError):
                validate_preview_files(fake_root)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_preview_works_without_meta_json(self):
        """preview_meta.json がなくても動くこと（変更リストは空）"""
        fake_root = ROOT / ".build" / "test_no_meta"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            (fake_root / "main_preview.py").write_text("# preview", encoding="utf-8")
            _, changes = validate_preview_files(fake_root)
            self.assertEqual(changes, [])
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


class TestMainPyWebSafety(unittest.TestCase):
    """main.py が Web 環境(emscripten)で安全に動くことを静的検証する"""

    def setUp(self):
        self.source = (ROOT / "main.py").read_text(encoding="utf-8")

    def test_sys_is_imported(self):
        """sys.platform を使っているなら import sys が必要"""
        if "sys.platform" in self.source:
            # 'import sys' が from __future__ の後、クラス定義の前にある
            self.assertIn("import sys", self.source)

    def test_pyxel_save_always_guarded_by_emscripten_check(self):
        """pyxel.save() の全呼び出しが sys.platform != 'emscripten' で囲まれている"""
        lines = self.source.split("\n")
        for i, line in enumerate(lines):
            stripped = line.strip()
            if "pyxel.save(" in stripped and not stripped.startswith("#"):
                # この行より前の近くに emscripten ガードがあること
                context = "\n".join(lines[max(0, i - 5) : i + 1])
                self.assertIn(
                    "emscripten",
                    context,
                    f"line {i+1}: pyxel.save() に emscripten ガードがありません:\n{line}",
                )


if __name__ == "__main__":
    unittest.main()
