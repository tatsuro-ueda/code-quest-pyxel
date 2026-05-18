"""architecture rules の診断専用入口 (shim)。

Problems:
    - architecture_rules パッケージへの呼び出し経路が複数あると、
      CI / hook / 手動実行で「どこを直すか」が散る。

Solutions:
    - 本 shim を CLI 入口に固定し、実体は
      `architecture_rules.check_architecture_rules` に委譲する。
    - 診断のみで書き換えはしないことを docstring で明示する。
"""

from architecture_rules.check_architecture_rules import *  # noqa: F401,F403
from architecture_rules.check_architecture_rules import main


if __name__ == "__main__":
    raise SystemExit(main())
