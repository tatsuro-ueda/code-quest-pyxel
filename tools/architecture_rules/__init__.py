"""architecture-rules YAML を扱う tools の公開 API をまとめる入口。

Problems:
    - check / fix / repair の各エントリ関数を内部モジュールから
      個別に import すると、呼び出し側の import 経路が散らばる。

Solutions:
    - パッケージ __init__.py で run_checker / run_fixer / run_repair を
      再エクスポートし、上位スクリプトはこの 1 行 import で完結させる。
"""
from .check_architecture_rules import run_checker  # noqa: F401
from .fix_architecture_rules import (  # noqa: F401
    FIXER_REGISTRY,
    run_fixer,
    write_yaml,
)
from .repair_architecture_rules import run_repair  # noqa: F401

__all__ = [
    "FIXER_REGISTRY",
    "run_checker",
    "run_fixer",
    "run_repair",
    "write_yaml",
]
