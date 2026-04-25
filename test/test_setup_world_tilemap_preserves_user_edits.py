from __future__ import annotations

"""``ImageBanks.setup_world_tilemap`` がユーザーの tilemap 編集を破棄しないことを保証する。

過去バグ（2026-04-25）：``tile_bank_layout_valid()`` が False の時、
``setup_world_tilemap`` は image bank を再描画したうえで
``bake_world_to_tilemap()`` を ``derive_world_from_tilemap()`` 抜きで呼び、
tilemap を **手続き的に再生成された ``game.world_map`` で上書き**していた。
その結果、Pyxel Code Maker でユーザーが pyxres の tilemap を編集（道の修整等）しても、
ゲーム実行時に tilemap が procedural 版で焼き戻されて編集が消えていた。

修正後の不変性：``pyxres_loaded`` が True のすべての分岐で
``derive_world_from_tilemap()`` が呼ばれること（pyxres の tilemap が
SoT として尊重されること）。
"""

import ast
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def _function_node(source: str, name: str) -> ast.FunctionDef:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise AssertionError(f"function {name!r} not found")


def _calls_in(node: ast.AST) -> set[str]:
    """node 配下で呼ばれている self.<method> 名の集合。"""
    out: set[str] = set()
    for child in ast.walk(node):
        if (
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Attribute)
            and isinstance(child.func.value, ast.Name)
            and child.func.value.id == "self"
        ):
            out.add(child.func.attr)
    return out


def _branch_bodies(if_node: ast.If) -> list[list[ast.stmt]]:
    """if/elif/else の各分岐の body を順に返す（ネストした if も再帰展開）。"""
    bodies: list[list[ast.stmt]] = [if_node.body]
    orelse = if_node.orelse
    while orelse and len(orelse) == 1 and isinstance(orelse[0], ast.If):
        bodies.append(orelse[0].body)
        orelse = orelse[0].orelse
    if orelse:
        bodies.append(orelse)
    return bodies


class SetupWorldTilemapStructureTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = ROOT / "src" / "shared" / "services" / "image_banks.py"
        cls.source = path.read_text(encoding="utf-8")
        cls.func = _function_node(cls.source, "setup_world_tilemap")

    def test_pyxres_loaded_branch_always_derives_world_from_tilemap(self):
        """``self.pyxres_loaded`` が True の分岐に入った時、tile bank 状態に
        かかわらず ``derive_world_from_tilemap`` が呼ばれること。

        過去バグでは ``tile_bank_layout_valid()`` が False のサブ分岐で
        derive をスキップして procedural bake のみ呼んでいた。本テストは
        if 本体配下のすべての statement から derive 呼び出しが見つかれば
        OK とする（途中のサブ if のどちら側に居ても外側で必ず通るため）。
        """
        for if_node in ast.walk(self.func):
            if not isinstance(if_node, ast.If):
                continue
            test = if_node.test
            if not (
                isinstance(test, ast.Attribute)
                and isinstance(test.value, ast.Name)
                and test.value.id == "self"
                and test.attr == "pyxres_loaded"
            ):
                continue
            outer_body_calls: set[str] = set()
            for stmt in if_node.body:
                outer_body_calls |= _calls_in(stmt)
            self.assertIn(
                "derive_world_from_tilemap",
                outer_body_calls,
                f"pyxres_loaded body lacks derive_world_from_tilemap; calls={sorted(outer_body_calls)}",
            )
            return

        self.fail("`if self.pyxres_loaded:` branch not found in setup_world_tilemap")

    def test_paint_tile_bank_no_longer_paired_with_procedural_bake(self):
        """過去バグ：image bank repaint と一緒に procedural bake_world をしていた。
        その組み合わせ（``paint_tile_bank`` を呼ぶ分岐で ``derive_world_from_tilemap`` を
        呼ばない）が再混入していないことを確認する。
        """
        for branch in ast.walk(self.func):
            if not isinstance(branch, ast.If):
                continue
            for body in _branch_bodies(branch):
                flat_calls: set[str] = set()
                for stmt in body:
                    flat_calls |= _calls_in(stmt)
                if "paint_tile_bank" in flat_calls and "bake_world_to_tilemap" in flat_calls:
                    self.assertIn(
                        "derive_world_from_tilemap",
                        flat_calls,
                        f"branch repaints image bank and bakes world without "
                        f"derive_world_from_tilemap (regression); calls={sorted(flat_calls)}",
                    )


if __name__ == "__main__":
    unittest.main()
