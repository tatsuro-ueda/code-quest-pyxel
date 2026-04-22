from __future__ import annotations

import argparse
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.shared.services.codemaker_resource_store import (  # noqa: E402
    clear_imported_resource,
    get_imported_resource_path,
    promote_imported_resource,
)
from tools.build_release_artifacts import (  # noqa: E402
    CODEMAKER_OUTPUT_FILE,
    DEVELOPMENT_ARTIFACT_FILES,
    DEVELOPMENT_CODEMAKER_OUTPUT_FILE,
    DEVELOPMENT_DIR,
    DEVELOPMENT_HTML_FILE,
    DEVELOPMENT_INDEX_FILE,
    DEVELOPMENT_OUTPUT_FILES,
    DEVELOPMENT_PLAY_FILE,
    DEVELOPMENT_PYXAPP_FILE,
    PRODUCTION_DIR,
    PRODUCTION_HTML_FILE,
    PRODUCTION_INDEX_FILE,
    PRODUCTION_PLAY_FILE,
    PRODUCTION_PYXAPP_FILE,
    apply_stage_overrides,
    build_codemaker_release,
    collect_release_paths,
    development_output_dir,
    production_output_dir,
    prune_development_outputs,
    prune_legacy_root_outputs,
    stage_release,
    write_wrapper_outputs,
)
from tools.render_release_selector import (  # noqa: E402
    NORMAL_CHANGE_LIST_DEPENDENCIES,
    generate_selector,
    generate_top_selector,
    generate_wrapper,
    load_top_page_changes,
    versioned_asset_url,
)
from tools.resolve_release_source_of_truth import (  # noqa: E402
    DEVELOPMENT_META_FILE,
    DevelopmentCandidate,
    build_cache_token,
    build_development_codemaker_dependency_paths,
    build_development_dependency_paths,
    load_development_meta,
    resolve_development_candidate,
    revision_timestamp,
    write_development_meta,
)


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
    import_check = subprocess.run(
        [sys.executable, "-c", "import pyxel"],
        cwd=root,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    if import_check.returncode == 0:
        return [sys.executable, "-m", "pyxel"]
    pyxel_cli = shutil.which("pyxel")
    if pyxel_cli:
        return [pyxel_cli]
    raise FileNotFoundError("Unable to find a Pyxel CLI or Python environment with Pyxel")


def development_outputs_are_available(root: Path, output_dir: Path) -> bool:
    root = root.resolve()
    output_dir = output_dir.resolve()
    if not (root / DEVELOPMENT_META_FILE).is_file():
        return False

    output_paths = [output_dir / rel_path for rel_path in DEVELOPMENT_OUTPUT_FILES]
    if not all(path.is_file() for path in output_paths):
        return False

    try:
        load_development_meta(root, validate_hashes=True)
        candidate = resolve_development_candidate(root)
    except ValueError:
        return False

    dependencies = build_development_dependency_paths(root, candidate)
    newest_dependency = max(revision_timestamp(root, rel_path) for rel_path in dependencies)
    oldest_output = min(path.stat().st_mtime for path in output_paths)
    return oldest_output >= newest_dependency


def development_codemaker_zip_is_available(root: Path, output_dir: Path) -> bool:
    root = root.resolve()
    output_dir = output_dir.resolve()
    if not development_outputs_are_available(root, output_dir):
        return False

    preview_zip = output_dir / DEVELOPMENT_CODEMAKER_OUTPUT_FILE
    if not preview_zip.is_file():
        return False

    try:
        candidate = resolve_development_candidate(root)
    except ValueError:
        return False

    dependencies = build_development_codemaker_dependency_paths(root, candidate)
    newest_dependency = max(revision_timestamp(root, rel_path) for rel_path in dependencies)
    return preview_zip.stat().st_mtime >= newest_dependency


def validate_development_files(root: Path) -> tuple[Path, list[str]]:
    root = root.resolve()
    preview_py = root / "main_development.py"
    imported_resource = get_imported_resource_path(root)
    if not preview_py.is_file() and imported_resource is None:
        raise FileNotFoundError(
            f"main_development.py not found at {preview_py}. "
            "Create it or import a Code Maker resource before running --development."
        )
    candidate = resolve_development_candidate(root)
    return candidate.main_source, candidate.changes


def promote(root: Path, *, choice: str) -> None:
    root = root.resolve()
    main_py = root / "main.py"
    preview_py = root / "main_development.py"
    meta_json = root / DEVELOPMENT_META_FILE

    if choice == "development":
        if preview_py.is_file():
            shutil.copy2(preview_py, main_py)
            preview_py.unlink()
        promote_imported_resource(root)
    elif choice == "production":
        clear_imported_resource(root)
    else:
        raise ValueError(f"Unknown promote choice: {choice!r}. Use 'development' or 'production'.")

    if preview_py.is_file():
        preview_py.unlink()
    if meta_json.is_file():
        meta_json.unlink()


def approve_development(root: Path, *, output_dir: Path | None = None, work_dir: Path | None = None) -> None:
    promote(root, choice="development")
    build_web_release(root, output_dir=output_dir, work_dir=work_dir)


def reject_development(root: Path, *, output_dir: Path | None = None, work_dir: Path | None = None) -> None:
    promote(root, choice="production")
    build_web_release(root, output_dir=output_dir, work_dir=work_dir)


def build_web_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path]:
    root = root.resolve()
    output_dir = output_dir.resolve() if output_dir else root
    production_dir = production_output_dir(output_dir)
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
    production_dir.mkdir(parents=True, exist_ok=True)
    prune_legacy_root_outputs(output_dir)
    pyxapp_path = output_dir / PRODUCTION_PYXAPP_FILE
    html_path = output_dir / PRODUCTION_HTML_FILE
    shutil.copy2(work_dir / f"{app_name}.pyxapp", pyxapp_path)
    shutil.copy2(work_dir / f"{app_name}.html", html_path)
    build_codemaker_release(
        root,
        main_source=root / "main.py",
        resource_source=root / "assets" / "blockquest.pyxres",
        output_path=output_dir / CODEMAKER_OUTPUT_FILE,
    )

    wrapper_path = generate_wrapper(
        work_dir,
        root,
        pyxel_html_name=versioned_asset_url("pyxel.html", current_token),
        page_kind="production",
    )
    play_path, _ = write_wrapper_outputs(wrapper_path, production_dir)

    preview_wrapper_name = ""
    preview_zip_name = ""
    if not development_outputs_are_available(root, output_dir):
        prune_development_outputs(output_dir)
    else:
        candidate = resolve_development_candidate(root)
        preview_dependencies = build_development_dependency_paths(root, candidate)
        preview_token = build_cache_token(root, preview_dependencies)
        preview_wrapper_name = versioned_asset_url("development/play.html", preview_token)
        if development_codemaker_zip_is_available(root, output_dir):
            preview_codemaker_token = build_cache_token(
                root,
                build_development_codemaker_dependency_paths(root, candidate),
            )
            preview_zip_name = versioned_asset_url(
                DEVELOPMENT_CODEMAKER_OUTPUT_FILE.as_posix(),
                preview_codemaker_token,
            )

    index_path = output_dir / "index.html"
    selector_path = generate_top_selector(
        work_dir,
        root,
        current_wrapper_name=versioned_asset_url("production/play.html", current_token),
        preview_wrapper_name=preview_wrapper_name,
        preview_zip_name=preview_zip_name,
    )
    shutil.copy2(selector_path, index_path)

    return pyxapp_path, html_path, play_path


