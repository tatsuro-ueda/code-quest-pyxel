from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


RELEASE_FILES = (
    Path("main.py"),
    Path("assets/umplus_j10r.bdf"),
    Path("assets/blockquest.pyxres"),
)
RELEASE_DIRS = ()
TOP_CHANGES_FILE = Path("top_changes.json")
NORMAL_CHANGE_LIST_DEPENDENCIES = RELEASE_FILES + (
    Path("templates/wrapper.html"),
    Path("templates/selector.html"),
)
PREVIEW_CHANGE_LIST_DEPENDENCIES = (
    Path("main_preview.py"),
    Path("templates/wrapper.html"),
    Path("templates/selector.html"),
)
PREVIEW_OUTPUT_FILES = (
    Path("play-preview.html"),
    Path("pyxel-preview.html"),
)
PREVIEW_META_FILE = Path("preview_meta.json")
PREVIEW_SNAPSHOT_FILE = Path(".preview_snapshot.py")
STEERING_NOTES_DIR = Path("docs/steering")
STEERING_TEMPLATE_NOTE = STEERING_NOTES_DIR / "_template.md"
PREVIEW_AUTO_CHANGE_RULES = (
    ("つうしんとうの ノイズガーディアンが フィールドに でない", ("is_noise_guardian",)),
    ("まおうを たおしたあとも つづきに すすめる", ("dungeon.glitch.exit", "callback=None")),
)


def collect_release_paths(root: Path) -> list[Path]:
    root = root.resolve()
    release_paths: set[Path] = set()

    for rel_path in RELEASE_FILES:
        if (root / rel_path).is_file():
            release_paths.add(rel_path)

    for rel_path in RELEASE_DIRS:
        for path in (root / rel_path).rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            release_paths.add(path.relative_to(root))

    return sorted(release_paths, key=lambda path: path.as_posix())


def stage_release(root: Path, stage_dir: Path) -> list[Path]:
    root = root.resolve()
    if stage_dir.exists():
        shutil.rmtree(stage_dir)
    stage_dir.mkdir(parents=True, exist_ok=True)

    copied_paths = collect_release_paths(root)
    for rel_path in copied_paths:
        src = root / rel_path
        dst = stage_dir / rel_path
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return copied_paths


def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _is_git_dirty(root: Path, rel_path: Path) -> bool:
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


def _revision_timestamp(root: Path, rel_path: Path) -> float:
    path = root / rel_path
    if not path.exists():
        return 0.0

    git_dir = root / ".git"
    if git_dir.exists():
        if _is_git_dirty(root, rel_path):
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


def _parse_task_note_frontmatter(path: Path) -> tuple[str, list[str]]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return "", []

    status = ""
    tags: list[str] = []
    in_tags = False
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            break
        if stripped.startswith("status:"):
            status = stripped.split(":", 1)[1].strip()
            in_tags = False
            continue
        if stripped == "tags:":
            in_tags = True
            continue
        if in_tags and stripped.startswith("- "):
            tags.append(stripped[2:].strip())
            continue
        if in_tags and stripped and not line.startswith(" "):
            in_tags = False

    return status, tags


def find_open_preview_request_notes(root: Path) -> list[Path]:
    root = root.resolve()
    notes_dir = root / STEERING_NOTES_DIR
    if not notes_dir.is_dir():
        return []

    notes: list[Path] = []
    for path in sorted(notes_dir.glob("*.md")):
        if path == root / STEERING_TEMPLATE_NOTE:
            continue
        status, tags = _parse_task_note_frontmatter(path)
        if status != "open":
            continue
        if "preview" not in tags:
            continue
        notes.append(path)
    return notes


def resolve_active_preview_request(root: Path) -> tuple[Path, str]:
    root = root.resolve()
    notes = find_open_preview_request_notes(root)
    if len(notes) != 1:
        raise ValueError(
            "Expected exactly one open preview task note in docs/steering/ with a 'preview' tag."
        )
    note_path = notes[0]
    return note_path.relative_to(root), _file_sha256(note_path)


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
    if _is_git_dirty(root, changes_rel_path):
        return

    changes_timestamp = _revision_timestamp(root, changes_rel_path)
    for dependency in dependency_paths:
        dependency_path = root / dependency
        if not dependency_path.exists():
            continue
        dependency_timestamp = _revision_timestamp(root, dependency)
        if dependency_timestamp > changes_timestamp:
            raise ValueError(
                f"{changes_rel_path} is older than {dependency}. "
                "Update the change list so selector text matches the shipped content."
            )


