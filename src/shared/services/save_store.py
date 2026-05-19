"""セーブデータの読み書きを抽象化する SaveStore 実装一式。

このファイルに含まれる関数・クラス：

- SaveStoreError: SaveStore 実装が save/load に失敗したときに送出する例外（メソッドなし）
- SaveStore: exists/load/save の構造的契約を表す Protocol
  - exists: セーブデータがあるかを返す抽象メソッド
  - load: セーブデータを読み込んで返す抽象メソッド
  - save: セーブデータを書き込む抽象メソッド
- _select_save_store_impl: js モジュールの import 成否で SaveStore 実装を選ぶ private 関数
- _validate_loaded: 読み込んだオブジェクトが対応 save_version の dict かを検証する private 関数
- InMemorySaveStore: テスト用に揮発で保持し、deep copy で外部変更を遮断する実装
  - __init__: 保持データなし状態で初期化する
  - exists: 保持データがあるかを返す
  - load: 保持データのディープコピーを返す
  - save: 入力をディープコピーして保持する
  - _clone_held_data: 保持データをディープコピーして返す private 委譲
  - _store_cloned: 入力をディープコピーして内部に置く private 委譲
- FileSaveStore: ローカルファイルに JSON で書く実装（デスクトップ用）
  - __init__: 保存先パスを記憶する
  - exists: 保存ファイルが存在するかを返す
  - load: 保存ファイルを読んで検証済み dict を返す
  - save: 一時ファイル経由で atomic に置換する
  - _read_validated: ファイルから読み出して検証する private 委譲
  - _write_atomic: 一時ファイルから本ファイルへ atomic 置換する private 委譲
- LocalStorageSaveStore: ブラウザ localStorage に置く実装（Web 版用）
  - __init__: js モジュールを取り込み、以後 localStorage を操作する
  - exists: localStorage に該当キーがあるかを返す
  - load: localStorage から読み出して検証済み dict を返す
  - save: localStorage に JSON 文字列として書き込む
  - _read_validated: localStorage から読んで検証する private 委譲
  - _write_json: localStorage へ JSON 文字列を書き込む private 委譲
- make_save_store: 実行環境に応じた SaveStore 実装を返すファクトリ

Problems:
    - セーブ書き込みの実装が file / localStorage / メモリで分かれているのに、
      呼び出し側で if 文を書き分けると、シーンや起動コードに環境判定が
      漏れて毎回保守の判断点が増える。
    - public な exists/load/save の本体に try/except や json parse を直書きすると
      入口契約と実装詳細が混ざり、テストや差し替えの境界がボケる。

Solutions:
    - SaveStore Protocol を「exists/load/save の 3 メソッド」だけに絞り、
      make_save_store で env 判定をファクトリに閉じ込めて呼び出し側を一本化する。
    - 各実装の public メソッドは「述語呼び出し + private 委譲 + return」のステップ列
      に揃え、ファイル I/O や JSON 解析は private helper に閉じ込める。
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional, Protocol


# === Public API ===


class SaveStoreError(OSError):
    """SaveStore 実装が save/load に失敗したときに送出する例外。"""

    # === Public API ===

    pass


class SaveStore(Protocol):
    """セーブデータの有無確認・読み込み・書き込みを抽象化する Protocol。"""

    # === Public API ===

    def exists(self) -> bool:  # noqa: CR100
        """セーブが存在するかを返す.

        Policy:
            - 実装ごとに保管先（ファイル / localStorage / メモリ）を見て判定する。
        """

    def load(self) -> Optional[dict[str, Any]]:
        """セーブデータを読み込んで返す.

        Returns:
            検証済みの dict、未保存または破損なら None。
        Policy:
            - 実装ごとに保管先から読み出し、検証は _validate_loaded に委譲する。
        """

    def save(self, data: dict[str, Any]) -> None:
        """セーブデータを書き込む.

        Args:
            data: 保存対象の dict。
        Policy:
            - 書き込みに失敗した実装は SaveStoreError を送出する。
        """


SUPPORTED_SAVE_VERSIONS = (1,)


class InMemorySaveStore:
    """テスト用の揮発セーブストア。ディープコピーで外部変更から隔離する。"""

    # === Public API ===

    def __init__(self) -> None:
        """保存データなし状態で初期化する。

        Policy:
            - 内部 dict は None スタートとし、save 呼び出しで初めて埋まる。
        """
        self._data: Optional[dict[str, Any]] = None

    def exists(self) -> bool:  # noqa: CR100
        """セーブデータが保持されているかを返す。

        Returns:
            保持データが None でなければ True。
        Policy:
            - 副作用を持たない単純な述語。
        """
        return self._data is not None

    def load(self) -> Optional[dict[str, Any]]:
        """保持データのディープコピーを返す（外部からの変更を防ぐ）。

        Returns:
            ディープコピーされた dict、未保存なら None。
        Policy:
            - 空判定とコピーは _clone_held_data に閉じる。
        """
        return self._clone_held_data()

    def save(self, data: dict[str, Any]) -> None:
        """ディープコピーして保持する。

        Args:
            data: 保存対象の dict。
        Policy:
            - 入力 dict の変更が内部状態に漏れないよう deep copy する。
        """
        self._store_cloned(data)

    # === Internal helpers (private) ===

    def _clone_held_data(self) -> Optional[dict[str, Any]]:
        """保持データをディープコピーして返す private 委譲。

        Returns:
            json round-trip による deep copy 結果、未保存なら None。
        Policy:
            - 未保存（None）も deep copy 経由で素通しすることで load の本体を 1 行に保つ。
        """
        if self._data is None:
            return None
        return json.loads(json.dumps(self._data))

    def _store_cloned(self, data: dict[str, Any]) -> None:
        """入力 dict をディープコピーして内部に保存する private 委譲。

        Args:
            data: 保存対象の dict。
        Policy:
            - 後段の外部 mutation を遮断するために json round-trip する。
        """
        self._data = json.loads(json.dumps(data))


class FileSaveStore:
    """ローカルファイルにセーブデータを JSON で書く実装（デスクトップ用）。"""

    # === Public API ===

    def __init__(self, path: Path) -> None:
        """保存先パスを記憶する。

        Args:
            path: 保存ファイルの絶対 or 相対パス。
        Policy:
            - 渡された path は Path 化して保持する。
        """
        self._path = Path(path)

    def exists(self) -> bool:  # noqa: CR100
        """保存ファイルが存在するかを返す。

        Returns:
            ファイルとして存在すれば True。
        Policy:
            - Path.is_file の薄いラッパー。
        """
        return self._path.is_file()

    def load(self) -> Optional[dict[str, Any]]:
        """保存ファイルを読んで検証済み dict を返す（破損なら None）。

        Returns:
            検証済み dict、未保存または破損なら None。
        Policy:
            - 存在判定・I/O・検証は _read_validated に閉じる。
        """
        return self._read_validated()

    def save(self, data: dict[str, Any]) -> None:
        """一時ファイルに書いて atomic に置換する。

        Args:
            data: 保存対象の dict。
        Policy:
            - 途中失敗時にも本ファイルを破損させないよう _write_atomic に委譲する。
        """
        self._write_atomic(data)

    # === Internal helpers (private) ===

    def _read_validated(self) -> Optional[dict[str, Any]]:
        """ファイルを読み出して _validate_loaded で検証した dict を返す。

        Returns:
            検証済み dict、不在・JSON 不正・OSError・version 不一致なら None。
        Policy:
            - 不在判定と JSON 解析と OSError をここで吸収し、load 本体を 1 行に保つ。
        """
        if not self._path.is_file():
            return None
        try:
            data = json.loads(self._path.read_text("utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
        return _validate_loaded(data)

    def _write_atomic(self, data: dict[str, Any]) -> None:
        """tmp に書いてから本ファイルへ atomic に置換する。

        Args:
            data: 保存対象の dict。
        Raises:
            SaveStoreError: tmp 書き込みまたは置換に失敗した場合。
        Policy:
            - 失敗時は tmp を可能な限り削除し、SaveStoreError に正規化する。
        """
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

    # === Public API ===

    KEY = "blockquest_save_v1"

    def __init__(self) -> None:
        """js モジュールを取り込み、以後 localStorage を操作する。

        Policy:
            - import 失敗時は呼び出し側（make_save_store）が File 実装にフォールバック
              するため、ここでは ImportError を握りつぶさない。
        """
        import js  # type: ignore[import-not-found]

        self._js = js

    def exists(self) -> bool:  # noqa: CR100
        """localStorage に該当キーがあるかを返す。

        Returns:
            キーに値があれば True。
        Policy:
            - 単純な getItem の比較で副作用なし。
        """
        return self._js.localStorage.getItem(self.KEY) is not None

    def load(self) -> Optional[dict[str, Any]]:
        """localStorage から読み出して検証済み dict を返す。

        Returns:
            検証済み dict、未保存または破損なら None。
        Policy:
            - getItem と JSON 解析と version 検証は _read_validated に閉じる。
        """
        return self._read_validated()

    def save(self, data: dict[str, Any]) -> None:
        """localStorage に JSON 文字列として書き込む。

        Args:
            data: 保存対象の dict。
        Policy:
            - setItem 失敗時は SaveStoreError に正規化し、呼び出し側の例外面を統一する。
        """
        self._write_json(data)

    # === Internal helpers (private) ===

    def _read_validated(self) -> Optional[dict[str, Any]]:
        """localStorage から読んで JSON 解析と version 検証を済ませた dict を返す。

        Returns:
            検証済み dict、不在または JSON 不正なら None。
        Policy:
            - JSON 解析失敗は None に丸め、上位での try/except を不要にする。
        """
        raw = self._js.localStorage.getItem(self.KEY)
        if raw is None:
            return None
        try:
            data = json.loads(str(raw))
        except json.JSONDecodeError:
            return None
        return _validate_loaded(data)

    def _write_json(self, data: dict[str, Any]) -> None:
        """localStorage へ JSON 文字列として書き込む private 委譲。

        Args:
            data: 保存対象の dict。
        Raises:
            SaveStoreError: setItem に失敗した場合。
        Policy:
            - 例外は何であれ SaveStoreError に正規化する（Web 側の例外型差異を吸収）。
        """
        try:
            self._js.localStorage.setItem(
                self.KEY, json.dumps(
                    data, ensure_ascii=False))
        except Exception as exc:  # noqa: BLE001
            raise SaveStoreError(str(exc)) from exc


def make_save_store(file_path: Path) -> SaveStore:
    """実行環境に応じた SaveStore 実装を返すファクトリ。

    Args:
        file_path: デスクトップ実行時に使う保存ファイルのパス。
    Returns:
        Web（js 取り込み成功）なら LocalStorageSaveStore、そうでなければ FileSaveStore。
    Policy:
        - 環境判定は _select_save_store_impl に閉じ込め、本体はその委譲だけにする。
    """
    return _select_save_store_impl(file_path)


# === Internal helpers (private) ===


def _select_save_store_impl(file_path: Path) -> SaveStore:
    """js モジュールの import 成否で SaveStore 実装を選ぶ private 委譲。

    Args:
        file_path: デスクトップ実行時に使う保存ファイルのパス。
    Returns:
        js が import できれば LocalStorageSaveStore、できなければ FileSaveStore。
    Policy:
        - try/except は public 関数からこちらへ寄せ、make_save_store を 1 行委譲に保つ。
    """
    try:
        import js  # noqa: F401

        return LocalStorageSaveStore()
    except ImportError:
        return FileSaveStore(file_path)


def _validate_loaded(data: Any) -> Optional[dict[str, Any]]:
    """読み込んだオブジェクトが対応 save_version の dict かを検証する。

    Args:
        data: load 経路から渡された任意オブジェクト。
    Returns:
        対応 save_version を持つ dict ならそれ自身、そうでなければ None。
    Policy:
        - dict でない、または save_version が SUPPORTED_SAVE_VERSIONS に無いなら None を返す。
    """
    if not isinstance(data, dict):
        return None
    if data.get("save_version") not in SUPPORTED_SAVE_VERSIONS:
        return None
    return data
