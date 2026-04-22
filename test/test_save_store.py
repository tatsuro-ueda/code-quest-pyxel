from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

PYXEL_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PYXEL_ROOT))

from src.shared.services.save_store import (
    FileSaveStore,
    InMemorySaveStore,
    SaveStoreError,
    make_save_store,
)


SAMPLE_DATA = {
    "save_version": 1,
    "town_pos": [20, 12],
    "player": {"x": 20, "y": 12, "hp": 25, "gold": 50},
}


class InMemorySaveStoreTest(unittest.TestCase):
    def test_starts_empty(self):
        store = InMemorySaveStore()
        self.assertFalse(store.exists())
        self.assertIsNone(store.load())

    def test_save_then_load(self):
        store = InMemorySaveStore()
        store.save(SAMPLE_DATA)
        self.assertTrue(store.exists())
        self.assertEqual(store.load(), SAMPLE_DATA)

    def test_overwrite(self):
        store = InMemorySaveStore()
        store.save({"save_version": 1, "town_pos": [0, 0], "player": {}})
        store.save(SAMPLE_DATA)
        self.assertEqual(store.load(), SAMPLE_DATA)


class FileSaveStoreTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "save.json"
        self.store = FileSaveStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_does_not_exist_initially(self):
        self.assertFalse(self.store.exists())
        self.assertIsNone(self.store.load())

    def test_save_creates_file(self):
        self.store.save(SAMPLE_DATA)
        self.assertTrue(self.path.exists())
        self.assertEqual(json.loads(self.path.read_text("utf-8")), SAMPLE_DATA)

    def test_load_after_save(self):
        self.store.save(SAMPLE_DATA)
        self.assertEqual(self.store.load(), SAMPLE_DATA)

    def test_atomic_temp_file_removed(self):
        self.store.save(SAMPLE_DATA)
        leftover = list(self.path.parent.glob("*.tmp*"))
        self.assertEqual(leftover, [])

    def test_corrupt_json_returns_none(self):
        self.path.write_text("not valid json {{{", "utf-8")
        self.assertIsNone(self.store.load())

    def test_unknown_save_version_returns_none(self):
        self.path.write_text(
            json.dumps({"save_version": 999, "town_pos": [0, 0], "player": {}}),
            "utf-8",
        )
        self.assertIsNone(self.store.load())

    def test_save_failure_raises_save_store_error(self):
        bogus = FileSaveStore(Path(self.tmp.name) / "no_such_dir" / "save.json")
        with self.assertRaises(SaveStoreError):
            bogus.save(SAMPLE_DATA)


class FactoryTest(unittest.TestCase):
    def test_returns_file_save_store_on_desktop(self):
        with tempfile.TemporaryDirectory() as d:
            store = make_save_store(Path(d) / "save.json")
            self.assertIsInstance(store, FileSaveStore)


if __name__ == "__main__":
    unittest.main()
