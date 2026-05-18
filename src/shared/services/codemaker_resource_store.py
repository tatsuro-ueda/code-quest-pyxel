"""Code Maker zip → pyxres 取り込みヘルパ（P3-E で dev staging を削除し 1 本化）。

このファイルに含まれる関数・クラス：

- Code Maker zip から pyxres を抽出して同封コード名も返す
  public 関数 extract_codemaker_resource_archive
- zip を抽出して正準パスへ書き戻し、取り込み記録 dict を返す public 関数 apply_imported_resource
- バイト列の SHA-256 を 16 進文字列にする private 関数 _compute_sha256_hex
- 正準 pyxres の絶対パスを返す private 関数 _resolve_canonical_resource_path
- zip バイト列を開いてエントリ一覧と ZipFile を返す private 関数 _load_zip_entries
- zip エントリ一覧から my_resource.pyxres を一意特定する private 関数 _resolve_resource_entry
- zip から resource エントリを読み出してバイト列で返す private 関数 _read_resource_bytes
- zip エントリ一覧から無視対象のコードエントリ名だけ拾う private 関数 _collect_code_entries
- 抽出した resource バイトを正準パスへ書き戻す private 関数 _write_canonical_resource
- 取り込み記録 payload を組み立てる private 関数 _build_import_record

Problems:
    - dev staging を経由した取り込みは経路が二重になり、
      正準 pyxres と staging のどちらが「真」か運用で揺れていた。
    - public 関数に zip 解凍と書き戻しと payload 整形を直書きすると、
      入口契約と実装詳細が混ざってシーン側からのテストもしづらい。

Solutions:
    - Phase 3 以降は staging を廃止し、Code Maker zip から正準
      `assets/blockquest.pyxres` へ直接書き戻す 1 本道に揃える。
    - public 関数は「述語呼び出し + private 委譲 + return」のステップ列に
      し、ハッシュ計算・zip 解析・正準パス解決・書き戻し・payload 整形は
      private helper に分離する。
"""
from __future__ import annotations

import hashlib
import io
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile


CANONICAL_RESOURCE = Path("assets") / "blockquest.pyxres"
CODE_ENTRY_NAME = "main.py"
RESOURCE_ENTRY_NAME = "my_resource.pyxres"


# === Public API ===

def extract_codemaker_resource_archive(
        archive_bytes: bytes) -> tuple[bytes, list[str]]:
    """Code Maker zip から pyxres バイト列を取り出し、同封コードエントリ名も返す。

    Args:
        archive_bytes: Code Maker からダウンロードした zip のバイト列。
    Returns:
        (pyxres バイト列, 無視対象として記録するコードエントリ名のリスト)。
    Policy:
        - public 関数は zip 展開・エントリ特定・同封コード収集に絞り、
          BadZipFile は ValueError に正規化して呼び出し側の例外面を統一する。
    """
    entries, zip_file = _load_zip_entries(archive_bytes)
    resource_bytes = _read_resource_bytes(zip_file, entries)
    ignored_code_entries = _collect_code_entries(entries)
    return resource_bytes, ignored_code_entries


def apply_imported_resource(
    project_root: Path,
    archive_bytes: bytes,
    *,
    source_name: str = "code-maker.zip",
) -> dict[str, object]:
    """Code Maker zip から pyxres を抽出し、正準パスへ書き戻して取り込み記録を返す。

    Args:
        project_root: リポジトリのルート（正準 pyxres を解決する基点）。
        archive_bytes: Code Maker zip のバイト列。
        source_name: 記録用の元 zip ファイル名（デフォルトは code-maker.zip）。
    Returns:
        source_name / resource_path / resource_sha256 / source_zip_sha256 /
        ignored_code_entries / imported_at を含む取り込み記録 dict。
    Policy:
        - Phase 3 以降の単一 artifact 方式：staging を経ず本番 pyxres を
          直接更新する。呼び出し側（web_runtime_server）はその後に
          production を再ビルドする。
        - public 関数はステップ列に揃え、抽出・書き戻し・payload 整形を
          private helper に委ねる。
    """
    project_root = project_root.resolve()
    resource_bytes, ignored_code_entries = extract_codemaker_resource_archive(
        archive_bytes)
    canonical_path = _write_canonical_resource(project_root, resource_bytes)
    return _build_import_record(
        source_name=source_name,
        canonical_path=canonical_path,
        resource_bytes=resource_bytes,
        archive_bytes=archive_bytes,
        ignored_code_entries=ignored_code_entries,
    )


# === Internal helpers (private) ===

def _compute_sha256_hex(data: bytes) -> str:
    """バイト列の SHA-256 を 16 進文字列で返す。

    Args:
        data: 任意のバイト列。
    Returns:
        SHA-256 ハッシュの hex 表現。
    Policy:
        - 取り込み記録での `resource_sha256` / `source_zip_sha256` 算出に
          のみ使う薄いラッパに留める。
    """
    return hashlib.sha256(data).hexdigest()


