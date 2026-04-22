from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional, Protocol


class SaveStoreError(OSError):
    """Raised when a SaveStore implementation cannot fulfil save/load."""


class SaveStore(Protocol):
    """セーブデータの有無確認・読み込み・書き込みを抽象化するインターフェース。"""

    def exists(self) -> bool: ...
    def load(self) -> Optional[dict[str, Any]]: ...
    def save(self, data: dict[str, Any]) -> None: ...


SUPPORTED_SAVE_VERSIONS = (1,)


def _validate_loaded(data: Any) -> Optional[dict[str, Any]]:
    """読み込んだオブジェクトが対応 save_version の dict か検証する。"""
    if not isinstance(data, dict):
        return None
    if data.get("save_version") not in SUPPORTED_SAVE_VERSIONS:
        return None
    return data


class InMemorySaveStore:
    """テスト用の揮発セーブストア。ディープコピーで外部変更から隔離する。"""

    def __init__(self) -> None:
        """保存データなし状態で初期化する。"""
        self._data: Optional[dict[str, Any]] = None

    def exists(self) -> bool:
        """セーブデータが保持されているかを返す。"""
        return self._data is not None

    def load(self) -> Optional[dict[str, Any]]:
        """保持データのディープコピーを返す（外部からの変更を防ぐ）。"""
        if self._data is None:
            return None
        return json.loads(json.dumps(self._data))

    def save(self, data: dict[str, Any]) -> None:
        """ディープコピーして保持する。"""
        self._data = json.loads(json.dumps(data))


class FileSaveStore:
    """ローカルファイルにセーブデータを JSON で書く実装（デスクトップ用）。"""

    def __init__(self, path: Path) -> None:
        """保存先パスを記憶する。"""
        self._path = Path(path)

    def exists(self) -> bool:
        """保存ファイルが存在するかを返す。"""
        return self._path.is_file()

    def load(self) -> Optional[dict[str, Any]]:
        """保存ファイルを読んで検証済み dict を返す（破損なら None）。"""
        if not self.exists():
            return None
        try:
            data = json.loads(self._path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return _validate_loaded(data)

    def save(self, data: dict[str, Any]) -> None:
        """一時ファイルに書いて atomic に置換する（途中失敗時は破損させない）。"""
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
    """ブラウザ localStorage にセーブデータを置く実装（Web 版用）。"""

    KEY = "blockquest_save_v1"

    def __init__(self) -> None:
        """js モジュールを取り込み、以後 localStorage を操作する。"""
        import js  # type: ignore[import-not-found]

        self._js = js

    def exists(self) -> bool:
        """localStorage に該当キーがあるかを返す。"""
        return self._js.localStorage.getItem(self.KEY) is not None

    def load(self) -> Optional[dict[str, Any]]:
        """localStorage から読み出して検証済み dict を返す。"""
        raw = self._js.localStorage.getItem(self.KEY)
        if raw is None:
            return None
        try:
            data = json.loads(str(raw))
        except json.JSONDecodeError:
            return None
        return _validate_loaded(data)

    def save(self, data: dict[str, Any]) -> None:
        """localStorage に JSON 文字列として書き込む。"""
        try:
            self._js.localStorage.setItem(self.KEY, json.dumps(data, ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            raise SaveStoreError(str(exc)) from exc


def make_save_store(file_path: Path) -> SaveStore:
    """実行環境（ブラウザ / ローカル）に応じた SaveStore 実装を返すファクトリ。"""
    try:
        import js  # noqa: F401

        return LocalStorageSaveStore()
    except ImportError:
        return FileSaveStore(file_path)
