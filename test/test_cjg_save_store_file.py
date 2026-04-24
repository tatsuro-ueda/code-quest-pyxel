"""CJG/save_store: FileSaveStore の実ファイル IO 挙動。

根拠:
- docs/product-requirements-platform.md（デスクトップ環境でのセーブ）

FileSaveStore は atomic save（tmp → rename）、壊れた JSON は load で None、
存在しないファイルも None、save_version 不正も None。
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.save_store import FileSaveStore


class FileSaveStoreRoundTripTest(unittest.TestCase):
    def test_save_and_load_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            store = FileSaveStore(path)
            data = {"save_version": 1, "player": {"hp": 10}, "town_pos": [25, 6]}

            store.save(data)

            self.assertTrue(store.exists())
            loaded = store.load()
            self.assertEqual(loaded, data)

    def test_load_nonexistent_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileSaveStore(Path(tmp) / "missing.json")

            self.assertIsNone(store.load())

    def test_load_corrupted_json_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            path.write_text("not a valid json", encoding="utf-8")
            store = FileSaveStore(path)

            self.assertIsNone(store.load())

    def test_load_unsupported_save_version_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            path.write_text(json.dumps({"save_version": 99}), encoding="utf-8")
            store = FileSaveStore(path)

            self.assertIsNone(store.load())

    def test_exists_returns_false_before_save(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileSaveStore(Path(tmp) / "save.json")

            self.assertFalse(store.exists())

    def test_save_overwrites_previous_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            store = FileSaveStore(path)

            store.save({"save_version": 1, "player": {"hp": 10}})
            store.save({"save_version": 1, "player": {"hp": 50}})

            loaded = store.load()
            self.assertEqual(loaded["player"]["hp"], 50)


class FileSaveStoreAtomicityTest(unittest.TestCase):
    def test_save_removes_tmp_file(self):
        """atomic save 後に .tmp が残らない。"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "save.json"
            store = FileSaveStore(path)

            store.save({"save_version": 1, "player": {}})

            tmp_path = path.with_suffix(path.suffix + ".tmp")
            self.assertFalse(tmp_path.exists())


if __name__ == "__main__":
    unittest.main()