def build_cache_token(root: Path, dependency_paths: tuple[Path, ...]) -> str:
    root = root.resolve()
    timestamps = [
        _revision_timestamp(root, dependency)
        for dependency in dependency_paths
        if (root / dependency).exists()
    ]
    if not timestamps:
        return "0"
    return str(int(max(timestamps)))


def versioned_asset_url(path: str, token: str) -> str:
    return f"{path}?v={token}" if token else path


def build_preview_change_list(root: Path) -> list[str]:
    root = root.resolve()
    main_path = root / "main.py"
    preview_path = root / "main_preview.py"
    if not main_path.is_file():
        raise FileNotFoundError(f"main.py not found at {main_path}")
    if not preview_path.is_file():
        raise FileNotFoundError(f"main_preview.py not found at {preview_path}")

    main_text = main_path.read_text(encoding="utf-8")
    preview_text = preview_path.read_text(encoding="utf-8")
    if main_text == preview_text:
        raise ValueError("main_preview.py must contain at least one preview-only change")

    diff_lines = list(
        difflib.unified_diff(
            main_text.splitlines(),
            preview_text.splitlines(),
            fromfile="main.py",
            tofile="main_preview.py",
            lineterm="",
        )
    )
    changed_text = "\n".join(
        line[1:]
        for line in diff_lines
        if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))
    )

    changes: list[str] = []
    for message, markers in PREVIEW_AUTO_CHANGE_RULES:
        if all(marker in changed_text for marker in markers):
            changes.append(message)

    if not changes:
        changes.append("おためしばんの ないようを こうしん")

    # Preserve order while removing duplicates.
    return list(dict.fromkeys(changes))


