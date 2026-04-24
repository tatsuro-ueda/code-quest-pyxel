"""CJG/codemaker: zip から pyxres を抽出する関数の挙動。

根拠:
- docs/customer-journeys.md CJ23/CJ24（Code Maker で編集→取り込み）
- docs/product-requirements-platform.md（取り込み経路のエラー）

_resolve_resource_entry は my_resource.pyxres を一意に特定する。
複数あればエラー、無ければエラー、`block-quest/my_resource.pyxres` を優先。
extract_codemaker_resource_archive は zip バイト列を受け取り、pyxres バイトと
同封されていたコードエントリ名のリストを返す。
"""

from __future__ import annotations

import io
import sys
import unittest
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.codemaker_resource_store import (
    extract_codemaker_resource_archive,
    _resolve_resource_entry,
)


def _make_zip(entries: dict[str, bytes]) -> bytes:
    buf = io.BytesIO()
    with ZipFile(buf, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    return buf.getvalue()


class ResolveResourceEntryTest(unittest.TestCase):
    def test_prefers_block_quest_prefixed_path(self):
        entries = ["block-quest/my_resource.pyxres", "other/my_resource.pyxres"]

        result = _resolve_resource_entry(entries)

        self.assertEqual(result, "block-quest/my_resource.pyxres")

    def test_accepts_bare_path_when_unique(self):
        entries = ["subfolder/my_resource.pyxres"]

        result = _resolve_resource_entry(entries)

        self.assertEqual(result, "subfolder/my_resource.pyxres")

    def test_raises_when_resource_missing(self):
        entries = ["block-quest/main.py"]

        with self.assertRaises(ValueError) as cm:
            _resolve_resource_entry(entries)

        self.assertIn("my_resource.pyxres", str(cm.exception))

    def test_raises_when_multiple_candidates(self):
        entries = [
            "first/my_resource.pyxres",
            "second/my_resource.pyxres",
        ]

        with self.assertRaises(ValueError):
            _resolve_resource_entry(entries)


class ExtractCodemakerResourceArchiveTest(unittest.TestCase):
    def test_extracts_pyxres_bytes(self):
        data = _make_zip({
            "block-quest/my_resource.pyxres": b"pyxres-data",
            "block-quest/main.py": b"print('ignored')",
        })

        pyxres_bytes, ignored = extract_codemaker_resource_archive(data)

        self.assertEqual(pyxres_bytes, b"pyxres-data")
        self.assertIn("block-quest/main.py", ignored)

    def test_bad_zip_raises_value_error(self):
        with self.assertRaises(ValueError):
            extract_codemaker_resource_archive(b"not a zip")

    def test_zip_without_pyxres_raises(self):
        data = _make_zip({
            "block-quest/main.py": b"just code",
        })

        with self.assertRaises(ValueError):
            extract_codemaker_resource_archive(data)


if __name__ == "__main__":
    unittest.main()
