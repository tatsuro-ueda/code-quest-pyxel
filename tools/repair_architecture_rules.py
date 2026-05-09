"""このスクリプトは architecture rule の自己修復ループ入口。まず checker で現在の warning を集め、次に fixer で安全なものだけを直し、最後に同じ rule 群を再検査する。これを最大回数まで繰り返し、warning が消えれば `OK` または `AUTOFIXED`、安全に直せない warning が残れば `NEEDS_HUMAN`、内部例外なら `ERROR` を返す。つまり診断・修復・再診断を束ねる orchestration 層である。"""

from architecture_rules.repair_architecture_rules import *  # noqa: F401,F403
from architecture_rules.repair_architecture_rules import main


if __name__ == "__main__":
    raise SystemExit(main())
