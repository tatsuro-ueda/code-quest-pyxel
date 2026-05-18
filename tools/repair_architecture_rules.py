"""architecture rule の自己修復ループ入口 (shim)。

Problems:
    - check と fix と再 check を別々に呼ぶと、運用側で順序を間違えやすく、
      result code (`OK` / `AUTOFIXED` / `NEEDS_HUMAN` / `ERROR`) も統一しにくい。

Solutions:
    - 本 shim を orchestration の CLI 入口に固定し、実体は
      `architecture_rules.repair_architecture_rules` に委譲する。
    - 診断・修復・再診断を束ねた最大回数ループの責務を docstring に明示する。
"""

from architecture_rules.repair_architecture_rules import *  # noqa: F401,F403
from architecture_rules.repair_architecture_rules import main


if __name__ == "__main__":
    raise SystemExit(main())
