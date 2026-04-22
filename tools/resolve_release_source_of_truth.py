from __future__ import annotations

import difflib
from dataclasses import dataclass
import hashlib
import json
import subprocess
from pathlib import Path

from src.shared.services.codemaker_resource_store import (
    IMPORT_MANIFEST,
    IMPORT_RESOURCE,
    get_imported_resource_path,
)


DEVELOPMENT_META_FILE = Path("development_meta.json")
RESOURCE_IMPORT_CHANGE = "Code Maker の resource を とりこんだ"
DEVELOPMENT_AUTO_CHANGE_RULES = (
    ("つうしんとうの ノイズガーディアンが フィールドに でない", ("is_noise_guardian",)),
    ("まおうを たおしたあとも つづきに すすめる", ("dungeon.glitch.exit", "callback=None")),
    ("まおうまえに おはなしが はじまる", ("_enter_glitch_lord_intro", "boss.glitch.prebattle_01")),
)


@dataclass(frozen=True)
class DevelopmentCandidate:
    main_source: Path
    resource_source: Path
    changes: list[str]
    uses_preview_code: bool
    uses_imported_resource: bool


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_git_dirty(root: Path, rel_path: Path) -> bool:
    git_dir = root / ".git"
    if not git_dir.exists():
        return False

    tracked = subprocess.run(
        ["git", "ls-files", "--error-unmatch", "--", rel_path.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if tracked.returncode != 0:
        return True

    dirty = subprocess.run(
        ["git", "diff", "--quiet", "HEAD", "--", rel_path.as_posix()],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return dirty.returncode == 1


def revision_timestamp(root: Path, rel_path: Path) -> float:
    path = root / rel_path
    if not path.exists():
        return 0.0

    git_dir = root / ".git"
    if git_dir.exists():
        if is_git_dirty(root, rel_path):
            return path.stat().st_mtime
        tracked = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", rel_path.as_posix()],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if tracked.returncode != 0:
            return path.stat().st_mtime

        result = subprocess.run(
            ["git", "log", "-1", "--format=%ct", "--", rel_path.as_posix()],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            return float(result.stdout.strip())

    return path.stat().st_mtime


def validate_change_list_freshness(
    root: Path,
    *,
    changes_rel_path: Path,
    dependency_paths: tuple[Path, ...],
) -> None:
    root = root.resolve()
    changes_path = root / changes_rel_path
    if not changes_path.exists():
        return
    if is_git_dirty(root, changes_rel_path):
        return

    changes_timestamp = revision_timestamp(root, changes_rel_path)
    for dependency in dependency_paths:
        dependency_path = root / dependency
        if not dependency_path.exists():
            continue
        dependency_timestamp = revision_timestamp(root, dependency)
        if dependency_timestamp > changes_timestamp:
            raise ValueError(
                f"{changes_rel_path} is older than {dependency}. "
                "Update the change list so selector text matches the shipped content."
            )


def build_cache_token(root: Path, dependency_paths: tuple[Path, ...]) -> str:
    root = root.resolve()
    timestamps = [
        revision_timestamp(root, dependency)
        for dependency in dependency_paths
        if (root / dependency).exists()
    ]
    if not timestamps:
        return "0"
    return str(int(max(timestamps)))


def _resource_override_differs_from_base(root: Path, imported_resource_path: Path | None) -> bool:
    if imported_resource_path is None or not imported_resource_path.is_file():
        return False
    base_resource = root / "assets" / "blockquest.pyxres"
    return imported_resource_path.read_bytes() != base_resource.read_bytes()


def build_development_change_list(root: Path) -> list[str]:
    root = root.resolve()
    main_path = root / "main.py"
    preview_path = root / "main_development.py"
    if not main_path.is_file():
        raise FileNotFoundError(f"main.py not found at {main_path}")
    if not preview_path.is_file():
        raise FileNotFoundError(f"main_development.py not found at {preview_path}")

    main_text = main_path.read_text(encoding="utf-8")
    preview_text = preview_path.read_text(encoding="utf-8")
    if main_text == preview_text:
        raise ValueError("main_development.py must contain at least one 開発版専用変更")

    diff_lines = list(
        difflib.unified_diff(
            main_text.splitlines(),
            preview_text.splitlines(),
            fromfile="main.py",
            tofile="main_development.py",
            lineterm="",
        )
    )
    changed_text = "\n".join(
        line[1:]
        for line in diff_lines
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    )

    changes: list[str] = []
    for message, markers in DEVELOPMENT_AUTO_CHANGE_RULES:
        if all(marker in changed_text for marker in markers):
            changes.append(message)

    if not changes:
        changes.append("開発版の ないようを こうしん")

    return list(dict.fromkeys(changes))


def resolve_development_candidate(root: Path) -> DevelopmentCandidate:
    root = root.resolve()
    main_path = root / "main.py"
    preview_path = root / "main_development.py"
    resource_path = root / "assets" / "blockquest.pyxres"
    imported_resource_path = get_imported_resource_path(root)

    uses_preview_code = False
    main_source = main_path
    if preview_path.is_file() and preview_path.read_text(encoding="utf-8") != main_path.read_text(encoding="utf-8"):
        uses_preview_code = True
        main_source = preview_path

    uses_imported_resource = _resource_override_differs_from_base(root, imported_resource_path)
    resource_source = imported_resource_path if uses_imported_resource and imported_resource_path is not None else resource_path

    if not uses_preview_code and not uses_imported_resource:
        raise ValueError("development candidate requires preview code or imported resource changes")

    changes: list[str] = []
    if uses_preview_code:
        changes.extend(build_development_change_list(root))
    if uses_imported_resource:
        changes.append(RESOURCE_IMPORT_CHANGE)

    return DevelopmentCandidate(
        main_source=main_source,
        resource_source=resource_source,
        changes=list(dict.fromkeys(changes)),
        uses_preview_code=uses_preview_code,
        uses_imported_resource=uses_imported_resource,
    )


def build_development_dependency_paths(root: Path, candidate: DevelopmentCandidate) -> tuple[Path, ...]:
    dependency_paths = [
        Path("main.py"),
        Path("assets/blockquest.pyxres"),
        Path("templates/wrapper.html"),
        Path("templates/selector.html"),
        Path("templates/codemaker_import_ui.js"),
        DEVELOPMENT_META_FILE,
    ]
    if candidate.uses_preview_code:
        dependency_paths.append(Path("main_development.py"))
    if candidate.uses_imported_resource:
        dependency_paths.extend([IMPORT_MANIFEST, IMPORT_RESOURCE])
    return tuple(dict.fromkeys(dependency_paths))


def build_development_codemaker_dependency_paths(root: Path, candidate: DevelopmentCandidate) -> tuple[Path, ...]:
    dependency_paths = list(build_development_dependency_paths(root, candidate))
    dependency_paths.append(Path("tools/build_codemaker.py"))
    return tuple(dict.fromkeys(dependency_paths))


def load_development_meta_payload(root: Path) -> dict[str, object] | None:
    root = root.resolve()
    meta_path = root / DEVELOPMENT_META_FILE
    if not meta_path.is_file():
        return None
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{meta_path} must contain a JSON object")
    return data


def load_development_meta(root: Path, *, validate_hashes: bool = False) -> list[str]:
    root = root.resolve()
    meta_path = root / DEVELOPMENT_META_FILE
    data = load_development_meta_payload(root)
    if data is None:
        return []
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError(f"{meta_path} must contain a JSON object with a 'changes' list")

    if validate_hashes:
        main_path = root / "main.py"
        preview_path = root / "main_development.py"
        base_resource_path = root / "assets" / "blockquest.pyxres"
        uses_preview_code = bool(data.get("uses_preview_code", True))
        uses_imported_resource = bool(data.get("uses_imported_resource", False))
        base_production_hash = str(data.get("base_production_hash", ""))
        development_hash = str(data.get("development_hash", ""))
        base_resource_hash = str(data.get("base_resource_hash", ""))
        development_resource_hash = str(data.get("development_resource_hash", ""))
        if not base_production_hash or not development_hash or not base_resource_hash or not development_resource_hash:
            raise ValueError(f"{meta_path} must contain 本番/開発版の code と resource のハッシュ")
        if base_production_hash != file_sha256(main_path):
            raise ValueError(f"{meta_path} no longer matches main.py")
        if base_resource_hash != file_sha256(base_resource_path):
            raise ValueError(f"{meta_path} no longer matches assets/blockquest.pyxres")

        expected_main = preview_path if uses_preview_code else main_path
        if not expected_main.is_file() or development_hash != file_sha256(expected_main):
            raise ValueError(f"{meta_path} no longer matches development code source")

        if uses_imported_resource:
            imported_resource = get_imported_resource_path(root)
            if imported_resource is None or development_resource_hash != file_sha256(imported_resource):
                raise ValueError(f"{meta_path} no longer matches imported resource")
        elif development_resource_hash != file_sha256(base_resource_path):
            raise ValueError(f"{meta_path} no longer matches development resource source")

    return [str(change) for change in changes]


def write_development_meta(root: Path, candidate: DevelopmentCandidate) -> Path:
    root = root.resolve()
    main_path = root / "main.py"
    resource_path = root / "assets" / "blockquest.pyxres"
    meta_path = root / DEVELOPMENT_META_FILE
    payload = {
        "base_production_hash": file_sha256(main_path),
        "development_hash": file_sha256(candidate.main_source),
        "base_resource_hash": file_sha256(resource_path),
        "development_resource_hash": file_sha256(candidate.resource_source),
        "uses_preview_code": candidate.uses_preview_code,
        "uses_imported_resource": candidate.uses_imported_resource,
        "changes": candidate.changes,
    }
    meta_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return meta_path
