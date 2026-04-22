from __future__ import annotations

import base64
import json
from pathlib import Path

from src.shared.services.codemaker_resource_store import (
    RESOURCE_ENTRY_NAME,
    extract_codemaker_resource_archive,
)


BROWSER_IMPORT_ZIP_KEY = "blockquest_codemaker_zip_v1"
BROWSER_IMPORT_META_KEY = "blockquest_codemaker_zip_meta_v1"


def _load_browser_import_payload(js_module) -> tuple[str, dict[str, object]] | None:
    """ブラウザの localStorage から Code Maker 由来の zip base64 とメタ情報を読み出す。"""
    raw_zip = js_module.localStorage.getItem(BROWSER_IMPORT_ZIP_KEY)
    raw_meta = js_module.localStorage.getItem(BROWSER_IMPORT_META_KEY)
    if raw_zip is None or raw_meta is None:
        return None
    try:
        meta = json.loads(str(raw_meta))
    except json.JSONDecodeError:
        return None
    if not isinstance(meta, dict):
        return None
    return str(raw_zip), meta


def stage_browser_imported_resource(runtime_root: Path, *, js_module=None) -> Path | None:
    """ブラウザ実行時に localStorage の zip を展開し、実行用の pyxres として配置する。"""
    runtime_root = Path(runtime_root).resolve()
    if js_module is None:
        try:
            import js as js_module  # type: ignore[import-not-found]
        except ImportError:
            return None

    payload = _load_browser_import_payload(js_module)
    if payload is None:
        return None

    raw_zip, _meta = payload
    try:
        archive_bytes = base64.b64decode(raw_zip.encode("ascii"), validate=True)
        resource_bytes, _ignored_code_entries = extract_codemaker_resource_archive(archive_bytes)
    except (ValueError, TypeError):
        return None

    target_path = runtime_root / RESOURCE_ENTRY_NAME
    target_path.write_bytes(resource_bytes)
    return target_path
