from __future__ import annotations

"""``resolve_pyxres_path`` のユニットテスト。

過去バグ（2026-04-25）：Pyxel Code Maker は ``block-quest/main.py`` と
``block-quest/my_resource.pyxres`` を同一ディレクトリに置くが、
従来の探索ロジックは ``M.__file__.parent.parent.parent`` から始めていたため
bundle 環境では ``block-quest/`` の 3 つ上を見て、bundle 内の pyxres を
完全に無視していた。結果として ``paint_tile_bank()`` の組み込みデフォルトが
描画され「古いマップ」が表示されていた。
"""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.image_banks import resolve_pyxres_path  # noqa: E402


class ResolvePyxresPathTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        # 関数は m_file.parent.parent.parent を project_root と見なす。
        # tempdir 自体（/tmp/tmpXXX）を project_root にすると周囲の /tmp の
        # ファイルが影響するので、tempdir 内にもう 1 つネストさせて
        # 外部ノイズを完全に遮断する。
        self.root = Path(self.tmp.name) / "isolated_root"
        self.root.mkdir()

    def tearDown(self):
        self.tmp.cleanup()

    # -------- bundle layout（過去バグの本丸） --------

    def test_bundle_layout_finds_pyxres_next_to_main(self):
        """Code Maker bundle では block-quest/main.py の隣の
        my_resource.pyxres が最優先で選ばれる。
        """
        bundle_dir = self.root / "block-quest"
        bundle_dir.mkdir()
        main_py = bundle_dir / "main.py"
        main_py.write_text("# bundle main", encoding="utf-8")
        bundle_pyxres = bundle_dir / "my_resource.pyxres"
        bundle_pyxres.write_bytes(b"bundle-pyxres")

        result = resolve_pyxres_path(main_py)
        self.assertEqual(result, bundle_pyxres.resolve())

    def test_bundle_layout_without_pyxres_falls_through(self):
        """bundle dir に pyxres がない場合は project_root 候補に進む。
        どちらも無ければ最後（assets パス）を返す。
        """
        bundle_dir = self.root / "block-quest"
        bundle_dir.mkdir()
        main_py = bundle_dir / "main.py"
        main_py.write_text("# bundle main", encoding="utf-8")

        result = resolve_pyxres_path(main_py)
        # 最後のフォールバックは assets パス（存在しなくても返る）
        self.assertEqual(
            result,
            (main_py.resolve().parent.parent.parent / "assets" / "blockquest.pyxres"),
        )

    # -------- dev project layout --------

    def test_dev_layout_uses_assets_blockquest_pyxres(self):
        """dev 環境では src/runtime/main_runtime.py から 2 階層上の
        assets/blockquest.pyxres が見つかる。
        """
        runtime_dir = self.root / "src" / "runtime"
        runtime_dir.mkdir(parents=True)
        main_runtime = runtime_dir / "main_runtime.py"
        main_runtime.write_text("# main_runtime", encoding="utf-8")
        assets_dir = self.root / "assets"
        assets_dir.mkdir()
        canonical_pyxres = assets_dir / "blockquest.pyxres"
        canonical_pyxres.write_bytes(b"canonical-pyxres")

        result = resolve_pyxres_path(main_runtime)
        self.assertEqual(result, canonical_pyxres.resolve())

    def test_dev_layout_prefers_project_root_override_over_assets(self):
        """project_root 直下の my_resource.pyxres は assets/blockquest.pyxres より
        優先される（手元で差し替え用）。"""
        runtime_dir = self.root / "src" / "runtime"
        runtime_dir.mkdir(parents=True)
        main_runtime = runtime_dir / "main_runtime.py"
        main_runtime.write_text("# main_runtime", encoding="utf-8")
        assets_dir = self.root / "assets"
        assets_dir.mkdir()
        (assets_dir / "blockquest.pyxres").write_bytes(b"canonical")
        override = self.root / "my_resource.pyxres"
        override.write_bytes(b"override")

        result = resolve_pyxres_path(main_runtime)
        self.assertEqual(result, override.resolve())

    # -------- precedence --------

    def test_bundle_pyxres_beats_project_root_override(self):
        """bundle dir の pyxres は project_root 直下の override より強い。"""
        bundle_dir = self.root / "block-quest"
        bundle_dir.mkdir()
        main_py = bundle_dir / "main.py"
        main_py.write_text("# bundle main", encoding="utf-8")
        bundle_pyxres = bundle_dir / "my_resource.pyxres"
        bundle_pyxres.write_bytes(b"bundle")
        # project_root（=bundle_dir.parent.parent.parent）に override を置いても
        # bundle_dir の pyxres が優先される。
        override_root = main_py.resolve().parent.parent.parent
        override_root.mkdir(parents=True, exist_ok=True)
        (override_root / "my_resource.pyxres").write_bytes(b"override")

        result = resolve_pyxres_path(main_py)
        self.assertEqual(result, bundle_pyxres.resolve())

    def test_string_path_input_is_accepted(self):
        bundle_dir = self.root / "block-quest"
        bundle_dir.mkdir()
        main_py = bundle_dir / "main.py"
        main_py.write_text("# bundle main", encoding="utf-8")
        bundle_pyxres = bundle_dir / "my_resource.pyxres"
        bundle_pyxres.write_bytes(b"bundle")

        result = resolve_pyxres_path(str(main_py))
        self.assertEqual(result, bundle_pyxres.resolve())


if __name__ == "__main__":
    unittest.main()
