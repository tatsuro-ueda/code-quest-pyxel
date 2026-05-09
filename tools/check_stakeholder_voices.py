"""このスクリプトは stakeholder voices の診断専用入口。`docs/stakeholder_voices.yml` に定義した deterministic rule を読み、stakeholder / request / requirement / task note frontmatter の実体と照合して、warning / ok を JSON で返す。ファイルの書き換えは行わず、「どこが task note 起票や requirement 参照の根拠として壊れているか」を機械的に可視化することだけを責務にする。"""

from stakeholder_voices.check_stakeholder_voices import *  # noqa: F401,F403
from stakeholder_voices.check_stakeholder_voices import main


if __name__ == "__main__":
    raise SystemExit(main())
