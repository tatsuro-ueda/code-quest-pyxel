from __future__ import annotations

import hashlib
import io
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from zipfile import BadZipFile, ZipFile


IMPORT_ROOT = Path(".runtime") / "codemaker_resource_imports"
IMPORT_MANIFEST = IMPORT_ROOT / "development.json"
IMPORT_RESOURCE = IMPORT_ROOT / "development" / "my_resource.pyxres"
CANONICAL_RESOURCE = Path("assets") / "blockquest.pyxres"
CODE_ENTRY_NAME = "main.py"
RESOURCE_ENTRY_NAME = "my_resource.pyxres"


def _sha256_bytes(data: bytes) -> str:
    """バイト列の SHA-256 を16進文字列で返す。"""
    return hashlib.sha256(data).hexdigest()


def _manifest_path(project_root: Path) -> Path:
    """インポート manifest JSON の絶対パスを返す。"""
    return project_root.resolve() / IMPORT_MANIFEST


def _imported_resource_path(project_root: Path) -> Path:
    """インポート先の pyxres ファイル絶対パスを返す。"""
    return project_root.resolve() / IMPORT_RESOURCE


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


def import_codemaker_resource_zip(
    project_root: Path,
    archive_bytes: bytes,
    *,
    source_name: str = "code-maker.zip",
) -> dict[str, object]:
    """Code Maker zip を取り込み、インポート先に pyxres を書き出して manifest を残す。"""
    project_root = project_root.resolve()
    resource_bytes, ignored_code_entries = extract_codemaker_resource_archive(archive_bytes)

    imported_path = _imported_resource_path(project_root)
    imported_path.parent.mkdir(parents=True, exist_ok=True)
    imported_path.write_bytes(resource_bytes)

    base_resource_bytes = _canonical_resource_path(project_root).read_bytes()
    changed_from_base = resource_bytes != base_resource_bytes
    imported_at = datetime.now(timezone.utc).isoformat()
    manifest = {
        "source_name": source_name,
        "resource_path": str(imported_path),
        "resource_sha256": _sha256_bytes(resource_bytes),
        "base_resource_sha256": _sha256_bytes(base_resource_bytes),
        "source_zip_sha256": _sha256_bytes(archive_bytes),
        "ignored_code_entries": ignored_code_entries,
        "changed_from_base": changed_from_base,
        "imported_at": imported_at,
    }
    manifest_path = _manifest_path(project_root)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def load_imported_resource_manifest(project_root: Path) -> dict[str, object] | None:
    """インポート manifest を読み込んで dict で返す（未インポートなら None）。"""
    project_root = project_root.resolve()
    manifest_path = _manifest_path(project_root)
    if not manifest_path.is_file():
        return None
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{manifest_path} must contain a JSON object")
    return data


def get_imported_resource_path(project_root: Path) -> Path | None:
    """インポート済み pyxres のパスを返す（未インポートなら None）。"""
    project_root = project_root.resolve()
    resource_path = _imported_resource_path(project_root)
    manifest = load_imported_resource_manifest(project_root)
    if manifest is None or not resource_path.is_file():
        return None
    return resource_path


def clear_imported_resource(project_root: Path) -> None:
    """インポート済み pyxres と manifest を削除し、空ディレクトリも片付ける。"""
    project_root = project_root.resolve()
    resource_path = _imported_resource_path(project_root)
    manifest_path = _manifest_path(project_root)

    if resource_path.exists():
        resource_path.unlink()
    if manifest_path.exists():
        manifest_path.unlink()

    resource_dir = resource_path.parent
    if resource_dir.exists():
        try:
            resource_dir.rmdir()
        except OSError:
            pass
    if manifest_path.parent.exists():
        try:
            manifest_path.parent.rmdir()
        except OSError:
            pass


def promote_imported_resource(project_root: Path) -> bool:
    """インポート済み pyxres を正準資産（assets/）に昇格し、インポートを後片付けする。"""
    project_root = project_root.resolve()
    imported_path = get_imported_resource_path(project_root)
    if imported_path is None:
        return False

    canonical_path = _canonical_resource_path(project_root)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(imported_path, canonical_path)
    clear_imported_resource(project_root)
    return True
