"""このスクリプトは stakeholder voices の自己修復ループ入口。まず checker で warning を集め、次に fixer で安全な list 正規化だけを直し、最後に同じ rule 群を再検査する。最大回数まで回して warning が消えれば `OK` または `AUTOFIXED`、安全に直せない warning が残れば `NEEDS_HUMAN` を返す。"""

from stakeholder_voices.repair_stakeholder_voices import *  # noqa: F401,F403
from stakeholder_voices.repair_stakeholder_voices import main


if __name__ == "__main__":
    raise SystemExit(main())
