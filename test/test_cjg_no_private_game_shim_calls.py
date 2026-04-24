"""CJG/guardrail: scene や shared 配下が Game の private shim (`game._xxx()`) を呼ばない。

根拠:
- steering/done/20260425-menu-shim-crash-fix.md（Game にない `game._open_settings`
  を menu が呼んで実機 crash した回帰）
- docs/framework-rule.md M4-4（Scene は Game を薄い配線として使い、private shim
  を勝手に呼ばない）

対策として、src/scenes/**/*.py と src/shared/**/*.py に `game._<name>(` の
呼び出しが 0 件であることを静的に保証する。Game の private メソッド（`_*`）は
Game 自身だけが使える前提で、scene 側から呼ぶのは許可しない。
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


_PRIVATE_SHIM_RE = re.compile(r"\bgame\._[a-z][a-z0-9_]*\(")


def _iter_py_files(base: Path):
    for path in base.rglob("*.py"):
        if path.name == "__init__.py":
            continue
        yield path


class NoPrivateGameShimInScenesTest(unittest.TestCase):
    """src/scenes/ 配下に `game._xxx(` 呼び出しが 0 件。"""

    def test_no_private_shim_calls_in_any_scene_py(self):
        violations: list[str] = []
        for path in _iter_py_files(ROOT / "src" / "scenes"):
            text = path.read_text(encoding="utf-8")
            for match in _PRIVATE_SHIM_RE.finditer(text):
                violations.append(f"{path.relative_to(ROOT)}: {match.group(0)}")

        self.assertEqual(
            violations,
            [],
            "Game の private shim `game._xxx(` を scenes から呼んでいる\n"
            "（Game に実体が無いと AttributeError で実機 crash する）:\n"
            + "\n".join(violations),
        )


class NoPrivateGameShimInSharedTest(unittest.TestCase):
    """src/shared/ 配下に `game._xxx(` 呼び出しが 0 件。"""

    def test_no_private_shim_calls_in_any_shared_py(self):
        violations: list[str] = []
        for path in _iter_py_files(ROOT / "src" / "shared"):
            text = path.read_text(encoding="utf-8")
            for match in _PRIVATE_SHIM_RE.finditer(text):
                violations.append(f"{path.relative_to(ROOT)}: {match.group(0)}")

        self.assertEqual(
            violations,
            [],
            "Game の private shim を shared サービスから呼んでいる:\n"
            + "\n".join(violations),
        )


if __name__ == "__main__":
    unittest.main()
