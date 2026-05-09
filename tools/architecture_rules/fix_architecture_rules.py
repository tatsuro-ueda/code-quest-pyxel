from __future__ import annotations

"""architecture rule warning に対して一度だけ deterministic fix を適用する。"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from . import check_architecture_rules


ROOT = Path(__file__).resolve().parents[2]

CANONICAL_MAIN_WRAPPER = """from pathlib import Path


_RUNTIME_PATH = Path(__file__).resolve().parent / "src" / "runtime" / "main_runtime.py"
exec(compile(_RUNTIME_PATH.read_text(encoding="utf-8"), str(_RUNTIME_PATH), "exec"), globals())

if __name__ == "__main__":
    run()
"""

ENTRY_POINT_MARKER = "# =====================================================================\n# ENTRY POINT\n# =====================================================================\n"
CANONICAL_RUNTIME_TAIL = """# =====================================================================
# ENTRY POINT
# =====================================================================
def run():
    \"\"\"Block Quest の entry point。Game を生成して pyxel.run に入る。\"\"\"
    return _run()
"""


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


class _ReadableYamlDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, False)


def _format_yaml_for_humans(data: dict[str, Any]) -> str:
    dumped = yaml.dump(
        data,
        Dumper=_ReadableYamlDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=88,
    )
    major_fact_keys = {
        "  tree:",
        "  flows:",
        "  entry_points:",
        "  runbooks:",
        "  migration_notes:",
    }
    formatted: list[str] = []
    for raw_line in dumped.splitlines():
        line = raw_line.rstrip()
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        needs_separator = False
        if line in {"facts:", "validation_rules:"} or line in major_fact_keys:
            needs_separator = True
        elif stripped.startswith("- path:"):
            needs_separator = True
        elif stripped.startswith("- id:") and indent <= 4:
            needs_separator = True

        if needs_separator and formatted and formatted[-1] != "":
            formatted.append("")
        formatted.append(line)
    return "\n".join(formatted).lstrip("\n") + "\n"


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(_format_yaml_for_humans(data), encoding="utf-8")


def _read_manifest_entries_with_lines(path: Path) -> list[str]:
    return path.read_text(encoding="utf-8").splitlines()


def _write_manifest_lines(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def _find_codemaker_bundle_contract(data: dict[str, Any], contract_id: str) -> dict[str, Any] | None:
    contracts = data.get("facts", {}).get("codemaker_bundle_contracts", [])
    return next((item for item in contracts if item.get("id") == contract_id), None)


def _manifest_entries(lines: list[str]) -> set[str]:
    entries: set[str] = set()
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entries.add(line)
    return entries


def _manifest_insert_before_marker(lines: list[str], path: str, marker: str | None) -> None:
    if marker is None:
        lines.append(path)
        return
    for index, line in enumerate(lines):
        if line.startswith(marker):
            lines.insert(index, path)
            return
    lines.append(path)


def _insert_codemaker_manifest_path(lines: list[str], path: str) -> None:
    if path in {
        "src/shared/services/debug_service.py",
        "src/shared/services/scene_manager.py",
    }:
        _manifest_insert_before_marker(lines, path, "# --- 10. src/runtime/app.py:")
        return
    if path.startswith("src/shared/assets/"):
        _manifest_insert_before_marker(lines, path, "# --- 2. shared/constants:")
        return
    if path.startswith("src/shared/constants/"):
        _manifest_insert_before_marker(lines, path, "# --- 3. src/generated:")
        return
    if path.startswith("src/generated/"):
        _manifest_insert_before_marker(lines, path, "# --- 4. src/game_data.py:")
        return
    if path == "src/game_data.py":
        _manifest_insert_before_marker(lines, path, "# --- 5a. shared/state:")
        return
    if path.startswith("src/shared/state/"):
        _manifest_insert_before_marker(lines, path, "# --- 5. shared/services:")
        return
    if path.startswith("src/shared/services/"):
        _manifest_insert_before_marker(lines, path, "# --- 6. shared/ui:")
        return
    if path.startswith("src/shared/ui/"):
        _manifest_insert_before_marker(lines, path, "# --- 7. scenes:")
        return
    if path == "src/runtime/app.py":
        _manifest_insert_before_marker(lines, path, None)
        return
    _manifest_insert_before_marker(lines, path, None)


def _set_rule_internal_fields(data: dict[str, Any], rules_path: Path) -> None:
    for rule in data.get("validation_rules", []):
        rule["__rules_path"] = str(rules_path)


def _generated_entry_expected_source(entry_path: str) -> str:
    stem = Path(entry_path).stem
    return f"assets/{stem}.yaml"


def ensure_tree_path(root: dict[str, Any], path_value: str, kind: str, **fields: Any) -> dict[str, Any]:
    if path_value == ".":
        root.update(fields)
        return root

    segments = path_value.split("/")
    current = root
    for index, segment in enumerate(segments):
        current_path = "/".join(segments[: index + 1])
        is_last = index == len(segments) - 1
        wanted_kind = kind if is_last else "directory"
        children = current.setdefault("children", [])
        child = next((item for item in children if item.get("path") == current_path), None)
        if child is None:
            child = {"path": current_path, "kind": wanted_kind}
            if wanted_kind != "file":
                child["children"] = []
            children.append(child)
        elif child.get("kind") != wanted_kind:
            child["kind"] = wanted_kind
        current = child
    current.update(fields)
    if current.get("kind") != "file":
        current.setdefault("children", [])
    return current


def fix_generated_files_edit_policy(repo_root: Path, rules_path: Path, warning: dict[str, Any]) -> list[dict[str, Any]]:
    data = load_yaml(rules_path)
    fixes: list[dict[str, Any]] = []
    changed_yaml = False
    tree = data.setdefault("facts", {}).setdefault("tree", {"path": ".", "kind": "root", "children": []})
    entries = check_architecture_rules.generated_file_nodes(data)

    for entry in entries:
        if entry.get("hand_editable") is not False:
            entry["hand_editable"] = False
            changed_yaml = True
            fixes.append({"kind": "yaml", "path": str(rules_path), "detail": f"set hand_editable false for {entry.get('id')}"})
        expected_source = _generated_entry_expected_source(entry["path"])
        generated_from = list(entry.get("generated_from", []))
        if generated_from != [expected_source]:
            entry["generated_from"] = [expected_source]
            changed_yaml = True
            fixes.append({"kind": "yaml", "path": str(rules_path), "detail": f"normalized generated_from for {entry.get('id')}"})

    if changed_yaml:
        write_yaml(rules_path, data)

    gen_script = repo_root / "tools" / "gen_data.py"
    if gen_script.is_file():
        subprocess.run([sys.executable, str(gen_script)], cwd=repo_root, check=True)
        fixes.append({"kind": "command", "path": str(gen_script), "detail": "ran gen_data.py"})
    return fixes


def fix_dist_not_source(repo_root: Path, rules_path: Path, warning: dict[str, Any]) -> list[dict[str, Any]]:
    data = load_yaml(rules_path)
    fixes: list[dict[str, Any]] = []
    changed_yaml = False
    tree = data.setdefault("facts", {}).setdefault("tree", {"path": ".", "kind": "root", "children": []})
    dist_root = ensure_tree_path(
        tree,
        "dist",
        "directory",
        role="distribution_root",
        status="distribution",
        source_of_truth=False,
        summary="承認済み配布物の出力先",
    )
    if dist_root:
        changed_yaml = True
        fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "normalized dist root node"})

    build_script = repo_root / "tools" / "build_web_release.py"
    if build_script.is_file():
        subprocess.run([sys.executable, str(build_script)], cwd=repo_root, check=True)
        fixes.append({"kind": "command", "path": str(build_script), "detail": "rebuilt dist artifacts"})

    if changed_yaml:
        write_yaml(rules_path, data)
    return fixes


def fix_build_runbook_paths(repo_root: Path, rules_path: Path, warning: dict[str, Any]) -> list[dict[str, Any]]:
    data = load_yaml(rules_path)
    fixes: list[dict[str, Any]] = []
    changed_yaml = False
    tree = data.setdefault("facts", {}).setdefault("tree", {"path": ".", "kind": "root", "children": []})
    artifacts = [
        {"id": "codemaker_zip", "path": "dist/code-maker.zip", "status": "distribution", "summary": "block-quest/main.py + my_resource.pyxres を梱包した教材版 zip"},
        {"id": "pyxel_html", "path": "dist/pyxel.html", "status": "distribution", "summary": "Web 配布用 HTML"},
        {"id": "pyxel_pyxapp", "path": "dist/pyxel.pyxapp", "status": "distribution", "summary": "Pyxel app 配布物"},
        {"id": "play_html", "path": "dist/play.html", "status": "distribution", "summary": "プレイページ"},
        {"id": "top_index_html", "path": "dist/index.html", "status": "distribution", "summary": "play.html と同内容の wrapper alias"},
    ]
    for artifact in artifacts:
        ensure_tree_path(
            tree,
            artifact["path"],
            "file",
            id=artifact["id"],
            status=artifact["status"],
            summary=artifact["summary"],
        )
    changed_yaml = True
    fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "normalized distribution artifact nodes"})

    runbooks = data.setdefault("facts", {}).setdefault("runbooks", [])
    for runbook in runbooks:
        if runbook.get("id") == "build_codemaker_zip":
            step = runbook.setdefault("steps", [{}])[0]
            if step.get("command") != "python tools/build_codemaker.py":
                step["command"] = "python tools/build_codemaker.py"
                changed_yaml = True
            if step.get("outputs") != ["dist/code-maker.zip"]:
                step["outputs"] = ["dist/code-maker.zip"]
                changed_yaml = True
        if runbook.get("id") == "build_all_release_artifacts":
            step = runbook.setdefault("steps", [{}])[0]
            desired_outputs = [item["path"] for item in artifacts]
            if step.get("command") != "python tools/build_web_release.py":
                step["command"] = "python tools/build_web_release.py"
                changed_yaml = True
            if step.get("outputs") != desired_outputs:
                step["outputs"] = desired_outputs
                changed_yaml = True
    if changed_yaml:
        write_yaml(rules_path, data)
        fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "normalized runbook outputs"})

    build_script = repo_root / "tools" / "build_web_release.py"
    if build_script.is_file():
        subprocess.run([sys.executable, str(build_script)], cwd=repo_root, check=True)
        fixes.append({"kind": "command", "path": str(build_script), "detail": "rebuilt release artifacts"})
    return fixes


def fix_codemaker_manifest_non_scene_paths(
    repo_root: Path,
    rules_path: Path,
    warning: dict[str, Any],
) -> list[dict[str, Any]]:
    data = load_yaml(rules_path)
    fixes: list[dict[str, Any]] = []
    contract = _find_codemaker_bundle_contract(data, "codemaker_non_scene_bundle")
    if contract is None:
        return fixes

    manifest_rel = contract.get("manifest_path")
    required_paths = contract.get("required_paths", [])
    if not isinstance(manifest_rel, str) or not manifest_rel:
        return fixes
    if not isinstance(required_paths, list) or not required_paths:
        return fixes

    manifest_path = repo_root / manifest_rel
    if not manifest_path.is_file():
        return fixes
    for rel_path in required_paths:
        if not (repo_root / rel_path).is_file():
            return fixes

    lines = _read_manifest_entries_with_lines(manifest_path)
    entries = _manifest_entries(lines)
    changed = False
    for rel_path in required_paths:
        if rel_path in entries:
            continue
        _insert_codemaker_manifest_path(lines, rel_path)
        entries.add(rel_path)
        changed = True
        fixes.append(
            {
                "kind": "code",
                "path": str(manifest_path),
                "detail": f"added missing codemaker manifest path: {rel_path}",
            }
        )

    if changed:
        _write_manifest_lines(manifest_path, lines)
    return fixes


def fix_runtime_entry_chain(repo_root: Path, rules_path: Path, warning: dict[str, Any]) -> list[dict[str, Any]]:
    data = load_yaml(rules_path)
    fixes: list[dict[str, Any]] = []
    changed_yaml = False
    tree = data.setdefault("facts", {}).setdefault("tree", {"path": ".", "kind": "root", "children": []})

    main_path = repo_root / "main.py"
    if main_path.is_file():
        if main_path.read_text(encoding="utf-8") != CANONICAL_MAIN_WRAPPER:
            main_path.write_text(CANONICAL_MAIN_WRAPPER, encoding="utf-8")
            fixes.append({"kind": "code", "path": str(main_path), "detail": "normalized runtime main wrapper"})

    shim_path = repo_root / "src" / "runtime" / "main_runtime.py"
    if shim_path.is_file():
        text = shim_path.read_text(encoding="utf-8")
        changed = False
        if "from src.runtime.app import Game" not in text:
            text = text.rstrip() + "\nfrom src.runtime.app import Game, say, say_clear\n"
            changed = True
        if "from src.runtime.app import run as _run" not in text:
            text = text.rstrip() + "\nfrom src.runtime.app import run as _run\n"
            changed = True
        if ENTRY_POINT_MARKER in text:
            prefix, _, _ = text.partition(ENTRY_POINT_MARKER)
            new_text = prefix.rstrip() + "\n" + CANONICAL_RUNTIME_TAIL
            if new_text != text:
                text = new_text
                changed = True
        if changed:
            shim_path.write_text(text, encoding="utf-8")
            fixes.append({"kind": "code", "path": str(shim_path), "detail": "normalized runtime shim tail"})

    canonical_entry_chain = [
        {"id": "runtime_main_wrapper", "path": "main.py", "role": "wrapper", "status": "active", "summary": "src/runtime/main_runtime.py を実行する 8 行 wrapper"},
        {"id": "runtime_shim", "path": "src/runtime/main_runtime.py", "role": "shim", "status": "active", "summary": "test / Code Maker bundler 互換のための re-export shim"},
        {"id": "runtime_game", "path": "src/runtime/app.py", "symbol": "Game", "role": "application_root", "status": "active", "summary": "pyxel 初期化、DI、scene/service 組み立て、update/draw dispatcher"},
    ]
    ensure_tree_path(tree, "main.py", "file", role="runtime_wrapper", status="active", source_of_truth=False, summary="src/runtime/main_runtime.py を呼ぶ薄い wrapper")
    ensure_tree_path(tree, "src/runtime", "directory", role="runtime_container", status="active", source_of_truth=True, summary="Pyxel 単一入口の受け皿")
    ensure_tree_path(
        tree,
        "src/runtime/main_runtime.py",
        "file",
        role="shim",
        status="active",
        source_of_truth=False,
        summary="test / Code Maker bundler 互換のための re-export shim",
    )
    ensure_tree_path(
        tree,
        "src/runtime/app.py",
        "file",
        role="application_root",
        status="active",
        source_of_truth=True,
        symbol="Game",
        summary="pyxel 初期化、DI、scene/service 組み立て、update/draw dispatcher",
    )
    entry_points = data.setdefault("facts", {}).setdefault("entry_points", [])
    current_entry = next((item for item in entry_points if item.get("id") == "runtime_entry_chain"), None)
    canonical_entry = {
        "id": "runtime_entry_chain",
        "summary": "runtime の入口は wrapper -> shim -> Game の流れを保つ",
        "paths": [item["path"] for item in canonical_entry_chain],
        "nodes": canonical_entry_chain,
    }
    if current_entry is None:
        entry_points.append(canonical_entry)
        changed_yaml = True
    elif current_entry != canonical_entry:
        current_entry.clear()
        current_entry.update(canonical_entry)
        changed_yaml = True
    if changed_yaml:
        write_yaml(rules_path, data)
        fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "normalized runtime entry tree nodes and entry_points"})
    return fixes


FIXER_REGISTRY = {
    "generated_files_edit_policy": fix_generated_files_edit_policy,
    "dist_not_source": fix_dist_not_source,
    "codemaker_manifest_non_scene_paths": fix_codemaker_manifest_non_scene_paths,
    "build_runbook_paths": fix_build_runbook_paths,
    "runtime_entry_chain": fix_runtime_entry_chain,
}


def run_fixer(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
    check: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    rules_path = rules_path.resolve()
    try:
        current_check = check or check_architecture_rules.run_checker(
            repo_root,
            rules_path,
            rule_ids=rule_ids,
        )
        if not current_check["has_warnings"]:
            return {
                "status": "OK",
                "check": current_check,
                "applied_fixes": [],
            }

        applied_fixes: list[dict[str, Any]] = []
        warnings = [item for item in current_check["results"] if item["status"] == "warning"]
        for warning in warnings:
            fixer = FIXER_REGISTRY.get(warning["rule_id"])
            if fixer is None:
                continue
            fixes = fixer(repo_root, rules_path, warning)
            if fixes:
                applied_fixes.extend(fixes)

        return {
            "status": "FIXED" if applied_fixes else "NEEDS_HUMAN",
            "check": current_check,
            "applied_fixes": applied_fixes,
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "check": check,
            "applied_fixes": [],
            "error": str(exc),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--rules-path", type=Path, default=ROOT / "docs" / "architecture_rules.yml")
    parser.add_argument("--rule-id", action="append", default=[])
    args = parser.parse_args(argv)
    result = run_fixer(
        args.repo_root,
        args.rules_path,
        rule_ids=set(args.rule_id) if args.rule_id else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"OK", "FIXED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
