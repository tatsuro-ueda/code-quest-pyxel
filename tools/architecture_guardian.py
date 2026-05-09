from __future__ import annotations

"""architecture rule 違反を自動修復しながら再検査する guardian。"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

import check_architecture_rules


ROOT = Path(__file__).resolve().parent.parent

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


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")


def _set_rule_internal_fields(data: dict[str, Any], rules_path: Path) -> None:
    for rule in data.get("validation_rules", []):
        rule["__rules_path"] = str(rules_path)


def _generated_entry_expected_source(entry_path: str) -> str:
    stem = Path(entry_path).stem
    return f"assets/{stem}.yaml"


def fix_generated_files_edit_policy(repo_root: Path, rules_path: Path, warning: dict[str, Any]) -> list[dict[str, Any]]:
    data = load_yaml(rules_path)
    fixes: list[dict[str, Any]] = []
    changed_yaml = False
    entries = data.setdefault("facts", {}).setdefault("generated", {}).setdefault("entries", [])

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
    roots = data.setdefault("facts", {}).setdefault("repository", {}).setdefault("roots", [])
    dist_root = next((item for item in roots if item.get("path") == "dist"), None)
    canonical = {
        "id": "dist_root",
        "path": "dist",
        "role": "distribution_root",
        "status": "distribution",
        "source_of_truth": False,
        "summary": "承認済み配布物の出力先",
    }
    if dist_root is None:
        roots.append(canonical)
        changed_yaml = True
        fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "added canonical dist_root"})
    else:
        for key, value in canonical.items():
            if dist_root.get(key) != value:
                dist_root[key] = value
                changed_yaml = True
        if changed_yaml:
            fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "normalized dist_root"})

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
    artifacts = [
        {"id": "codemaker_zip", "path": "dist/code-maker.zip", "status": "distribution", "summary": "block-quest/main.py + my_resource.pyxres を梱包した教材版 zip"},
        {"id": "pyxel_html", "path": "dist/pyxel.html", "status": "distribution", "summary": "Web 配布用 HTML"},
        {"id": "pyxel_pyxapp", "path": "dist/pyxel.pyxapp", "status": "distribution", "summary": "Pyxel app 配布物"},
        {"id": "play_html", "path": "dist/play.html", "status": "distribution", "summary": "プレイページ"},
        {"id": "top_index_html", "path": "dist/index.html", "status": "distribution", "summary": "play.html と同内容の wrapper alias"},
    ]
    distribution = data.setdefault("facts", {}).setdefault("distribution", {})
    if distribution.get("artifacts") != artifacts:
        distribution["artifacts"] = artifacts
        changed_yaml = True
        fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "normalized distribution artifacts"})

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


def fix_runtime_entry_chain(repo_root: Path, rules_path: Path, warning: dict[str, Any]) -> list[dict[str, Any]]:
    data = load_yaml(rules_path)
    fixes: list[dict[str, Any]] = []
    changed_yaml = False

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

    runtime = data.setdefault("facts", {}).setdefault("runtime", {})
    canonical_entry_chain = [
        {"id": "runtime_main_wrapper", "path": "main.py", "role": "wrapper", "status": "active", "summary": "src/runtime/main_runtime.py を実行する 8 行 wrapper"},
        {"id": "runtime_shim", "path": "src/runtime/main_runtime.py", "role": "shim", "status": "active", "summary": "test / Code Maker bundler 互換のための re-export shim"},
        {"id": "runtime_game", "path": "src/runtime/app.py", "symbol": "Game", "role": "application_root", "status": "active", "summary": "pyxel 初期化、DI、scene/service 組み立て、update/draw dispatcher"},
    ]
    if runtime.get("entry_chain") != canonical_entry_chain:
        runtime["entry_chain"] = canonical_entry_chain
        changed_yaml = True
    if changed_yaml:
        write_yaml(rules_path, data)
        fixes.append({"kind": "yaml", "path": str(rules_path), "detail": "normalized runtime entry_chain facts"})
    return fixes


FIXER_REGISTRY = {
    "generated_files_edit_policy": fix_generated_files_edit_policy,
    "dist_not_source": fix_dist_not_source,
    "build_runbook_paths": fix_build_runbook_paths,
    "runtime_entry_chain": fix_runtime_entry_chain,
}


def run_guardian(
    repo_root: Path,
    rules_path: Path,
    *,
    max_cycles: int = 5,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    rules_path = rules_path.resolve()
    history: list[dict[str, Any]] = []
    applied_fixes: list[dict[str, Any]] = []
    autofixed = False

    try:
        for cycle in range(1, max_cycles + 1):
            check = check_architecture_rules.run_checker(repo_root, rules_path, rule_ids=rule_ids)
            history.append({"cycle": cycle, "check": check})
            if not check["has_warnings"]:
                return {
                    "status": "AUTOFIXED" if autofixed else "OK",
                    "cycles": cycle,
                    "history": history,
                    "applied_fixes": applied_fixes,
                    "final_check": check,
                }

            cycle_fixes: list[dict[str, Any]] = []
            warnings = [item for item in check["results"] if item["status"] == "warning"]
            for warning in warnings:
                fixer = FIXER_REGISTRY.get(warning["rule_id"])
                if fixer is None:
                    continue
                fixes = fixer(repo_root, rules_path, warning)
                if fixes:
                    cycle_fixes.extend(fixes)

            if not cycle_fixes:
                return {
                    "status": "NEEDS_HUMAN",
                    "cycles": cycle,
                    "history": history,
                    "applied_fixes": applied_fixes,
                    "final_check": check,
                }

            autofixed = True
            applied_fixes.extend({"cycle": cycle, **fix} for fix in cycle_fixes)

        final_check = check_architecture_rules.run_checker(repo_root, rules_path, rule_ids=rule_ids)
        history.append({"cycle": max_cycles + 1, "check": final_check})
        return {
            "status": "AUTOFIXED" if autofixed and not final_check["has_warnings"] else "NEEDS_HUMAN",
            "cycles": max_cycles,
            "history": history,
            "applied_fixes": applied_fixes,
            "final_check": final_check,
        }
    except Exception as exc:
        return {
            "status": "ERROR",
            "cycles": len(history),
            "history": history,
            "applied_fixes": applied_fixes,
            "error": str(exc),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--rules-path", type=Path, default=ROOT / "docs" / "architecture_rules.yml")
    parser.add_argument("--max-cycles", type=int, default=5)
    parser.add_argument("--rule-id", action="append", default=[])
    args = parser.parse_args(argv)
    result = run_guardian(
        args.repo_root,
        args.rules_path,
        max_cycles=args.max_cycles,
        rule_ids=set(args.rule_id) if args.rule_id else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"OK", "AUTOFIXED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
