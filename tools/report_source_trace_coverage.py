"""このスクリプトは stakeholder voices の source trace coverage 入口。`docs/stakeholder_voices.yml` の source document catalog と active source_trace_refs を読み、document ごとの total / referenced / missing stable ref を JSON で返す。壊れた doc id や extraction contract は success のふりをせず `BROKEN_TRACEABILITY` として返す。"""

from stakeholder_voices.source_trace_coverage import *  # noqa: F401,F403
from stakeholder_voices.source_trace_coverage import main


if __name__ == "__main__":
    raise SystemExit(main())
