from __future__ import annotations

"""Code Maker zip → pyxres 取り込みヘルパ（P3-E で dev staging を削除し 1 本化）。

Phase 3 以降、取り込んだ pyxres は直接 `assets/blockquest.pyxres` に
書き戻す。間 staging（`.runtime/codemaker_resource_imports/...`）は廃止。
"""

import hashlib
import io
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile


CANONICAL_RESOURCE = Path("assets") / "blockquest.pyxres"
CODE_ENTRY_NAME = "main.py"
RESOURCE_ENTRY_NAME = "my_resource.pyxres"


def _sha256_bytes(data: bytes) -> str:
    """バイト列の SHA-256 を16進文字列で返す。"""
    return hashlib.sha256(data).hexdigest()


def _canonical_resource_path(project_root: Path) -> Path:
    """正準（assets/配下）pyxres の絶対パスを返す。"""
    return project_root.resolve() / CANONICAL_RESOURCE


def _load_zip_entries(archive_bytes: bytes) -> tuple[list[str], ZipFile]:
    """zip バイト列を開き、エントリ名一覧と ZipFile ハンドルを返す。"""
    try:
        zip_file = ZipFile(io.BytesIO(archive_bytes))
    except BadZipFile as exc:
        raise ValueError("Code Maker zip として読めません") from exc
    return zip_file.namelist(), zip_file


def _resolve_resource_entry(entries: list[str]) -> str:
    """zip 内のエントリ名群から my_resource.pyxres を一意に特定する。"""
    exact_path = f"block-quest/{RESOURCE_ENTRY_NAME}"
    if exact_path in entries:
        return exact_path

    matches = [entry for entry in entries if entry.endswith(f"/{RESOURCE_ENTRY_NAME}") or entry == RESOURCE_ENTRY_NAME]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        raise ValueError("Code Maker zip に my_resource.pyxres がありません")
    raise ValueError("Code Maker zip に my_resource.pyxres が複数あります")


def extract_codemaker_resource_archive(archive_bytes: bytes) -> tuple[bytes, list[str]]:
    """Code Maker zip から pyxres バイト列を取り出し、同封コードエントリ名も返す。"""
    entries, zip_file = _load_zip_entries(archive_bytes)
    with zip_file:
        resource_entry = _resolve_resource_entry(entries)
        resource_bytes = zip_file.read(resource_entry)

    ignored_code_entries = [
        entry
        for entry in entries
        if entry.endswith(f"/{CODE_ENTRY_NAME}") or entry == CODE_ENTRY_NAME
    ]
    return resource_bytes, ignored_code_entries


def apply_imported_resource(
    project_root: Path,
    archive_bytes: bytes,
    *,
    source_name: str = "code-maker.zip",
) -> dict[str, object]:
    """Code Maker zip から pyxres を抽出し、正準パス（assets/blockquest.pyxres）へ書き戻す。

    Phase 3 以降の単一 artifact 方式：
    - dev staging を経由せず、本番 pyxres を直接更新する
    - 呼び出し側（web_runtime_server）はその後に production を再ビルドする
    """
    project_root = project_root.resolve()
    resource_bytes, ignored_code_entries = extract_codemaker_resource_archive(archive_bytes)

    canonical_path = _canonical_resource_path(project_root)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_bytes(resource_bytes)

    imported_at = datetime.now(timezone.utc).isoformat()
    return {
        "source_name": source_name,
        "resource_path": str(canonical_path),
        "resource_sha256": _sha256_bytes(resource_bytes),
        "source_zip_sha256": _sha256_bytes(archive_bytes),
        "ignored_code_entries": ignored_code_entries,
        "imported_at": imported_at,
    }
