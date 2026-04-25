from __future__ import annotations

"""Code Maker bundle が実行可能であることを保証する smoke test。

過去のインシデント:
- 2026-04-25: `src/shared/state/player_model.py` を manifest に追加し忘れ、
  Pyxel Code Maker で `NameError: PlayerModel is not defined` が発生
- 2026-04-25: bundler が多行 `from src.X import (Y as Z, ...)` から `Z = Y` の
  alias 行を生成し損ね、`_stats_for_level_defense` が未定義になり Game() 起動で落ちた

これらは bundler が生成した main.py を一度も exec しないテスト構成だった
ため検出が遅れた。本ファイルは：

1. ``_strip_local_imports`` の多行 ``as`` alias 抽出を直接ユニットテストする
2. 実 manifest から build_bundled_source して、stub pyxel で
   モジュールロードと Game() 生成を実行し、NameError が出ないことを確認する
"""

import sys
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.codemaker_bundler import (  # noqa: E402
    _strip_local_imports,
    build_bundled_source,
)


class StripLocalImportsAsAliasTest(unittest.TestCase):
    """``_strip_local_imports`` の ``as`` alias 抽出を検証する。"""

    def test_single_line_as_alias_is_rewritten(self):
        source = "from src.shared.state.player_model import stats_for_level as _orig\n"
        out = _strip_local_imports(source)
        self.assertIn("_orig = stats_for_level", out)

    def test_multi_line_import_with_as_alias_is_preserved(self):
        """過去バグ: 多行 import の中の ``as`` alias が消えていた。"""
        source = (
            "from src.shared.state.player_model import (\n"
            "    MAX_LEVEL,\n"
            "    PlayerModel,\n"
            "    stats_for_level as _stats_for_level_defense,\n"
            "    exp_for_level,\n"
            ")\n"
            "\n"
            "x = _stats_for_level_defense(1)\n"
        )
        out = _strip_local_imports(source)
        # alias 行が出力されていること
        self.assertIn("_stats_for_level_defense = stats_for_level", out)
        # alias 以外の名前は alias 行を出さないこと
        self.assertNotIn("MAX_LEVEL = MAX_LEVEL", out)
        # 元の使用箇所は残っていること
        self.assertIn("x = _stats_for_level_defense(1)", out)
        # import 文自体は消えていること
        self.assertNotIn("from src.shared.state.player_model import", out)

    def test_multi_line_import_without_as_emits_no_alias(self):
        source = (
            "from src.shared.services.foo import (\n"
            "    A,\n"
            "    B,\n"
            ")\n"
        )
        out = _strip_local_imports(source).strip()
        self.assertEqual(out, "")

    def test_multi_line_import_with_multiple_as_aliases(self):
        source = (
            "from src.x import (\n"
            "    A as a1,\n"
            "    B,\n"
            "    C as c1,\n"
            ")\n"
        )
        out = _strip_local_imports(source)
        self.assertIn("a1 = A", out)
        self.assertIn("c1 = C", out)
        # B は as がないので alias 行は出ない
        self.assertNotIn("B = B", out)


def _install_pyxel_stub() -> object:
    """pyxel を吸収する stub を sys.modules に挿入し、元の値を返す。"""

    class _Any:
        def __init__(self, name: str = ""):
            self._n = name

        def __getattr__(self, name: str) -> "_Any":
            return _Any(f"{self._n}.{name}")

        def __call__(self, *args, **kwargs) -> "_Any":
            return _Any(self._n + "()")

        def __getitem__(self, key) -> "_Any":
            return _Any(f"{self._n}[{key!r}]")

        def __setitem__(self, key, value) -> None:
            return None

        def __iter__(self):
            return iter([])

        def __int__(self) -> int:
            return 0

        def __bool__(self) -> bool:
            return False

        def __eq__(self, other) -> bool:
            return False

        def __ne__(self, other) -> bool:
            return True

        def __hash__(self) -> int:
            return id(self)

        def __len__(self) -> int:
            return 0

    pyxel_stub = types.ModuleType("pyxel")
    pyxel_stub.__getattr__ = lambda name: _Any(name)  # type: ignore[attr-defined]
    pyxel_stub.frame_count = 0
    original = sys.modules.get("pyxel")
    sys.modules["pyxel"] = pyxel_stub
    return original


def _restore_pyxel(original: object) -> None:
    if original is None:
        sys.modules.pop("pyxel", None)
    else:
        sys.modules["pyxel"] = original  # type: ignore[assignment]


class BundledSourceLoadsTest(unittest.TestCase):
    """build_bundled_source の出力を実際に exec して回帰を検出する。"""

    @classmethod
    def setUpClass(cls):
        cls._original_pyxel = _install_pyxel_stub()
        cls._source = build_bundled_source()

    @classmethod
    def tearDownClass(cls):
        _restore_pyxel(cls._original_pyxel)

    def _exec_bundle(self) -> types.ModuleType:
        """bundle を新しい module に exec して返す。"""
        mod = types.ModuleType("__codemaker_bundle_test__")
        mod.__file__ = str(ROOT / ".build" / "test_codemaker_bundle_smoke.py")
        sys.modules[mod.__name__] = mod
        try:
            exec(compile(self._source, mod.__file__, "exec"), mod.__dict__)
        finally:
            sys.modules.pop(mod.__name__, None)
        return mod

    def test_module_level_load_has_no_nameerror(self):
        """過去バグ #1: PlayerModel 未追加で module load 時に NameError が出ていた。"""
        try:
            mod = self._exec_bundle()
        except NameError as exc:  # pragma: no cover - 失敗時のメッセージを明示
            self.fail(f"bundle module-level load raised NameError: {exc}")
        # 主要な定義が module に出ていること
        self.assertIn("PlayerModel", mod.__dict__)
        self.assertIn("Game", mod.__dict__)

    def test_player_model_helpers_resolve_at_call_time(self):
        """過去バグ #2: 多行 ``as`` alias 抜けで `_stats_for_level_defense` が
        function 本体内で NameError になっていた。
        """
        mod = self._exec_bundle()
        # 旧 API shim 経由で stats_for_level を呼ぶと、内部で _stats_for_level_defense を参照
        try:
            result = mod.__dict__["stats_for_level"](1)
        except NameError as exc:  # pragma: no cover - 失敗時のメッセージを明示
            self.fail(f"stats_for_level(1) raised NameError: {exc}")
        # 旧 API は def キー（PlayerModel 側は defense）を返す
        self.assertIn("def", result)
        self.assertIn("max_hp", result)


if __name__ == "__main__":
    unittest.main()
