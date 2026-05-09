"""このスクリプトは stakeholder voices warning に対する一回限りの安全な autofix 入口。checker が返した warning のうち、requirement list の sort / dedupe のように意味を変えない正規化だけを適用する。要求内容の補完や path の推測は行わず、修正結果と適用した fix 一覧を JSON で返す。"""

from stakeholder_voices.fix_stakeholder_voices import *  # noqa: F401,F403
from stakeholder_voices.fix_stakeholder_voices import main


if __name__ == "__main__":
    raise SystemExit(main())
