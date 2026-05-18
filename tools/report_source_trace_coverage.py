"""stakeholder voices の source trace coverage 入口 (shim)。

Problems:
    - source trace coverage の集計を毎回手書きで呼び出すと、broken doc id
      や extraction contract の扱いが運用ごとにブレる。

Solutions:
    - 本 shim を CLI 入口に固定し、実体は
      `stakeholder_voices.source_trace_coverage` に委譲する。
    - 壊れた traceability を `BROKEN_TRACEABILITY` として返す挙動を
      docstring に明示する。
"""

from stakeholder_voices.source_trace_coverage import *  # noqa: F401,F403
from stakeholder_voices.source_trace_coverage import main


if __name__ == "__main__":
    raise SystemExit(main())
