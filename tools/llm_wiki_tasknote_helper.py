from __future__ import annotations

import sys
from pathlib import Path

_SHARED_CORE = Path.home() / "dotfiles/shared/llm-wiki-core/python"
if str(_SHARED_CORE) not in sys.path:
    sys.path.insert(0, str(_SHARED_CORE))

from llm_wiki_tasknote_helper import main, prepare_raw_tasknote, prepare_tasknote_material


if __name__ == "__main__":
    raise SystemExit(main())
