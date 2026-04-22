"""Tests for tools/build_web_release.py preview release flow."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from tools.build_web_release import (  # noqa: E402
    approve_development,
    build_development_release,
    build_web_release,
    collect_release_paths,
    generate_selector,
    generate_top_selector,
    generate_wrapper,
    load_top_page_changes,
    main as build_web_release_main,
    promote,
    reject_development,
    resolve_pyxel_command,
    validate_development_files,
)
from tools.build_codemaker import build_codemaker_main_text  # noqa: E402
from src.shared.services.codemaker_resource_store import import_codemaker_resource_zip  # noqa: E402


def copy_web_release_fixture(dst_root: Path, *, include_preview: bool = False) -> None:
    (dst_root / "assets").mkdir(parents=True, exist_ok=True)
    (dst_root / "templates").mkdir(parents=True, exist_ok=True)

    shutil.copy2(ROOT / "main.py", dst_root / "main.py")
    shutil.copy2(ROOT / "assets" / "blockquest.pyxres", dst_root / "assets" / "blockquest.pyxres")
    shutil.copy2(ROOT / "assets" / "umplus_j10r.bdf", dst_root / "assets" / "umplus_j10r.bdf")
    shutil.copy2(ROOT / "templates" / "wrapper.html", dst_root / "templates" / "wrapper.html")
    shutil.copy2(ROOT / "templates" / "selector.html", dst_root / "templates" / "selector.html")
    shutil.copy2(ROOT / "templates" / "codemaker_import_ui.js", dst_root / "templates" / "codemaker_import_ui.js")
    if (ROOT / "top_changes.json").exists():
        shutil.copy2(ROOT / "top_changes.json", dst_root / "top_changes.json")
        os.utime(dst_root / "top_changes.json", None)
    if include_preview:
        shutil.copy2(ROOT / "main_development.py", dst_root / "main_development.py")
        main_path = dst_root / "main.py"
        preview_path = dst_root / "main_development.py"
        if main_path.read_text(encoding="utf-8") == preview_path.read_text(encoding="utf-8"):
            main_path.write_text(
                main_path.read_text(encoding="utf-8").replace(
                    '\n            or e.get("is_noise_guardian")',
                    "",
                ),
                encoding="utf-8",
            )
            if (dst_root / "top_changes.json").exists():
                os.utime(dst_root / "top_changes.json", None)


def production_dir(output_dir: Path) -> Path:
    return output_dir / "production"


def development_dir(output_dir: Path) -> Path:
    return output_dir / "development"


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
                preview_wrapper_name="play-development.html",
                changes=changes,
            )
            self.assertTrue(result.exists())
            content = result.read_text(encoding="utf-8")
            self.assertIn("スライムの HP を へらしたよ", content)
            self.assertIn("あたらしい まほう を ついか したよ", content)
            self.assertIn("play-development.html", content)
            self.assertIn("play.html", content)
            self.assertIn("開発版", content)
            self.assertIn("本番", content)
            self.assertNotIn("おためしばん", content)
            self.assertNotIn("もとのままばん", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_empty_changes_still_generates(self):
        build_dir = ROOT / ".build" / "test_selector_empty"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir, ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                changes=[],
            )
            self.assertTrue(result.exists())
            content = result.read_text(encoding="utf-8")
            self.assertIn("開発版", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_empty_preview_wrapper_hides_preview_card(self):
        build_dir = ROOT / ".build" / "test_selector_no_preview"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir,
                ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="",
                changes=["にげる しっぱいを しゅうせい"],
            )
            content = result.read_text(encoding="utf-8")
            self.assertNotIn("開発版", content)
            self.assertNotIn("play-development.html", content)
            self.assertNotIn("りょうほう あそんだら", content)
            self.assertIn("本番", content)
            self.assertIn("play.html", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_selector_contains_code_server_link(self):
        build_dir = ROOT / ".build" / "test_selector_code_server_link"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir,
                ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                changes=["にげる しっぱいを しゅうせい"],
            )
            content = result.read_text(encoding="utf-8")
            self.assertIn('id="code-server-link"', content)
            self.assertIn(":8081/", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_selector_contains_preview_codemaker_download_link(self):
        build_dir = ROOT / ".build" / "test_selector_preview_codemaker_link"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir,
                ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                preview_zip_name="code-maker-development.zip",
                changes=["にげる しっぱいを しゅうせい"],
            )
            content = result.read_text(encoding="utf-8")
            self.assertIn('href="code-maker-development.zip"', content)
            self.assertIn("リソースファイルをダウンロード", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_selector_contains_preview_pyxel_codemaker_link(self):
        build_dir = ROOT / ".build" / "test_selector_preview_pyxel_codemaker_link"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir,
                ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                preview_zip_name="code-maker-development.zip",
                changes=["にげる しっぱいを しゅうせい"],
            )
            content = result.read_text(encoding="utf-8")
            self.assertIn('href="https://kitao.github.io/pyxel/wasm/code-maker/"', content)
            self.assertIn("リソースエディタを開く", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_selector_hides_preview_codemaker_download_link_without_preview_zip(self):
        build_dir = ROOT / ".build" / "test_selector_no_preview_codemaker_link"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir,
                ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                changes=["にげる しっぱいを しゅうせい"],
            )
            content = result.read_text(encoding="utf-8")
            self.assertNotIn("code-maker-development.zip", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_selector_hides_preview_pyxel_codemaker_link_without_preview_zip(self):
        build_dir = ROOT / ".build" / "test_selector_no_preview_pyxel_codemaker_link"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir,
                ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                changes=["にげる しっぱいを しゅうせい"],
            )
            content = result.read_text(encoding="utf-8")
            self.assertNotIn("https://kitao.github.io/pyxel/wasm/code-maker/", content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_selector_contains_codemaker_resource_import_panel(self):
        build_dir = ROOT / ".build" / "test_selector_codemaker_import_panel"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = generate_selector(
                build_dir,
                ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                preview_zip_name="code-maker-development.zip",
                changes=["にげる しっぱいを しゅうせい"],
            )
            content = result.read_text(encoding="utf-8")
            self.assertIn('id="codemaker-import-panel"', content)
            self.assertNotIn('id="codemaker-import-panel" hidden', content)
            self.assertIn('id="codemaker-import-input" type="file" accept=".zip,application/zip"', content)
            self.assertNotIn('id="codemaker-import-input" type="file" accept=".zip,application/zip" disabled', content)
            self.assertIn('id="codemaker-import-button" type="button"', content)
            self.assertNotIn('id="codemaker-import-button" type="button" disabled', content)
            self.assertIn('id="codemaker-import-input"', content)
            self.assertIn("このブラウザに ほぞんします", content)
            self.assertIn("がぞう、マップ、こうかおん、おんがくだけを とりこみます", content)
            self.assertIn("プログラムは とりこみません", content)
            self.assertIn("zip を えらんでください", content)
            self.assertNotIn("このページでは まだ とりこめません", content)
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

    def test_generate_top_selector_uses_preview_meta_json(self):
        fake_root = ROOT / ".build" / "test_top_selector_root"
        build_dir = ROOT / ".build" / "test_top_selector_out"
        (fake_root / "templates").mkdir(parents=True, exist_ok=True)
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(ROOT / "templates" / "selector.html", fake_root / "templates" / "selector.html")
            shutil.copy2(ROOT / "templates" / "codemaker_import_ui.js", fake_root / "templates" / "codemaker_import_ui.js")
            (fake_root / "development_meta.json").write_text(
                json.dumps({
                    "base_production_hash": "base",
                    "development_hash": "development",
                    "changes": ["まおうを たおしたあとも つづきに すすめる"],
                }),
                encoding="utf-8",
            )
            (fake_root / "top_changes.json").write_text(
                json.dumps({"changes": ["ふるい current せつめい"]}),
                encoding="utf-8",
            )

            result = generate_top_selector(
                build_dir,
                fake_root,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
            )

            content = result.read_text(encoding="utf-8")
            self.assertIn("まおうを たおしたあとも つづきに すすめる", content)
            self.assertIn("ふるい current せつめい", content)
            self.assertIn('href="play.html"', content)
            self.assertIn('href="play-development.html"', content)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)
            shutil.rmtree(build_dir, ignore_errors=True)

    def test_generate_top_selector_shows_current_changes_without_preview(self):
        fake_root = ROOT / ".build" / "test_top_selector_current_only_root"
        build_dir = ROOT / ".build" / "test_top_selector_current_only_out"
        (fake_root / "templates").mkdir(parents=True, exist_ok=True)
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(ROOT / "templates" / "selector.html", fake_root / "templates" / "selector.html")
            shutil.copy2(ROOT / "templates" / "codemaker_import_ui.js", fake_root / "templates" / "codemaker_import_ui.js")
            (fake_root / "top_changes.json").write_text(
                json.dumps({"changes": ["まおうを たおしたあとも ぼうけんが つづく"]}),
                encoding="utf-8",
            )

            result = generate_top_selector(
                build_dir,
                fake_root,
                current_wrapper_name="play.html",
                preview_wrapper_name="",
            )

            content = result.read_text(encoding="utf-8")
            self.assertIn("まおうを たおしたあとも ぼうけんが つづく", content)
            self.assertNotIn("開発版", content)
            self.assertIn("本番", content)
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
                preview_wrapper_name="play-development.html",
                changes=["test"],
            )
            content = result.read_text(encoding="utf-8")
            # wrapper 経由のリンクが存在する
            self.assertIn('href="play.html"', content)
            self.assertIn('href="play-development.html"', content)
            # pyxel.html / pyxel-development.html への直リンクがない
            self.assertNotIn('href="pyxel.html"', content)
            self.assertNotIn('href="pyxel-development.html"', content)
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
            result = generate_wrapper(build_dir, ROOT, pyxel_html_name="pyxel-development.html")
            content = result.read_text(encoding="utf-8")
            self.assertIn('src="pyxel-development.html"', content)
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
                page_kind="production",
                session_api_base="/internal/play-sessions",
            )
            content = result.read_text(encoding="utf-8")
            self.assertIn('data-page-kind="production"', content)
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
        """selector→play.html→pyxel.html, selector→play-development.html→pyxel-development.html"""
        build_dir = ROOT / ".build" / "test_chain"
        build_dir.mkdir(parents=True, exist_ok=True)
        try:
            # selector
            selector = generate_selector(
                build_dir, ROOT,
                current_wrapper_name="play.html",
                preview_wrapper_name="play-development.html",
                changes=["てすと"],
            )
            selector_content = selector.read_text(encoding="utf-8")

            # wrappers
            wrapper_dir = build_dir / "wrappers"
            wrapper_dir.mkdir(exist_ok=True)
            w_current = generate_wrapper(wrapper_dir, ROOT, pyxel_html_name="pyxel.html")
            w_preview_dir = build_dir / "wrappers_p"
            w_preview_dir.mkdir(exist_ok=True)
            w_preview = generate_wrapper(w_preview_dir, ROOT, pyxel_html_name="pyxel-development.html")

            w_current_content = w_current.read_text(encoding="utf-8")
            w_preview_content = w_preview.read_text(encoding="utf-8")

            # chain: selector → play.html → pyxel.html
            self.assertIn('href="play.html"', selector_content)
            self.assertIn('src="pyxel.html"', w_current_content)

            # chain: selector → play-development.html → pyxel-development.html
            self.assertIn('href="play-development.html"', selector_content)
            self.assertIn('src="pyxel-development.html"', w_preview_content)
        finally:
            shutil.rmtree(build_dir, ignore_errors=True)


class TestPreviewBuildPrerequisites(unittest.TestCase):
    """--development ビルドの前提条件テスト"""

    def test_preview_requires_main_preview_py(self):
        """main_development.py が存在しないとき FileNotFoundError"""
        fake_root = ROOT / ".build" / "test_no_preview"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            preview_path = fake_root / "main_development.py"
            if preview_path.exists():
                preview_path.unlink()
            with self.assertRaises(FileNotFoundError):
                validate_development_files(fake_root)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_preview_generates_changes_from_diff(self):
        """preview の差分から変更リストを自動生成する"""
        fake_root = ROOT / ".build" / "test_meta"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            (fake_root / "main.py").write_text(
                "def _build_zone_enemies(enemies):\n    return []\n",
                encoding="utf-8",
            )
            (fake_root / "main_development.py").write_text(
                "def _build_zone_enemies(enemies):\n"
                "    if e.get(\"is_noise_guardian\"):\n"
                "        return []\n",
                encoding="utf-8",
            )
            _, changes = validate_development_files(fake_root)
            self.assertEqual(changes, ["つうしんとうの ノイズガーディアンが フィールドに でない"])
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_preview_generates_glitch_lord_conversation_change_from_diff(self):
        fake_root = ROOT / ".build" / "test_glitch_lord_preview_meta"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            (fake_root / "main.py").write_text(
                "tile == T_GLITCH_LORD_TRIGGER\n"
                "self._start_battle(GLITCH_LORD_DATA, is_glitch_lord=True)\n",
                encoding="utf-8",
            )
            (fake_root / "main_development.py").write_text(
                "tile == T_GLITCH_LORD_TRIGGER\n"
                "self._enter_glitch_lord_intro()\n"
                "boss.glitch.prebattle_01\n",
                encoding="utf-8",
            )

            _, changes = validate_development_files(fake_root)

            self.assertEqual(changes, ["まおうまえに おはなしが はじまる"])
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_preview_ignores_manual_preview_meta_json(self):
        """development_meta.json があっても入力としては信用せず差分から決める"""
        fake_root = ROOT / ".build" / "test_stale_meta"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            (fake_root / "main.py").write_text(
                "def _build_zone_enemies(enemies):\n    return []\n",
                encoding="utf-8",
            )
            (fake_root / "main_development.py").write_text(
                "def _build_zone_enemies(enemies):\n"
                "    if e.get(\"is_noise_guardian\"):\n"
                "        return []\n",
                encoding="utf-8",
            )
            (fake_root / "development_meta.json").write_text(
                json.dumps({"changes": ["ふるい せつめい"]}),
                encoding="utf-8",
            )

            _, changes = validate_development_files(fake_root)
            self.assertEqual(changes, ["つうしんとうの ノイズガーディアンが フィールドに でない"])
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)

    def test_preview_rejects_identical_main_and_preview(self):
        """preview 差分がないならおためし版は作らない"""
        fake_root = ROOT / ".build" / "test_no_meta"
        fake_root.mkdir(parents=True, exist_ok=True)
        try:
            content = "print('same')\n"
            (fake_root / "main.py").write_text(content, encoding="utf-8")
            (fake_root / "main_development.py").write_text(content, encoding="utf-8")

            with self.assertRaises(ValueError):
                validate_development_files(fake_root)
        finally:
            shutil.rmtree(fake_root, ignore_errors=True)


class TestResolvePyxelCommand(unittest.TestCase):
    def test_resolve_pyxel_command_prefers_python_module_even_if_find_spec_breaks(self):
        fake_root = ROOT / ".build" / "test_resolve_pyxel_command_python_module"
        fake_root.mkdir(parents=True, exist_ok=True)
        completed = subprocess.CompletedProcess(
            args=[sys.executable, "-c", "import pyxel"],
            returncode=0,
        )
        with (
            patch("tools.build_web_release.importlib.util.find_spec", side_effect=ValueError("pyxel.__spec__ is None")),
            patch("tools.build_web_release.subprocess.run", return_value=completed) as run_mock,
        ):
            self.assertEqual(resolve_pyxel_command(fake_root), [sys.executable, "-m", "pyxel"])
        run_mock.assert_called_once()

    def test_resolve_pyxel_command_handles_pyxel_module_without_spec(self):
        fake_root = ROOT / ".build" / "test_resolve_pyxel_command"
        fake_root.mkdir(parents=True, exist_ok=True)
        with (
            patch("tools.build_web_release.importlib.util.find_spec", side_effect=ValueError("pyxel.__spec__ is None")),
            patch(
                "tools.build_web_release.subprocess.run",
                return_value=subprocess.CompletedProcess(
                    args=[sys.executable, "-c", "import pyxel"],
                    returncode=1,
                ),
            ),
            patch("tools.build_web_release.shutil.which", return_value="/usr/bin/pyxel"),
        ):
            self.assertEqual(resolve_pyxel_command(fake_root), ["/usr/bin/pyxel"])


class TestPromote(unittest.TestCase):
    """preview 採否の内部ヘルパを検証する"""

    def setUp(self):
        self.work_dir = ROOT / ".build" / "test_promote"
        self.work_dir.mkdir(parents=True, exist_ok=True)
        # main.py を作成
        (self.work_dir / "main.py").write_text("# original", encoding="utf-8")
        # main_development.py を作成
        (self.work_dir / "main_development.py").write_text("# preview", encoding="utf-8")
        # development_meta.json を作成
        (self.work_dir / "development_meta.json").write_text(
            json.dumps({"changes": ["test"]}), encoding="utf-8"
        )

    def tearDown(self):
        shutil.rmtree(self.work_dir, ignore_errors=True)

    def test_promote_preview_replaces_main(self):
        promote(self.work_dir, choice="development")
        main_content = (self.work_dir / "main.py").read_text(encoding="utf-8")
        self.assertEqual(main_content, "# preview")
        self.assertFalse((self.work_dir / "main_development.py").exists())
        self.assertFalse((self.work_dir / "development_meta.json").exists())

    def test_promote_current_removes_preview(self):
        promote(self.work_dir, choice="production")
        main_content = (self.work_dir / "main.py").read_text(encoding="utf-8")
        self.assertEqual(main_content, "# original")
        self.assertFalse((self.work_dir / "main_development.py").exists())
        self.assertFalse((self.work_dir / "development_meta.json").exists())


class TestCliDispatch(unittest.TestCase):
    def test_preview_flag_dispatches_preview_build(self):
        with (
            patch.object(sys, "argv", ["build_web_release.py", "--development"]),
            patch("tools.build_web_release.build_development_release", return_value=("a", "b", "c")) as preview_build,
            patch("builtins.print") as print_mock,
        ):
            build_web_release_main()

        preview_build.assert_called_once_with(ROOT)
        print_mock.assert_called_once()

    def test_approve_development_flag_dispatches_approve(self):
        with (
            patch.object(sys, "argv", ["build_web_release.py", "--approve-development"]),
            patch("tools.build_web_release.approve_development") as approve,
            patch("builtins.print") as print_mock,
        ):
            build_web_release_main()

        approve.assert_called_once_with(ROOT)
        print_mock.assert_called_once_with("開発版を承認し、本番を再ビルドしました。")

    def test_reject_development_flag_dispatches_reject(self):
        with (
            patch.object(sys, "argv", ["build_web_release.py", "--reject-development"]),
            patch("tools.build_web_release.reject_development") as reject,
            patch("builtins.print") as print_mock,
        ):
            build_web_release_main()

        reject.assert_called_once_with(ROOT)
        print_mock.assert_called_once_with("開発版を却下し、本番を再ビルドしました。")

    def test_no_flag_dispatches_normal_build(self):
        with (
            patch.object(sys, "argv", ["build_web_release.py"]),
            patch("tools.build_web_release.build_web_release") as normal_build,
        ):
            build_web_release_main()

        normal_build.assert_called_once_with(ROOT)


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


class TestNormalBuildWithoutPreviewSource(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_normal_build_no_preview_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_normal_build_prunes_stale_preview_outputs(self):
        development_dir(self.output_dir).mkdir(parents=True, exist_ok=True)
        (development_dir(self.output_dir) / "play.html").write_text("stale preview wrapper", encoding="utf-8")
        (development_dir(self.output_dir) / "index.html").write_text("stale preview wrapper", encoding="utf-8")
        (development_dir(self.output_dir) / "pyxel.html").write_text("stale preview build", encoding="utf-8")
        (development_dir(self.output_dir) / "pyxel.pyxapp").write_text("stale preview app", encoding="utf-8")
        (development_dir(self.output_dir) / "code-maker.zip").write_text("stale preview zip", encoding="utf-8")

        build_web_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertFalse((development_dir(self.output_dir) / "play.html").exists())
        self.assertFalse((development_dir(self.output_dir) / "pyxel.html").exists())
        self.assertFalse((development_dir(self.output_dir) / "code-maker.zip").exists())
        self.assertNotIn("development/play.html", index_content)
        self.assertNotIn("開発版", index_content)
        self.assertIn('href="production/play.html?v=', index_content)
        self.assertTrue((production_dir(self.output_dir) / "code-maker.zip").exists())

        play_content = (production_dir(self.output_dir) / "play.html").read_text(encoding="utf-8")
        self.assertIn('src="pyxel.html?v=', play_content)

        with zipfile.ZipFile(production_dir(self.output_dir) / "code-maker.zip") as zf:
            current_main = zf.read("block-quest/main.py").decode("utf-8")
        self.assertEqual(
            current_main,
            build_codemaker_main_text(
                (self.project_root / "main.py").read_text(encoding="utf-8")
            ),
        )


class TestNormalBuildWithStalePreviewMeta(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_normal_build_stale_preview_meta_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root, include_preview=True)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_normal_build_hides_preview_when_preview_meta_hashes_do_not_match_sources(self):
        (self.project_root / "development_meta.json").write_text(
            json.dumps(
                {
                    "base_production_hash": "stale-main",
                    "development_hash": "stale-development",
                    "changes": ["ふるい せつめい"],
                }
            ),
            encoding="utf-8",
        )
        (self.output_dir / "play-development.html").write_text("stale preview wrapper", encoding="utf-8")
        (self.output_dir / "pyxel-development.html").write_text("stale preview build", encoding="utf-8")
        os.utime((self.output_dir / "play-development.html"), None)
        os.utime((self.output_dir / "pyxel-development.html"), None)

        build_web_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertFalse((self.output_dir / "play-development.html").exists())
        self.assertFalse((self.output_dir / "pyxel-development.html").exists())
        self.assertNotIn("ふるい せつめい", index_content)
        self.assertNotIn("開発版", index_content)


class TestPreviewBuildUsesVersionedLinks(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_preview_versioned_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root, include_preview=True)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_preview_build_versions_selector_and_wrapper_urls(self):
        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        play_content = (production_dir(self.output_dir) / "play.html").read_text(encoding="utf-8")
        play_preview_content = (development_dir(self.output_dir) / "play.html").read_text(encoding="utf-8")

        self.assertIn('href="production/play.html?v=', index_content)
        self.assertIn('href="development/play.html?v=', index_content)
        self.assertIn('href="development/code-maker.zip?v=', index_content)
        self.assertIn('href="https://kitao.github.io/pyxel/wasm/code-maker/"', index_content)
        self.assertIn("まおうまえに おはなしが はじまる", index_content)
        self.assertIn('src="pyxel.html?v=', play_content)
        self.assertIn('src="pyxel.html?v=', play_preview_content)
        self.assertTrue((production_dir(self.output_dir) / "code-maker.zip").exists())
        self.assertTrue((development_dir(self.output_dir) / "code-maker.zip").exists())
        self.assertTrue((production_dir(self.output_dir) / "index.html").exists())
        self.assertTrue((development_dir(self.output_dir) / "index.html").exists())
        meta = json.loads((self.project_root / "development_meta.json").read_text(encoding="utf-8"))
        self.assertEqual(meta["changes"], ["まおうまえに おはなしが はじまる"])

        with zipfile.ZipFile(production_dir(self.output_dir) / "code-maker.zip") as zf:
            current_main = zf.read("block-quest/main.py").decode("utf-8")
        with zipfile.ZipFile(development_dir(self.output_dir) / "code-maker.zip") as zf:
            preview_main = zf.read("block-quest/main.py").decode("utf-8")
        self.assertEqual(
            current_main,
            build_codemaker_main_text(
                (self.project_root / "main.py").read_text(encoding="utf-8")
            ),
        )
        self.assertEqual(
            preview_main,
            build_codemaker_main_text(
                (self.project_root / "main_development.py").read_text(encoding="utf-8")
            ),
        )

    def test_normal_build_outputs_production_files_under_subdir(self):
        build_web_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        self.assertTrue((self.output_dir / "index.html").exists())
        self.assertTrue((production_dir(self.output_dir) / "index.html").exists())
        self.assertTrue((production_dir(self.output_dir) / "play.html").exists())
        self.assertTrue((production_dir(self.output_dir) / "pyxel.html").exists())
        self.assertTrue((production_dir(self.output_dir) / "pyxel.pyxapp").exists())
        self.assertTrue((production_dir(self.output_dir) / "code-maker.zip").exists())

    def test_preview_build_busts_preview_zip_url_when_codemaker_builder_changes(self):
        tools_dir = self.project_root / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "tools" / "build_codemaker.py", tools_dir / "build_codemaker.py")

        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)
        first_index = (self.output_dir / "index.html").read_text(encoding="utf-8")
        first_token = re.search(r'href="development/code-maker\.zip\?v=([^"]+)"', first_index)
        self.assertIsNotNone(first_token)

        builder_path = tools_dir / "build_codemaker.py"
        newer_mtime = (development_dir(self.output_dir) / "code-maker.zip").stat().st_mtime + 10
        os.utime(builder_path, (newer_mtime, newer_mtime))

        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)
        second_index = (self.output_dir / "index.html").read_text(encoding="utf-8")
        second_token = re.search(r'href="development/code-maker\.zip\?v=([^"]+)"', second_index)
        self.assertIsNotNone(second_token)
        self.assertNotEqual(first_token.group(1), second_token.group(1))


class TestResourceOnlyDevelopmentBuild(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_resource_only_development_build_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_resource_only_import_builds_development_candidate_without_preview_code(self):
        import io

        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as zf:
            zf.writestr("block-quest/main.py", "print('ignored code')\n")
            zf.writestr("block-quest/my_resource.pyxres", b"resource-only-preview")
        import_codemaker_resource_zip(
            self.project_root,
            payload.getvalue(),
            source_name="code-maker.zip",
        )

        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        meta = json.loads((self.project_root / "development_meta.json").read_text(encoding="utf-8"))

        self.assertIn("開発版", index_content)
        self.assertIn("Code Maker の resource を とりこんだ", index_content)
        self.assertTrue(meta["uses_imported_resource"])
        self.assertFalse(meta["uses_preview_code"])
        self.assertTrue((development_dir(self.output_dir) / "play.html").exists())
        self.assertTrue((development_dir(self.output_dir) / "pyxel.html").exists())
        self.assertTrue((development_dir(self.output_dir) / "code-maker.zip").exists())

        with zipfile.ZipFile(production_dir(self.output_dir) / "code-maker.zip") as zf:
            production_resource = zf.read("block-quest/my_resource.pyxres")
            production_main = zf.read("block-quest/main.py").decode("utf-8")
        with zipfile.ZipFile(development_dir(self.output_dir) / "code-maker.zip") as zf:
            development_resource = zf.read("block-quest/my_resource.pyxres")
            development_main = zf.read("block-quest/main.py").decode("utf-8")

        self.assertEqual(
            production_main,
            build_codemaker_main_text(
                (self.project_root / "main.py").read_text(encoding="utf-8")
            ),
        )
        self.assertEqual(
            development_main,
            build_codemaker_main_text(
                (self.project_root / "main.py").read_text(encoding="utf-8")
            ),
        )
        self.assertEqual(
            production_resource,
            (self.project_root / "assets" / "blockquest.pyxres").read_bytes(),
        )
        self.assertEqual(development_resource, b"resource-only-preview")


class TestPreviewBuildMetadata(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_preview_request_note_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root, include_preview=True)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_preview_meta_records_hashes_for_current_candidate_only(self):
        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        meta = json.loads((self.project_root / "development_meta.json").read_text(encoding="utf-8"))
        self.assertTrue(meta["base_production_hash"])
        self.assertTrue(meta["development_hash"])
        self.assertNotIn("request_note_path", meta)
        self.assertNotIn("request_note_hash", meta)


class TestPreviewBuildDoesNotRollForwardAutomatically(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_preview_no_roll_forward_root"
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.original_main = "dungeon.glitch.exit callback=_enter_ending\n"
        self.new_preview = "dungeon.glitch.exit callback=None\nis_noise_guardian\n"
        (self.project_root / "main.py").write_text(self.original_main, encoding="utf-8")
        (self.project_root / "main_development.py").write_text(self.new_preview, encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_build_development_release_leaves_current_unchanged_until_approved(self):
        _, changes = validate_development_files(self.project_root)

        self.assertEqual(
            (self.project_root / "main.py").read_text(encoding="utf-8"),
            self.original_main,
        )
        self.assertEqual(
            changes,
            [
                "つうしんとうの ノイズガーディアンが フィールドに でない",
                "まおうを たおしたあとも つづきに すすめる",
            ],
        )


class TestNormalBuildWithStalePreviewArtifacts(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_normal_build_stale_preview_artifact_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root, include_preview=True)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_normal_build_hides_preview_when_preview_meta_hashes_do_not_match(self):
        (self.output_dir / "play-development.html").write_text("preview wrapper", encoding="utf-8")
        (self.output_dir / "pyxel-development.html").write_text("preview build", encoding="utf-8")
        (self.output_dir / "code-maker-development.zip").write_text("preview zip", encoding="utf-8")
        os.utime((self.output_dir / "play-development.html"), None)
        os.utime((self.output_dir / "pyxel-development.html"), None)
        os.utime((self.output_dir / "code-maker-development.zip"), None)
        (self.project_root / "development_meta.json").write_text(
            json.dumps(
                {
                    "base_production_hash": "stale-main",
                    "development_hash": "stale-development",
                    "changes": ["ふるい せつめい"],
                }
            ),
            encoding="utf-8",
        )

        build_web_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertFalse((self.output_dir / "play-development.html").exists())
        self.assertFalse((self.output_dir / "pyxel-development.html").exists())
        self.assertFalse((self.output_dir / "code-maker-development.zip").exists())
        self.assertNotIn("ふるい せつめい", index_content)
        self.assertNotIn("開発版", index_content)


class TestNormalBuildWithMatchingPreviewArtifacts(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_normal_build_matching_preview_artifact_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root, include_preview=True)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_normal_build_keeps_preview_when_hashes_match(self):
        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)
        build_web_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("開発版", index_content)
        self.assertIn("まおうまえに おはなしが はじまる", index_content)
        self.assertIn("development/code-maker.zip", index_content)
        self.assertIn("https://kitao.github.io/pyxel/wasm/code-maker/", index_content)
        self.assertTrue((development_dir(self.output_dir) / "play.html").exists())
        self.assertTrue((development_dir(self.output_dir) / "pyxel.html").exists())
        self.assertTrue((development_dir(self.output_dir) / "code-maker.zip").exists())

    def test_normal_build_hides_preview_codemaker_links_when_builder_is_newer_than_preview_zip(self):
        tools_dir = self.project_root / "tools"
        tools_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "tools" / "build_codemaker.py", tools_dir / "build_codemaker.py")

        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)
        builder_path = tools_dir / "build_codemaker.py"
        newer_mtime = (development_dir(self.output_dir) / "code-maker.zip").stat().st_mtime + 10
        os.utime(builder_path, (newer_mtime, newer_mtime))

        build_web_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertIn("開発版", index_content)
        self.assertIn("development/play.html", index_content)
        self.assertNotIn("development/code-maker.zip", index_content)
        self.assertNotIn("https://kitao.github.io/pyxel/wasm/code-maker/", index_content)


class TestExplicitPreviewCommands(unittest.TestCase):
    def setUp(self):
        self.project_root = ROOT / ".build" / "test_explicit_preview_commands_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root, include_preview=True)
        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_approve_development_promotes_candidate_then_rebuilds_current(self):
        approve_development(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        self.assertFalse((self.project_root / "main_development.py").exists())
        self.assertFalse((self.project_root / "development_meta.json").exists())
        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("開発版", index_content)

    def test_reject_development_discards_candidate_then_rebuilds_current(self):
        original_main = (self.project_root / "main.py").read_text(encoding="utf-8")

        reject_development(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        self.assertEqual(
            (self.project_root / "main.py").read_text(encoding="utf-8"),
            original_main,
        )
        self.assertFalse((self.project_root / "main_development.py").exists())
        self.assertFalse((self.project_root / "development_meta.json").exists())


class TestExplicitResourceOnlyPreviewCommands(unittest.TestCase):
    def setUp(self):
        import io

        self.project_root = ROOT / ".build" / "test_explicit_resource_only_preview_commands_root"
        self.output_dir = self.project_root / "out"
        self.work_dir = self.project_root / "work"
        self.project_root.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        copy_web_release_fixture(self.project_root)
        self.original_resource = (self.project_root / "assets" / "blockquest.pyxres").read_bytes()

        payload = io.BytesIO()
        with zipfile.ZipFile(payload, "w") as zf:
            zf.writestr("block-quest/main.py", "print('ignored code')\n")
            zf.writestr("block-quest/my_resource.pyxres", b"approved-resource")
        import_codemaker_resource_zip(
            self.project_root,
            payload.getvalue(),
            source_name="code-maker.zip",
        )
        build_development_release(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

    def tearDown(self):
        shutil.rmtree(self.project_root, ignore_errors=True)

    def test_approve_development_promotes_imported_resource_then_rebuilds_current(self):
        approve_development(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        self.assertEqual(
            (self.project_root / "assets" / "blockquest.pyxres").read_bytes(),
            b"approved-resource",
        )
        self.assertFalse((self.project_root / ".runtime" / "codemaker_resource_imports" / "development.json").exists())
        self.assertFalse((self.project_root / "development_meta.json").exists())
        self.assertFalse((development_dir(self.output_dir) / "play.html").exists())
        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("開発版", index_content)

    def test_reject_development_discards_imported_resource_then_rebuilds_current(self):
        reject_development(self.project_root, output_dir=self.output_dir, work_dir=self.work_dir)

        self.assertEqual(
            (self.project_root / "assets" / "blockquest.pyxres").read_bytes(),
            self.original_resource,
        )
        self.assertFalse((self.project_root / ".runtime" / "codemaker_resource_imports" / "development.json").exists())
        self.assertFalse((self.project_root / "development_meta.json").exists())
        self.assertFalse((development_dir(self.output_dir) / "play.html").exists())
        index_content = (self.output_dir / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("開発版", index_content)


if __name__ == "__main__":
    unittest.main()