def _resolve_canonical_resource_path(project_root: Path) -> Path:
    """正準（assets/配下）pyxres の絶対パスを返す。

    Args:
        project_root: リポジトリのルート（resolve 済みを期待）。
    Returns:
        `<project_root>/assets/blockquest.pyxres` の絶対パス。
    Policy:
        - 正準パスの組み立てを 1 か所に閉じ込め、書き戻し先のブレを防ぐ。
    """
    return project_root.resolve() / CANONICAL_RESOURCE


def _load_zip_entries(archive_bytes: bytes) -> tuple[list[str], ZipFile]:
    """zip バイト列を開き、エントリ名一覧と ZipFile ハンドルを返す。

    Args:
        archive_bytes: Code Maker zip のバイト列。
    Returns:
        (zip エントリ名のリスト, 同じ zip の ZipFile ハンドル)。
    Raises:
        ValueError: BadZipFile を ValueError に正規化して再送出する。
    Policy:
        - 呼び出し側で `with zip_file:` して資源解放する責務を共有する。
    """
    try:
        zip_file = ZipFile(io.BytesIO(archive_bytes))
    except BadZipFile as exc:
        raise ValueError("Code Maker zip として読めません") from exc
    return zip_file.namelist(), zip_file


def _resolve_resource_entry(entries: list[str]) -> str:
    """zip 内のエントリ名群から my_resource.pyxres を一意に特定する。

    Args:
        entries: zip の namelist。
    Returns:
        my_resource.pyxres を指すエントリ名（block-quest/ 優先）。
    Raises:
        ValueError: pyxres が無い／複数あって特定できないとき。
    Policy:
        - `block-quest/my_resource.pyxres` を最優先し、無ければ末尾一致で
          一意候補なら採用、それ以外は ValueError に倒す。
    """
    exact_path = f"block-quest/{RESOURCE_ENTRY_NAME}"
    if exact_path in entries:
        return exact_path

    matches = [entry for entry in entries if entry.endswith(
        f"/{RESOURCE_ENTRY_NAME}") or entry == RESOURCE_ENTRY_NAME]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError("Code Maker zip に my_resource.pyxres がありません")
    raise ValueError("Code Maker zip に my_resource.pyxres が複数あります")


def _read_resource_bytes(zip_file: ZipFile, entries: list[str]) -> bytes:
    """zip 内の resource エントリを特定して読み込み、バイト列で返す。

    Args:
        zip_file: 開いている ZipFile（このヘルパが close する）。
        entries: zip_file.namelist() と同じエントリ一覧。
    Returns:
        my_resource.pyxres の中身バイト列。
    Policy:
        - エントリ特定と read を 1 か所にまとめ、`with` ブロックでの
          資源解放を public 関数から見えなくする。
    """
    with zip_file:
        resource_entry = _resolve_resource_entry(entries)
        return zip_file.read(resource_entry)


def _collect_code_entries(entries: list[str]) -> list[str]:
    """zip エントリ一覧から main.py 系のコードエントリ名だけ拾って返す。

    Args:
        entries: zip_file.namelist() の結果。
    Returns:
        無視対象として記録するコードエントリ名のリスト。
    Policy:
        - 取り込み記録の ignored_code_entries に使う情報用ヘルパに留める。
    """
    return [
        entry
        for entry in entries
        if entry.endswith(f"/{CODE_ENTRY_NAME}") or entry == CODE_ENTRY_NAME
    ]


def _write_canonical_resource(
        project_root: Path, resource_bytes: bytes) -> Path:
    """抽出した pyxres バイトを正準パスへ書き戻し、書き戻した絶対パスを返す。

    Args:
        project_root: リポジトリのルート（resolve 済み）。
        resource_bytes: 書き込む pyxres のバイト列。
    Returns:
        書き戻した正準 pyxres の絶対パス。
    Policy:
        - 親ディレクトリを mkdir(parents=True) しておき、初回起動でも
          write_bytes が落ちないようにする。
    """
    canonical_path = _resolve_canonical_resource_path(project_root)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_bytes(resource_bytes)
    return canonical_path


def _build_import_record(
    *,
    source_name: str,
    canonical_path: Path,
    resource_bytes: bytes,
    archive_bytes: bytes,
    ignored_code_entries: list[str],
) -> dict[str, object]:
    """取り込み記録 dict を組み立てる（ハッシュと imported_at を含む）。

    Args:
        source_name: 取り込み元 zip ファイル名。
        canonical_path: 書き戻した正準 pyxres の絶対パス。
        resource_bytes: 書き戻した pyxres のバイト列。
        archive_bytes: 元の zip バイト列。
        ignored_code_entries: 無視対象として記録するコードエントリ名。
    Returns:
        web_runtime_server が JSON 化する取り込み記録 dict。
    Policy:
        - フィールド構成を変えると配信側の表示が壊れるため、キー名は固定。
    """
    imported_at = datetime.now(timezone.utc).isoformat()
    return {
        "source_name": source_name,
        "resource_path": str(canonical_path),
        "resource_sha256": _compute_sha256_hex(resource_bytes),
        "source_zip_sha256": _compute_sha256_hex(archive_bytes),
        "ignored_code_entries": ignored_code_entries,
        "imported_at": imported_at,
    }
