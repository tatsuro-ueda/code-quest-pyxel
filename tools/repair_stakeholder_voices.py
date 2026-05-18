"""stakeholder voices の自己修復ループ入口 (shim)。

Problems:
    - check と fix と再 check を別々に呼ぶと、運用側で順序を間違えやすく、
      result code (`OK` / `AUTOFIXED` / `NEEDS_HUMAN`) も統一しにくい。

Solutions:
    - 本 shim を orchestration の CLI 入口に固定し、実体は
      `stakeholder_voices.repair_stakeholder_voices` に委譲する。
    - 安全な list 正規化のみを反復適用する責務を docstring に明示する。
"""

from stakeholder_voices.repair_stakeholder_voices import *  # noqa: F401,F403
from stakeholder_voices.repair_stakeholder_voices import main


if __name__ == "__main__":
    raise SystemExit(main())
