"""CJG/save_store: _validate_loaded + InMemorySaveStore の契約。

根拠:
- docs/product-requirements-platform.md（セーブ互換）

_validate_loaded は dict で save_version=1 のもののみ通す。壊れた JSON /
バージョン不正 / 非 dict は全て None を返す。
InMemorySaveStore は exists / load / save の往復が deep copy で隔離される。
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.save_store import (
    InMemorySaveStore,
    _validate_loaded,
)


class ValidateLoadedTest(unittest.TestCase):
    def test_valid_save_version_1_passes(self):
        data = {"save_version": 1, "player": {}, "town_pos": [0, 0]}
        self.assertIs(_validate_loaded(data), data)

    def test_missing_save_version_rejected(self):
        self.assertIsNone(_validate_loaded({"player": {}}))

    def test_future_save_version_rejected(self):
        self.assertIsNone(_validate_loaded({"save_version": 99, "player": {}}))

    def test_zero_save_version_rejected(self):
        self.assertIsNone(_validate_loaded({"save_version": 0}))

    def test_non_dict_inputs_rejected(self):
        self.assertIsNone(_validate_loaded(None))
        self.assertIsNone(_validate_loaded([]))
        self.assertIsNone(_validate_loaded("string"))
        self.assertIsNone(_validate_loaded(42))


class InMemorySaveStoreTest(unittest.TestCase):
    def test_new_store_has_no_data(self):
        store = InMemorySaveStore()
        self.assertFalse(store.exists())
        self.assertIsNone(store.load())

    def test_save_then_load_round_trip(self):
        store = InMemorySaveStore()
        data = {"save_version": 1, "player": {"hp": 10}, "town_pos": [25, 6]}

        store.save(data)

        self.assertTrue(store.exists())
        loaded = store.load()
        self.assertEqual(loaded, data)

    def test_load_returns_deep_copy_not_reference(self):
        """呼び出し側が返り値を書き換えても store 内部は変わらない。"""
        store = InMemorySaveStore()
        store.save({"save_version": 1, "player": {"hp": 10}, "town_pos": [0, 0]})

        loaded = store.load()
        loaded["player"]["hp"] = 9999

        # 再度 load しても 10 のまま
        reloaded = store.load()
        self.assertEqual(reloaded["player"]["hp"], 10)

    def test_save_copies_input_so_later_mutation_does_not_leak(self):
        """保存後に外部で dict を書き換えても store は影響を受けない。"""
        store = InMemorySaveStore()
        data = {"save_version": 1, "player": {"hp": 10}, "town_pos": [0, 0]}
        store.save(data)

        data["player"]["hp"] = 9999

        self.assertEqual(store.load()["player"]["hp"], 10)


if __name__ == "__main__":
    unittest.main()
