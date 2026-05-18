"""stakeholder voices の診断専用入口 (shim)。

Problems:
    - stakeholder_voices パッケージへの呼び出し経路が複数あると、
      CI / hook / 手動実行で「どこを直すか」が散る。

Solutions:
    - 本 shim を CLI 入口に固定し、実体は
      `stakeholder_voices.check_stakeholder_voices` に委譲する。
    - 診断のみで書き換えはしないことを docstring で明示する。
"""

from stakeholder_voices.check_stakeholder_voices import *  # noqa: F401,F403
from stakeholder_voices.check_stakeholder_voices import main


if __name__ == "__main__":
    raise SystemExit(main())
