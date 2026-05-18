"""architecture rule warning の安全な autofix 入口 (shim)。

Problems:
    - architecture_rules の自動修正経路が複数あると、安全 / 非安全な
      fix の境界が曖昧になり、CI / hook の挙動が読みにくい。

Solutions:
    - 本 shim を CLI 入口に固定し、実体は
      `architecture_rules.fix_architecture_rules` に委譲する。
    - 副作用範囲を限定できる fix だけを適用する方針を docstring で明示する。
"""

from architecture_rules.fix_architecture_rules import *  # noqa: F401,F403
from architecture_rules.fix_architecture_rules import main


if __name__ == "__main__":
    raise SystemExit(main())
