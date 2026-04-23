from __future__ import annotations

"""互換 shim. 本体は `src.shared.services.dialog_runner` に移動した（Q1A）。

P1-E4 で `src/scenes/dialog/` を削除するまでの一時的な再エクスポート。
新規コードは `src.shared.services.dialog_runner` を直接 import すること。
"""

from src.shared.services.dialog_runner import (
    DialogChoice,
    DialogStep,
    DialogValidationError,
    StructuredDialogRunner,
)

__all__ = [
    "DialogChoice",
    "DialogStep",
    "DialogValidationError",
    "StructuredDialogRunner",
]
