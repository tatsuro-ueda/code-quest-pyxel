"""このスクリプトは architecture rules の診断専用入口。`docs/architecture_rules.yml` に定義した deterministic rule を読み、repo 上の tree facts、entry point、generated file、manifest、runbook などの実体と照合して、warning / skipped / ok を JSON で返す。ファイルの書き換えや build の再実行は行わず、「いま何がずれているか」を機械的に可視化することだけを責務にする。"""

from architecture_rules.check_architecture_rules import *  # noqa: F401,F403
from architecture_rules.check_architecture_rules import main


if __name__ == "__main__":
    raise SystemExit(main())
