"""Tests for src/game_data loaders."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import game_data  # noqa: E402


class LoadYamlTest(unittest.TestCase):
    def test_load_yaml_returns_dict_or_list(self):
        result = game_data.load_yaml(ROOT / "assets" / "dialogue.yaml")
        self.assertTrue(isinstance(result, (dict, list)))


if __name__ == "__main__":
    unittest.main()
