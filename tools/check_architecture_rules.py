from __future__ import annotations

"""architecture_rules.yml の deterministic rule を warning 形式で検証する CLI。"""

import argparse
import json
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parent.parent
VALID_DETERMINISTIC_REVIEWS = {
    "implemented",
    "candidate",
    "keep_llm_assisted",
    "keep_manual",
}
VALID_GUARDIAN_AUTOFIX = {
    "implemented",
    "candidate",
    "not_recommended",
}


@dataclass
class CheckContext:
    repo_root: Path
    rules_path: Path
    data: dict[str, Any]


@dataclass
class CheckOutcome:
    status: str
    checked_paths: list[str]
    failed_checks: list[str] = field(default_factory=list)
    message: str | None = None
    suggested_actions: list[str] = field(default_factory=list)
    reason: str | None = None
    expected: dict[str, Any] | None = None
    observed: dict[str, Any] | None = None


def load_rules(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("architecture rules YAML must parse to a dict")
    for key in ("meta", "facts", "validation_rules"):
        if key not in data:
            raise KeyError(f"missing top-level key: {key}")
    validate_rules_schema(data)
    return data


def validate_rules_schema(data: dict[str, Any]) -> None:
    tree = data.get("facts", {}).get("tree")
    if not isinstance(tree, dict):
        raise KeyError("facts.tree must be present")
    if tree.get("path") != "." or tree.get("kind") != "root":
        raise ValueError("facts.tree must start with path='.' and kind='root'")
    required_rule_keys = {
        "id",
        "summary",
        "severity",
        "enforcement",
        "scope",
        "evidence",
        "message",
        "suggested_actions",
        "coverage",
    }
    for rule in data["validation_rules"]:
        missing = required_rule_keys - set(rule)
        if missing:
            raise KeyError(f"rule {rule.get('id', '<unknown>')} missing keys: {sorted(missing)}")
        if not isinstance(rule["suggested_actions"], list):
            raise TypeError(f"rule {rule['id']} suggested_actions must be a list")
        if "mode" not in rule["enforcement"]:
            raise KeyError(f"rule {rule['id']} missing enforcement.mode")
        if not isinstance(rule.get("scope", {}).get("paths"), list):
            raise TypeError(f"rule {rule['id']} scope.paths must be a list")
        checks = rule.get("evidence", {}).get("checks")
        if not isinstance(checks, list) or not checks:
            raise TypeError(f"rule {rule['id']} evidence.checks must be a non-empty list")
        coverage = rule.get("coverage")
        if not isinstance(coverage, dict):
            raise TypeError(f"rule {rule['id']} coverage must be a dict")
        for key in ("deterministic_review", "next_checker_unit", "guardian_autofix", "rationale"):
            if key not in coverage:
                raise KeyError(f"rule {rule['id']} coverage missing key: {key}")
        if coverage["deterministic_review"] not in VALID_DETERMINISTIC_REVIEWS:
            raise ValueError(
                f"rule {rule['id']} coverage.deterministic_review must be one of "
                f"{sorted(VALID_DETERMINISTIC_REVIEWS)}"
            )
        next_checker_unit = coverage["next_checker_unit"]
        if next_checker_unit is not None and not isinstance(next_checker_unit, str):
            raise TypeError(f"rule {rule['id']} coverage.next_checker_unit must be a string or null")
        if coverage["guardian_autofix"] not in VALID_GUARDIAN_AUTOFIX:
            raise ValueError(
                f"rule {rule['id']} coverage.guardian_autofix must be one of "
                f"{sorted(VALID_GUARDIAN_AUTOFIX)}"
            )
        if not isinstance(coverage["rationale"], str) or not coverage["rationale"].strip():
            raise TypeError(f"rule {rule['id']} coverage.rationale must be a non-empty string")
        if rule["enforcement"]["mode"] == "deterministic":
            for check_name in checks:
                if check_name not in CHECK_REGISTRY:
                    raise KeyError(f"rule {rule['id']} references unknown deterministic check: {check_name}")


def _scope_paths(rule: dict[str, Any]) -> list[str]:
    return list(rule.get("scope", {}).get("paths", []))


def iter_tree_nodes(node: dict[str, Any]):
    yield node
    for child in node.get("children", []):
        yield from iter_tree_nodes(child)


def find_tree_node(data: dict[str, Any], path_value: str) -> dict[str, Any] | None:
    for node in iter_tree_nodes(data["facts"]["tree"]):
        if node.get("path") == path_value:
            return node
    return None


def find_entry_point(data: dict[str, Any], entry_id: str) -> dict[str, Any] | None:
    entries = data.get("facts", {}).get("entry_points", [])
    return next((item for item in entries if item.get("id") == entry_id), None)


def generated_file_nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for node in iter_tree_nodes(data["facts"]["tree"]):
        path_value = node.get("path", "")
        if node.get("kind") == "file" and path_value.startswith("src/generated/"):
            nodes.append(node)
    return nodes


def distribution_artifact_nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    dist_node = find_tree_node(data, "dist")
    if dist_node is None:
        return []
    return [child for child in dist_node.get("children", []) if child.get("kind") == "file"]


def _warning(
    rule: dict[str, Any],
    checked_paths: list[str],
    failed_check: str,
    *,
    reason: str | None = None,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    message = rule.get("message")
    if reason:
        message = f"{message}: {reason}" if message else reason
    return CheckOutcome(
        status="warning",
        checked_paths=checked_paths,
        failed_checks=[failed_check],
        message=message,
        suggested_actions=list(rule.get("suggested_actions", [])),
        expected=expected,
        observed=observed,
    )


def _ok(rule: dict[str, Any], checked_paths: list[str]) -> CheckOutcome:
    return CheckOutcome(status="ok", checked_paths=checked_paths)


def _skipped(rule: dict[str, Any]) -> CheckOutcome:
    return CheckOutcome(
        status="skipped",
        checked_paths=_scope_paths(rule),
        reason="初版では deterministic rule のみ実行する",
    )


def _file_contains(path: Path, needle: str) -> bool:
    return needle in path.read_text(encoding="utf-8")


def wrapper_chain_present(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    for rel_path in checked_paths:
        if not (repo_root / rel_path).exists():
            return _warning(rule, checked_paths, "wrapper_chain_present", reason=f"missing path: {rel_path}")

    entry = find_entry_point(context.data, "runtime_entry_chain")
    if entry is None:
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="facts.entry_points.runtime_entry_chain is missing")
    entry_chain = list(entry.get("nodes", []))
    entry_paths = [item.get("path") for item in entry_chain]
    if entry_paths != checked_paths:
        return _warning(
            rule,
            checked_paths,
            "wrapper_chain_present",
            reason="facts.entry_points.runtime_entry_chain paths do not match scope",
            expected={"scope_paths": checked_paths},
            observed={"entry_chain_paths": entry_paths},
        )
    if entry_chain[-1].get("symbol") != "Game":
        return _warning(
            rule,
            checked_paths,
            "wrapper_chain_present",
            reason="runtime_game symbol is not Game",
            expected={"runtime_game_symbol": "Game"},
            observed={"runtime_game_symbol": entry_chain[-1].get("symbol")},
        )

    main_path = repo_root / "main.py"
    shim_path = repo_root / "src/runtime/main_runtime.py"
    app_path = repo_root / "src/runtime/app.py"

    if not _file_contains(main_path, "main_runtime.py"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="main.py does not point at runtime shim")
    if not _file_contains(main_path, "run()"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="main.py does not call run()")
    if not _file_contains(shim_path, "from src.runtime.app import Game"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime shim does not re-export Game")
    if not _file_contains(shim_path, "from src.runtime.app import run as _run"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime shim does not import run() from app")
    if not _file_contains(shim_path, "def run()"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime shim does not expose run()")
    if not _file_contains(app_path, "class Game"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime app does not define Game")
    if not _file_contains(app_path, "def run()"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime app does not define run()")

    return _ok(rule, checked_paths)


def distribution_paths_marked_non_source(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    dist_root = find_tree_node(context.data, "dist")
    if dist_root is None:
        return _warning(rule, checked_paths, "distribution_paths_marked_non_source", reason="dist root is missing from facts.tree")
    if dist_root.get("status") != "distribution":
        return _warning(
            rule,
            checked_paths,
            "distribution_paths_marked_non_source",
            reason="dist root status is not distribution",
            expected={"status": "distribution"},
            observed={"status": dist_root.get("status")},
        )
    if dist_root.get("source_of_truth") is not False:
        return _warning(
            rule,
            checked_paths,
            "distribution_paths_marked_non_source",
            reason="dist root source_of_truth is not false",
            expected={"source_of_truth": False},
            observed={"source_of_truth": dist_root.get("source_of_truth")},
        )
    if not (repo_root / "dist").exists():
        return _warning(rule, checked_paths, "distribution_paths_marked_non_source", reason="dist directory does not exist")
    return _ok(rule, checked_paths)


def generated_entries_mark_non_hand_editable_and_sources(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    entries = generated_file_nodes(context.data)
    if not (repo_root / "tools/gen_data.py").is_file():
        return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason="tools/gen_data.py is missing")

    for entry in entries:
        rel_path = entry.get("path")
        if not rel_path or not (repo_root / rel_path).is_file():
            return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason=f"generated target is missing: {rel_path}")
        if entry.get("hand_editable") is not False:
            return _warning(
                rule,
                checked_paths,
                "generated_entries_mark_non_hand_editable_and_sources",
                reason=f"hand_editable must be false for {entry.get('id')}",
                expected={"hand_editable": False, "generated_from_prefix": "assets/"},
                observed={"entry_id": entry.get("id"), "hand_editable": entry.get("hand_editable")},
            )
        sources = entry.get("generated_from")
        if not isinstance(sources, list) or not sources:
            return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason=f"generated_from is missing for {entry.get('id')}")
        for source in sources:
            if not str(source).startswith("assets/"):
                return _warning(
                    rule,
                    checked_paths,
                    "generated_entries_mark_non_hand_editable_and_sources",
                    reason=f"generated_from must point to assets/* for {entry.get('id')}",
                    expected={"hand_editable": False, "generated_from_prefix": "assets/"},
                    observed={"entry_id": entry.get("id"), "generated_from": sources},
                )
            if not (repo_root / source).is_file():
                return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason=f"generated source is missing: {source}")

    return _ok(rule, checked_paths)


def _command_script_paths(command: str) -> list[str]:
    tokens = shlex.split(command)
    if "-c" in tokens:
        return []
    return [token for token in tokens if token.endswith(".py")]


def compare_runbook_commands_and_artifact_defs(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    artifact_paths = {item["path"] for item in distribution_artifact_nodes(context.data)}
    runbooks = context.data["facts"].get("runbooks", [])

    for rel_path in checked_paths:
        if not (repo_root / rel_path).exists():
            return _warning(rule, checked_paths, "compare_runbook_commands_and_artifact_defs", reason=f"missing scoped path: {rel_path}")

    for runbook in runbooks:
        for step in runbook.get("steps", []):
            command = step.get("command", "")
            for script_path in _command_script_paths(command):
                if not (repo_root / script_path).exists():
                    return _warning(rule, checked_paths, "compare_runbook_commands_and_artifact_defs", reason=f"runbook command references missing script: {script_path}")
            for output_path in step.get("outputs", []):
                if output_path not in artifact_paths:
                    return _warning(
                        rule,
                        checked_paths,
                        "compare_runbook_commands_and_artifact_defs",
                        reason=f"runbook output not declared as distribution artifact: {output_path}",
                        expected={"artifact_paths": sorted(artifact_paths)},
                        observed={"missing_output": output_path},
                    )
                if not (repo_root / output_path).exists():
                    return _warning(rule, checked_paths, "compare_runbook_commands_and_artifact_defs", reason=f"distribution artifact path is missing: {output_path}")

    return _ok(rule, checked_paths)


CHECK_REGISTRY = {
    "wrapper_chain_present": wrapper_chain_present,
    "distribution_paths_marked_non_source": distribution_paths_marked_non_source,
    "generated_entries_mark_non_hand_editable_and_sources": generated_entries_mark_non_hand_editable_and_sources,
    "compare_runbook_commands_and_artifact_defs": compare_runbook_commands_and_artifact_defs,
}


def run_deterministic_rule(context: CheckContext, rule: dict[str, Any]) -> dict[str, Any]:
    checks = list(rule.get("evidence", {}).get("checks", []))
    if not checks:
        raise KeyError(f"rule {rule.get('id')} has no evidence.checks")
    outcome = _ok(rule, _scope_paths(rule))
    for check_name in checks:
        fn = CHECK_REGISTRY.get(check_name)
        if fn is None:
            raise KeyError(f"no check function registered for {check_name}")
        outcome = fn(context, rule)
        if outcome.status != "ok":
            break
    return result_record(rule, outcome)


def result_record(rule: dict[str, Any], outcome: CheckOutcome) -> dict[str, Any]:
    return {
        "rule_id": rule["id"],
        "status": outcome.status,
        "severity": rule.get("severity"),
        "mode": rule["enforcement"]["mode"],
        "coverage": dict(rule.get("coverage", {})),
        "checked_paths": outcome.checked_paths,
        "failed_checks": outcome.failed_checks,
        "message": outcome.message,
        "suggested_actions": outcome.suggested_actions,
        "reason": outcome.reason,
        "expected": outcome.expected,
        "observed": outcome.observed,
        "rule_source": str(rule.get("__rules_path", "")),
    }


def build_coverage_review(results: list[dict[str, Any]]) -> dict[str, Any]:
    mode_counts = {
        "deterministic": 0,
        "llm_assisted": 0,
        "manual": 0,
    }
    deterministic_candidate_rule_ids: list[str] = []
    next_checker_units: list[dict[str, str]] = []
    guardian_candidate_rule_ids: list[str] = []
    guardian_implemented_rule_ids: list[str] = []
    keep_non_deterministic_rule_ids: list[str] = []

    for item in results:
        mode = item["mode"]
        if mode in mode_counts:
            mode_counts[mode] += 1
        coverage = item.get("coverage", {})
        deterministic_review = coverage.get("deterministic_review")
        if deterministic_review == "candidate":
            deterministic_candidate_rule_ids.append(item["rule_id"])
            next_checker_unit = coverage.get("next_checker_unit")
            if next_checker_unit:
                next_checker_units.append(
                    {
                        "rule_id": item["rule_id"],
                        "unit": next_checker_unit,
                    }
                )
        elif deterministic_review in {"keep_llm_assisted", "keep_manual"}:
            keep_non_deterministic_rule_ids.append(item["rule_id"])

        guardian_autofix = coverage.get("guardian_autofix")
        if guardian_autofix == "candidate":
            guardian_candidate_rule_ids.append(item["rule_id"])
        elif guardian_autofix == "implemented":
            guardian_implemented_rule_ids.append(item["rule_id"])

    return {
        "mode_counts": mode_counts,
        "deterministic_candidate_rule_ids": deterministic_candidate_rule_ids,
        "next_checker_units": next_checker_units,
        "guardian_candidate_rule_ids": guardian_candidate_rule_ids,
        "guardian_implemented_rule_ids": guardian_implemented_rule_ids,
        "keep_non_deterministic_rule_ids": keep_non_deterministic_rule_ids,
    }


def build_output(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "total_rules": len(results),
        "executed_rules": sum(1 for item in results if item["status"] in {"ok", "warning"}),
        "warning_rules": sum(1 for item in results if item["status"] == "warning"),
        "skipped_rules": sum(1 for item in results if item["status"] == "skipped"),
        "error_rules": sum(1 for item in results if item["status"] == "error"),
    }
    return {
        "run_ok": summary["error_rules"] == 0,
        "has_warnings": summary["warning_rules"] > 0,
        "summary": summary,
        "coverage_review": build_coverage_review(results),
        "results": results,
    }


def run_checker(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    rules_path = rules_path.resolve()
    data = load_rules(rules_path)
    context = CheckContext(repo_root=repo_root, rules_path=rules_path, data=data)
    results: list[dict[str, Any]] = []
    for rule in data["validation_rules"]:
        rule["__rules_path"] = str(rules_path)
        if rule_ids is not None and rule["id"] not in rule_ids:
            continue
        mode = rule["enforcement"]["mode"]
        if mode != "deterministic":
            results.append(result_record(rule, _skipped(rule)))
            continue
        results.append(run_deterministic_rule(context, rule))
    return build_output(results)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "architecture_rules.yml",
        help="path to architecture rules YAML",
    )
    parser.add_argument("--rule-id", action="append", default=[], help="run only the specified rule id (repeatable)")
    parser.add_argument("--fail-on-warning", action="store_true", help="return exit 1 when warnings remain")
    args = parser.parse_args(argv)
    try:
        result = run_checker(
            args.repo_root,
            args.rules_path,
            rule_ids=set(args.rule_id) if args.rule_id else None,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.fail_on_warning and result["has_warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