def build_development_release(
    root: Path,
    *,
    output_dir: Path | None = None,
    work_dir: Path | None = None,
) -> tuple[Path, Path, Path, Path]:
    root = root.resolve()
    candidate = resolve_development_candidate(root)
    preview_meta_path = write_development_meta(root, candidate)
    output_dir = output_dir.resolve() if output_dir else root
    production_dir = production_output_dir(output_dir)
    development_dir = development_output_dir(output_dir)
    work_dir = work_dir.resolve() if work_dir else (root / ".build" / "web_release")
    pyxel_command = resolve_pyxel_command(root)
    current_token = build_cache_token(root, NORMAL_CHANGE_LIST_DEPENDENCIES)
    preview_dependencies = build_development_dependency_paths(root, candidate)
    preview_token = build_cache_token(root, preview_dependencies)
    preview_codemaker_token = build_cache_token(
        root,
        build_development_codemaker_dependency_paths(root, candidate),
    )
    prune_legacy_root_outputs(output_dir)

    app_dir = work_dir / "app"
    stage_release(root, app_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    app_name = app_dir.name
    subprocess.run(
        [*pyxel_command, "package", app_name, f"{app_name}/main.py"],
        cwd=work_dir,
        check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{app_name}.pyxapp"],
        cwd=work_dir,
        check=True,
    )
    output_dir.mkdir(parents=True, exist_ok=True)
    production_dir.mkdir(parents=True, exist_ok=True)
    development_dir.mkdir(parents=True, exist_ok=True)
    pyxapp_path = output_dir / PRODUCTION_PYXAPP_FILE
    html_path = output_dir / PRODUCTION_HTML_FILE
    shutil.copy2(work_dir / f"{app_name}.pyxapp", pyxapp_path)
    shutil.copy2(work_dir / f"{app_name}.html", html_path)
    build_codemaker_release(
        root,
        main_source=root / "main.py",
        resource_source=root / "assets" / "blockquest.pyxres",
        output_path=output_dir / CODEMAKER_OUTPUT_FILE,
    )

    preview_app_dir = work_dir / "app_preview"
    stage_release(root, preview_app_dir)
    apply_stage_overrides(
        preview_app_dir,
        main_source=candidate.main_source,
        resource_source=candidate.resource_source,
    )
    preview_app_name = preview_app_dir.name
    subprocess.run(
        [*pyxel_command, "package", preview_app_name, f"{preview_app_name}/main.py"],
        cwd=work_dir,
        check=True,
    )
    subprocess.run(
        [*pyxel_command, "app2html", f"{preview_app_name}.pyxapp"],
        cwd=work_dir,
        check=True,
    )
    preview_pyxapp_path = output_dir / DEVELOPMENT_PYXAPP_FILE
    preview_html_path = output_dir / DEVELOPMENT_HTML_FILE
    shutil.copy2(work_dir / f"{preview_app_name}.pyxapp", preview_pyxapp_path)
    shutil.copy2(work_dir / f"{preview_app_name}.html", preview_html_path)
    build_codemaker_release(
        root,
        main_source=candidate.main_source,
        resource_source=candidate.resource_source,
        output_path=output_dir / DEVELOPMENT_CODEMAKER_OUTPUT_FILE,
    )

    current_wrapper = generate_wrapper(
        work_dir,
        root,
        pyxel_html_name=versioned_asset_url("pyxel.html", current_token),
        page_kind="production",
    )
    play_path, _ = write_wrapper_outputs(current_wrapper, production_dir)

    preview_wrapper_dir = work_dir / "preview_wrapper"
    preview_wrapper_dir.mkdir(parents=True, exist_ok=True)
    preview_wrapper = generate_wrapper(
        preview_wrapper_dir,
        root,
        pyxel_html_name=versioned_asset_url("pyxel.html", preview_token),
        page_kind="development",
    )
    play_preview_path, _ = write_wrapper_outputs(preview_wrapper, development_dir)

    selector_path = generate_selector(
        work_dir,
        root,
        current_wrapper_name=versioned_asset_url("production/play.html", current_token),
        preview_wrapper_name=versioned_asset_url("development/play.html", preview_token),
        preview_zip_name=versioned_asset_url(
            DEVELOPMENT_CODEMAKER_OUTPUT_FILE.as_posix(),
            preview_codemaker_token,
        ),
        changes=candidate.changes,
    )
    index_path = output_dir / "index.html"
    shutil.copy2(selector_path, index_path)

    if not preview_meta_path.exists():
        raise FileNotFoundError(f"Failed to generate {preview_meta_path}")

    return html_path, preview_html_path, index_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Block Quest Web release")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--development",
        action="store_true",
        help="本番 + 開発版をビルドする（main_development.py が必要）",
    )
    group.add_argument(
        "--approve-development",
        action="store_true",
        help="開発版を本番へ昇格し、本番を再ビルドして開発版入力を掃除する",
    )
    group.add_argument(
        "--reject-development",
        action="store_true",
        help="開発版を却下し、本番を維持したまま開発版入力を掃除する",
    )
    args = parser.parse_args()

    if args.approve_development:
        approve_development(ROOT)
        print("開発版を承認し、本番を再ビルドしました。")
    elif args.reject_development:
        reject_development(ROOT)
        print("開発版を却下し、本番を再ビルドしました。")
    elif args.development:
        html, preview_html, index = build_development_release(ROOT)
        print(f"開発版ビルド完了:\n  {html}\n  {preview_html}\n  {index}")
    else:
        build_web_release(ROOT)


if __name__ == "__main__":
    main()
