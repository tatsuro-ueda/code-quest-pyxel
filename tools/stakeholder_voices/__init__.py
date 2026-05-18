"""stakeholder-voices YAML を扱う tools の公開 API をまとめる入口。

Problems:
    - check / fix / repair / coverage の各エントリ関数を個別 import すると、
      呼び出し側の import 経路がバラつく。

Solutions:
    - パッケージ __init__.py で run_checker / run_fixer / run_repair /
      run_report / build_report / write_yaml / FIXER_REGISTRY をまとめて
      再エクスポートし、上位スクリプトはこの 1 行 import で完結させる。
"""
from .check_stakeholder_voices import run_checker  # noqa: F401
from .fix_stakeholder_voices import (  # noqa: F401
    FIXER_REGISTRY,
    run_fixer,
    write_yaml,
)
from .repair_stakeholder_voices import run_repair  # noqa: F401
from .source_trace_coverage import build_report, run_report  # noqa: F401

__all__ = [
    "FIXER_REGISTRY",
    "build_report",
    "run_checker",
    "run_fixer",
    "run_repair",
    "run_report",
    "write_yaml",
]
