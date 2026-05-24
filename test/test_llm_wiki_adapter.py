from __future__ import annotations

import sys
import textwrap
from pathlib import Path

SHARED_CORE = Path.home() / "dotfiles/shared/llm-wiki-core/python"
if str(SHARED_CORE) not in sys.path:
    sys.path.insert(0, str(SHARED_CORE))

from adapter import load_adapter


def test_load_adapter_reads_named_tasknote_sections(tmp_path: Path) -> None:
    adapter_path = tmp_path / "llm-wiki/adapter.yml"
    adapter_path.parent.mkdir(parents=True, exist_ok=True)
    adapter_path.write_text(
        textwrap.dedent(
            """\
            raw_root: llm-wiki/raw
            summary_root: llm-wiki/wiki/summaries
            master_index_path: llm-wiki/wiki/indexes/master-index.md
            source_inbox_path: llm-wiki/wiki/logs/source-inbox.md
            ingest_log_path: llm-wiki/wiki/logs/ingest-log.md
            health_check_log_path: llm-wiki/wiki/logs/health-check-log.md
            area_root: llm-wiki/wiki/areas
            query_root: llm-wiki/wiki/query
            candidate_root: llm-wiki/wiki/candidates
            tasknote_required_sections:
              result: Result
              discussion: Discussion
              closing: Closing
            """
        ),
        encoding="utf-8",
    )

    adapter = load_adapter(tmp_path)

    assert adapter.raw_root == "llm-wiki/raw"
    assert adapter.tasknote_required_sections["discussion"] == "Discussion"
    assert adapter.tasknote_summary_root == "llm-wiki/wiki/summaries/tasknotes"
