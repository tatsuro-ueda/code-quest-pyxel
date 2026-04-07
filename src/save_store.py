"""Persistence layer for Block Quest save data.

Three implementations:
  * FileSaveStore         — desktop, atomic write to save.json
  * LocalStorageSaveStore — Pyxel web (Pyodide), via js.localStorage
  * InMemorySaveStore     — unit tests

Use make_save_store() to pick the right one for the current environment.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional, Protocol


class SaveStoreError(OSError):
    """Raised when a SaveStore implementation cannot fulfil save/load."""


class SaveStore(Protocol):
    def exists(self) -> bool: ...
    def load(self) -> Optional[dict[str, Any]]: ...
    def save(self, data: dict[str, Any]) -> None: ...


SUPPORTED_SAVE_VERSIONS = (1,)


def _validate_loaded(data: Any) -> Optional[dict[str, Any]]:
    if not isinstance(data, dict):
        return None
    if data.get("save_version") not in SUPPORTED_SAVE_VERSIONS:
        return None
    return data


class InMemorySaveStore:
    """Test-only store. Holds a single in-RAM dict."""

    def __init__(self) -> None:
        self._data: Optional[dict[str, Any]] = None

    def exists(self) -> bool:
        return self._data is not None

    def load(self) -> Optional[dict[str, Any]]:
        if self._data is None:
            return None
        # JSON round-trip mimics real stores (catches non-serializable values).
        return json.loads(json.dumps(self._data))

    def save(self, data: dict[str, Any]) -> None:
        self._data = json.loads(json.dumps(data))


class FileSaveStore:
    """Desktop store. Atomic write via tmp file + os.replace."""

    def __init__(self, path: Path) -> None:
        self._path = Path(path)

    def exists(self) -> bool:
        return self._path.is_file()

    def load(self) -> Optional[dict[str, Any]]:
        if not self.exists():
            return None
        try:
            data = json.loads(self._path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return _validate_loaded(data)

    def save(self, data: dict[str, Any]) -> None:
        tmp_path = self._path.with_suffix(self._path.suffix + ".tmp")
        try:
            tmp_path.write_text(json.dumps(data, ensure_ascii=False), "utf-8")
            os.replace(tmp_path, self._path)
        except OSError as exc:
            try:
                tmp_path.unlink()
            except OSError:
                pass
            raise SaveStoreError(str(exc)) from exc


class LocalStorageSaveStore:
    """Web store. Backed by browser localStorage via Pyodide's `js` module.

    `import js` lives inside __init__ so desktop Python (which lacks `js`)
    can still import this module without errors.
    """

    KEY = "blockquest_save_v1"

    def __init__(self) -> None:
        import js  # type: ignore[import-not-found]
        self._js = js

    def exists(self) -> bool:
        return self._js.localStorage.getItem(self.KEY) is not None

    def load(self) -> Optional[dict[str, Any]]:
        raw = self._js.localStorage.getItem(self.KEY)
        if raw is None:
            return None
        try:
            data = json.loads(str(raw))
        except json.JSONDecodeError:
            return None
        return _validate_loaded(data)

    def save(self, data: dict[str, Any]) -> None:
        try:
            self._js.localStorage.setItem(
                self.KEY, json.dumps(data, ensure_ascii=False)
            )
        except Exception as exc:  # noqa: BLE001 - js exceptions vary
            raise SaveStoreError(str(exc)) from exc


def make_save_store(file_path: Path) -> SaveStore:
    """Pick the right SaveStore for the current Python runtime.

    On Pyodide (web Pyxel) the `js` module exists; on desktop it doesn't.
    """
    try:
        import js  # noqa: F401
        return LocalStorageSaveStore()
    except ImportError:
        return FileSaveStore(file_path)
