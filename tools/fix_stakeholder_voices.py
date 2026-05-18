"""stakeholder voices warning の安全な autofix 入口 (shim)。

Problems:
    - stakeholder_voices の自動修正経路が複数あると、安全 / 非安全な
      fix の境界が曖昧になり、CI / hook の挙動が読みにくい。

Solutions:
    - 本 shim を CLI 入口に固定し、実体は
      `stakeholder_voices.fix_stakeholder_voices` に委譲する。
    - 意味を変えない sort / dedupe だけを適用する方針を docstring で明示する。
"""

from stakeholder_voices.fix_stakeholder_voices import *  # noqa: F401,F403
from stakeholder_voices.fix_stakeholder_voices import main


if __name__ == "__main__":
    raise SystemExit(main())