def load_preview_meta_payload(root: Path) -> dict[str, object] | None:
    root = root.resolve()
    meta_path = root / PREVIEW_META_FILE
    if not meta_path.is_file():
        return None
    data = json.loads(meta_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{meta_path} must contain a JSON object")
    return data


def load_preview_meta(root: Path, *, validate_hashes: bool = False) -> list[str]:
    root = root.resolve()
    meta_path = root / PREVIEW_META_FILE
    data = load_preview_meta_payload(root)
    if data is None:
        return []
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError(
            f"{meta_path} must contain a JSON object with a 'changes' list"
        )
    if validate_hashes:
        main_path = root / "main.py"
        preview_path = root / "main_preview.py"
        base_current_hash = str(data.get("base_current_hash", ""))
        preview_hash = str(data.get("preview_hash", ""))
        request_note_path = str(data.get("request_note_path", ""))
        if not base_current_hash or not preview_hash:
            raise ValueError(f"{meta_path} must contain current and preview hashes")
        if not request_note_path:
            raise ValueError(f"{meta_path} must contain preview request note metadata")
        if main_path.is_file() and base_current_hash != _file_sha256(main_path):
            raise ValueError(f"{meta_path} no longer matches main.py")
        if preview_path.is_file() and preview_hash != _file_sha256(preview_path):
            raise ValueError(f"{meta_path} no longer matches main_preview.py")
        current_request_path, _current_request_hash = resolve_active_preview_request(root)
        if request_note_path != current_request_path.as_posix():
            raise ValueError(f"{meta_path} no longer matches the current preview task note")
    return [str(change) for change in changes]


def write_preview_snapshot(root: Path) -> Path:
    root = root.resolve()
    preview_path = root / "main_preview.py"
    snapshot_path = root / PREVIEW_SNAPSHOT_FILE
    shutil.copy2(preview_path, snapshot_path)
    return snapshot_path


def roll_forward_approved_preview(root: Path) -> bool:
    root = root.resolve()
    data = load_preview_meta_payload(root)
    if data is None:
        return False

    request_note_path = str(data.get("request_note_path", ""))
    request_note_hash = str(data.get("request_note_hash", ""))
    if not request_note_path or not request_note_hash:
        return False

    current_request_path, _current_request_hash = resolve_active_preview_request(root)
    if request_note_path == current_request_path.as_posix():
        return False

    snapshot_path = root / PREVIEW_SNAPSHOT_FILE
    if not snapshot_path.is_file():
        raise ValueError(f"Cannot roll forward previous preview without {snapshot_path}")

    preview_hash = str(data.get("preview_hash", ""))
    if preview_hash and _file_sha256(snapshot_path) != preview_hash:
        raise ValueError(f"{snapshot_path} no longer matches preview_meta.json")

    shutil.copy2(snapshot_path, root / "main.py")
    (root / PREVIEW_META_FILE).unlink()
    return True


def write_preview_meta(root: Path, changes: list[str]) -> Path:
    root = root.resolve()
    main_path = root / "main.py"
    preview_path = root / "main_preview.py"
    meta_path = root / PREVIEW_META_FILE
    request_note_path, request_note_hash = resolve_active_preview_request(root)
    payload = {
        "base_current_hash": _file_sha256(main_path),
        "preview_hash": _file_sha256(preview_path),
        "request_note_path": request_note_path.as_posix(),
        "request_note_hash": request_note_hash,
        "changes": changes,
    }
    meta_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return meta_path


def resolve_pyxel_command(root: Path) -> list[str]:
    root = root.resolve()
    venv_python = root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return [str(venv_python), "-m", "pyxel"]
    try:
        pyxel_spec = importlib.util.find_spec("pyxel")
    except ValueError:
        pyxel_spec = None
    if pyxel_spec is not None:
        return [sys.executable, "-m", "pyxel"]
    pyxel_cli = shutil.which("pyxel")
    if pyxel_cli:
        return [pyxel_cli]
    raise FileNotFoundError("Unable to find a Pyxel CLI or Python environment with Pyxel")


def generate_wrapper(
    build_dir: Path,
    project_root: Path,
    pyxel_html_name: str = "pyxel.html",
    *,
    page_kind: str = "current",
    session_api_base: str = "/internal/play-sessions",
) -> Path:
    """カスタムHTMLラッパーを生成する"""
    template_path = project_root / "templates" / "wrapper.html"
    template = template_path.read_text(encoding="utf-8")
    wrapper_html = (
        template
        .replace("{{PYXEL_HTML_SRC}}", pyxel_html_name)
        .replace("{{PAGE_KIND}}", page_kind)
        .replace("{{SESSION_API_BASE}}", session_api_base)
    )
    output_path = build_dir / "index.html"
    output_path.write_text(wrapper_html, encoding="utf-8")
    return output_path


def build_web_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    root = root.resolve()
    output_dir = output_dir.resolve() if output_dir else root
    work_dir = work_dir.resolve() if work_dir else (root / ".build" / "web_release")
    app_dir = work_dir / "app"
    app_name = app_dir.name
    pyxel_command = resolve_pyxel_command(root)
    current_token = build_cache_token(root, NORMAL_CHANGE_LIST_DEPENDENCIES)

    stage_release(root, app_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(
        [*pyxel_command, "package", app_dir.name, f"{app_dir.name}/main.py"],
        cwd=work_dir,
        check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{app_name}.pyxapp"],
        cwd=work_dir,
        check=True,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    pyxapp_path = output_dir / "pyxel.pyxapp"
    html_path = output_dir / "pyxel.html"
    shutil.copy2(work_dir / f"{app_name}.pyxapp", pyxapp_path)
    shutil.copy2(work_dir / f"{app_name}.html", html_path)

    # カスタムHTMLラッパー生成 → play.html に保存
    wrapper_path = generate_wrapper(
        work_dir,
        root,
        pyxel_html_name=versioned_asset_url("pyxel.html", current_token),
        page_kind="current",
    )
    play_path = output_dir / "play.html"
    shutil.copy2(wrapper_path, play_path)

    preview_wrapper_name = ""
    if not preview_outputs_are_available(root, output_dir):
        prune_preview_outputs(output_dir)
    else:
        preview_dependencies = PREVIEW_CHANGE_LIST_DEPENDENCIES
        if (root / PREVIEW_META_FILE).is_file():
            preview_dependencies = PREVIEW_CHANGE_LIST_DEPENDENCIES + (PREVIEW_META_FILE,)
        preview_token = build_cache_token(root, preview_dependencies)
        preview_wrapper_name = versioned_asset_url("play-preview.html", preview_token)

    # トップ画面は source of truth から毎回再生成する
    index_path = output_dir / "index.html"
    selector_path = generate_top_selector(
        work_dir,
        root,
        current_wrapper_name=versioned_asset_url("play.html", current_token),
        preview_wrapper_name=preview_wrapper_name,
    )
    shutil.copy2(selector_path, index_path)

    return pyxapp_path, html_path, play_path


def generate_selector(
    build_dir: Path,
    project_root: Path,
    *,
    current_wrapper_name: str = "play.html",
    preview_wrapper_name: str = "play-preview.html",
    changes: list[str] | None = None,
    current_changes: list[str] | None = None,
) -> Path:
    """選択ページ（selector.html）を生成する"""
    template_path = project_root / "templates" / "selector.html"
    template = template_path.read_text(encoding="utf-8")
    if preview_wrapper_name:
        if changes:
            change_list = "\n".join(f"      <li>{c}</li>" for c in changes)
        else:
            change_list = ""
        preview_card = (
            '  <div class="version-card">\n'
            '    <h2>おためしばん</h2>\n'
            '    <ul class="changes">\n'
            f"{change_list}\n"
            '    </ul>\n'
            f'    <a class="play-btn" href="{preview_wrapper_name}">あそんでみる</a>\n'
            "  </div>"
        )
        hint_block = (
            '  <p class="hint">\n'
            "    りょうほう あそんだら<br>\n"
            "    おとうさんに おしえてね！<br>\n"
            '    「こっちが いい！」って\n'
            "  </p>"
        )
    else:
        preview_card = ""
        hint_block = ""
    if current_changes:
        current_card_body = (
            '    <ul class="changes">\n'
            + "\n".join(f"      <li>{c}</li>" for c in current_changes)
            + "\n    </ul>\n"
        )
    else:
        current_card_body = '    <p class="desc">いままでと おなじ</p>\n'
    html = (
        template
        .replace("{{PREVIEW_CARD}}", preview_card)
        .replace("{{HINT_BLOCK}}", hint_block)
        .replace("{{CURRENT_CARD_BODY}}", current_card_body.rstrip())
        .replace("{{CURRENT_WRAPPER_SRC}}", current_wrapper_name)
    )
    output_path = build_dir / "index.html"
    output_path.write_text(html, encoding="utf-8")
    return output_path


def load_top_page_changes(root: Path) -> list[str]:
    """normal build 用のトップ画面変更点を読み込む。"""
    root = root.resolve()
    changes_path = root / TOP_CHANGES_FILE
    if not changes_path.is_file():
        return []
    validate_change_list_freshness(
        root,
        changes_rel_path=TOP_CHANGES_FILE,
        dependency_paths=NORMAL_CHANGE_LIST_DEPENDENCIES,
    )
    data = json.loads(changes_path.read_text(encoding="utf-8"))
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        raise ValueError(
            f"{changes_path} must contain a JSON object with a 'changes' list"
        )
    return [str(change) for change in changes]


def generate_top_selector(
    build_dir: Path,
    project_root: Path,
    *,
    current_wrapper_name: str = "play.html",
    preview_wrapper_name: str = "play-preview.html",
) -> Path:
    """トップ画面用 JSON を読んで selector を生成する。"""
    current_changes = load_top_page_changes(project_root)
    changes = load_preview_meta(project_root) if preview_wrapper_name else []
    return generate_selector(
        build_dir,
        project_root,
        current_wrapper_name=current_wrapper_name,
        preview_wrapper_name=preview_wrapper_name,
        changes=changes,
        current_changes=current_changes,
    )


def preview_outputs_are_available(root: Path, output_dir: Path) -> bool:
    """通常 build で preview を露出してよいか判定する。"""
    root = root.resolve()
    output_dir = output_dir.resolve()
    preview_py = root / "main_preview.py"
    if not preview_py.is_file():
        return False
    if not (root / PREVIEW_META_FILE).is_file():
        return False

    output_paths = [output_dir / rel_path for rel_path in PREVIEW_OUTPUT_FILES]
    if not all(path.is_file() for path in output_paths):
        return False

    try:
        load_preview_meta(root, validate_hashes=True)
    except ValueError:
        return False

    dependencies = [
        Path("main_preview.py"),
        Path("templates/wrapper.html"),
        Path("templates/selector.html"),
    ]
    dependencies.append(Path("preview_meta.json"))

    newest_dependency = max(_revision_timestamp(root, rel_path) for rel_path in dependencies)
    oldest_output = min(path.stat().st_mtime for path in output_paths)
    return oldest_output >= newest_dependency


def prune_preview_outputs(output_dir: Path) -> None:
    """preview source がない時に stale preview 配信物を消す。"""
    output_dir = output_dir.resolve()
    for rel_path in PREVIEW_OUTPUT_FILES:
        path = output_dir / rel_path
        if path.exists():
            path.unlink()


def validate_preview_files(root: Path) -> tuple[Path, list[str]]:
    """--preview に必要なファイルを検証し、変更リストを返す"""
    root = root.resolve()
    preview_py = root / "main_preview.py"
    if not preview_py.is_file():
        raise FileNotFoundError(
            f"main_preview.py not found at {preview_py}. "
            "Create it before running --preview."
        )
    changes = build_preview_change_list(root)
    return preview_py, changes


def promote(root: Path, *, choice: str) -> None:
    """おためし版を昇格、またはもとのまま版を維持する"""
    root = root.resolve()
    main_py = root / "main.py"
    preview_py = root / "main_preview.py"
    meta_json = root / "preview_meta.json"
    snapshot_py = root / PREVIEW_SNAPSHOT_FILE

    if choice == "preview":
        if preview_py.is_file():
            shutil.copy2(preview_py, main_py)
            preview_py.unlink()
    elif choice == "current":
        pass  # main.py はそのまま
    else:
        raise ValueError(f"Unknown promote choice: {choice!r}. Use 'preview' or 'current'.")

    # クリーンアップ
    if preview_py.is_file():
        preview_py.unlink()
    if meta_json.is_file():
        meta_json.unlink()
    if snapshot_py.is_file():
        snapshot_py.unlink()


def build_preview_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path, Path]:
    """2版ビルド: もとのまま版 + おためし版 + 選択ページ"""
    root = root.resolve()
    roll_forward_approved_preview(root)
    preview_py, changes = validate_preview_files(root)
    preview_meta_path = write_preview_meta(root, changes)
    write_preview_snapshot(root)
    output_dir = output_dir.resolve() if output_dir else root
    work_dir = work_dir.resolve() if work_dir else (root / ".build" / "web_release")
    pyxel_command = resolve_pyxel_command(root)
    current_token = build_cache_token(root, NORMAL_CHANGE_LIST_DEPENDENCIES)
    preview_dependencies = PREVIEW_CHANGE_LIST_DEPENDENCIES + (PREVIEW_META_FILE,)
    preview_token = build_cache_token(root, preview_dependencies)

    # --- もとのまま版 ---
    app_dir = work_dir / "app"
    stage_release(root, app_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    app_name = app_dir.name
    subprocess.run(
        [*pyxel_command, "package", app_name, f"{app_name}/main.py"],
        cwd=work_dir, check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{app_name}.pyxapp"],
        cwd=work_dir, check=True,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "pyxel.html"
    shutil.copy2(work_dir / f"{app_name}.html", html_path)

    # --- おためし版 ---
    preview_app_dir = work_dir / "app_preview"
    stage_release(root, preview_app_dir)
    # main.py をおためし版で上書き
    shutil.copy2(preview_py, preview_app_dir / "main.py")
    preview_app_name = preview_app_dir.name
    subprocess.run(
        [*pyxel_command, "package", preview_app_name, f"{preview_app_name}/main.py"],
        cwd=work_dir, check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{preview_app_name}.pyxapp"],
        cwd=work_dir, check=True,
    )
    preview_html_path = output_dir / "pyxel-preview.html"
    shutil.copy2(work_dir / f"{preview_app_name}.html", preview_html_path)

    # --- ラッパーHTML（iframe + 全画面ボタン）を2つ生成 ---
    current_wrapper = generate_wrapper(
        work_dir,
        root,
        pyxel_html_name=versioned_asset_url("pyxel.html", current_token),
        page_kind="current",
    )
    play_path = output_dir / "play.html"
    shutil.copy2(current_wrapper, play_path)

    preview_wrapper_dir = work_dir / "preview_wrapper"
    preview_wrapper_dir.mkdir(parents=True, exist_ok=True)
    preview_wrapper = generate_wrapper(
        preview_wrapper_dir,
        root,
        pyxel_html_name=versioned_asset_url("pyxel-preview.html", preview_token),
        page_kind="preview",
    )
    play_preview_path = output_dir / "play-preview.html"
    shutil.copy2(preview_wrapper, play_preview_path)

    # --- 選択ページ ---
    selector_path = generate_selector(
        work_dir, root,
        current_wrapper_name=versioned_asset_url("play.html", current_token),
        preview_wrapper_name=versioned_asset_url("play-preview.html", preview_token),
        changes=changes,
    )
    index_path = output_dir / "index.html"
    shutil.copy2(selector_path, index_path)

    # Keep the generated selector source of truth in sync with the build inputs.
    if not preview_meta_path.exists():
        raise FileNotFoundError(f"Failed to generate {preview_meta_path}")

    return html_path, preview_html_path, index_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Block Quest web release")
    parser.add_argument("--preview", action="store_true",
                        help="Build 2-version preview (requires main_preview.py)")
    parser.add_argument("--promote", choices=["preview", "current"],
                        help="Promote preview or keep current, then clean up")
    args = parser.parse_args()

    if args.promote:
        promote(ROOT, choice=args.promote)
        print(f"Promoted '{args.promote}'. Running normal build...")
        build_web_release(ROOT)
    elif args.preview:
        html, preview_html, index = build_preview_release(ROOT)
        print(f"Preview build complete:\n  {html}\n  {preview_html}\n  {index}")
    else:
        build_web_release(ROOT)


if __name__ == "__main__":
    main()
