from __future__ import annotations

"""stakeholder_voices.yml の deterministic rule を warning 形式で検証する CLI。"""

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
VALID_DETERMINISTIC_REVIEWS = {
    "implemented",
    "candidate",
    "keep_llm_assisted",
    "keep_manual",
}
VALID_REPAIR_AUTOFIX = {
    "implemented",
    "candidate",
    "not_recommended",
}
VALID_ACCEPTANCE_VERIFICATION_MODES = {"deterministic", "manual"}
TRACKED_TRACE_STATUSES = {"active", "later", "wont"}


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
    expected: dict[str, Any] | None = None
    observed: dict[str, Any] | None = None


def load_rules(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("stakeholder voices YAML must parse to a dict")
    for key in ("meta", "facts", "validation_rules"):
        if key not in data:
            raise KeyError(f"missing top-level key: {key}")
    validate_rules_schema(data)
    return data


def validate_rules_schema(data: dict[str, Any]) -> None:
    facts = data.get("facts")
    if not isinstance(facts, dict):
        raise KeyError("facts must be present")
    for key in (
        "stakeholders",
        "requests",
        "requirements",
        "acceptance",
        "source_documents",
        "tasknote_contracts",
    ):
        if key not in facts:
            raise KeyError(f"facts missing key: {key}")
    if not isinstance(facts["stakeholders"], list):
        raise TypeError("facts.stakeholders must be a list")
    if not isinstance(facts["requests"], list):
        raise TypeError("facts.requests must be a list")
    if not isinstance(facts["requirements"], list):
        raise TypeError("facts.requirements must be a list")
    if not isinstance(facts["acceptance"], list):
        raise TypeError("facts.acceptance must be a list")
    if not isinstance(facts["source_documents"], list):
        raise TypeError("facts.source_documents must be a list")
    for source_document in facts["source_documents"]:
        if not isinstance(source_document, dict):
            raise TypeError("facts.source_documents items must be dicts")
        for key in ("id", "path"):
            if key not in source_document:
                raise KeyError(f"source document missing key: {key}")
    contracts = facts["tasknote_contracts"]
    if not isinstance(contracts, dict):
        raise TypeError("facts.tasknote_contracts must be a dict")
    for key in ("note_glob", "opt_in_frontmatter_key", "required_frontmatter_keys"):
        if key not in contracts:
            raise KeyError(f"tasknote_contracts missing key: {key}")
    if not isinstance(contracts["required_frontmatter_keys"], list):
        raise TypeError("tasknote_contracts.required_frontmatter_keys must be a list")

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
        if rule["enforcement"]["mode"] != "deterministic":
            raise ValueError(f"rule {rule['id']} only deterministic mode is supported")
        if not isinstance(rule.get("scope", {}).get("paths"), list):
            raise TypeError(f"rule {rule['id']} scope.paths must be a list")
        checks = rule.get("evidence", {}).get("checks")
        if not isinstance(checks, list) or not checks:
            raise TypeError(f"rule {rule['id']} evidence.checks must be a non-empty list")
        coverage = rule.get("coverage")
        if not isinstance(coverage, dict):
            raise TypeError(f"rule {rule['id']} coverage must be a dict")
        for key in ("deterministic_review", "next_checker_unit", "repair_autofix", "rationale"):
            if key not in coverage:
                raise KeyError(f"rule {rule['id']} coverage missing key: {key}")
        if coverage["deterministic_review"] not in VALID_DETERMINISTIC_REVIEWS:
            raise ValueError(
                f"rule {rule['id']} coverage.deterministic_review must be one of "
                f"{sorted(VALID_DETERMINISTIC_REVIEWS)}"
            )
        if coverage["repair_autofix"] not in VALID_REPAIR_AUTOFIX:
            raise ValueError(
                f"rule {rule['id']} coverage.repair_autofix must be one of "
                f"{sorted(VALID_REPAIR_AUTOFIX)}"
            )
        if coverage["next_checker_unit"] is not None and not isinstance(
            coverage["next_checker_unit"],
            str,
        ):
            raise TypeError(
                f"rule {rule['id']} coverage.next_checker_unit must be a string or null"
            )
        if not isinstance(coverage["rationale"], str) or not coverage["rationale"].strip():
            raise TypeError(f"rule {rule['id']} coverage.rationale must be a non-empty string")
        for check_name in checks:
            if check_name not in CHECK_REGISTRY:
                raise KeyError(f"rule {rule['id']} references unknown deterministic check: {check_name}")


def _scope_paths(rule: dict[str, Any]) -> list[str]:
    return list(rule.get("scope", {}).get("paths", []))


def _id_map(entries: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {entry["id"]: entry for entry in entries}


def _list_duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return duplicates


def _load_frontmatter(path: Path) -> dict[str, Any] | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return None
    parts = text.split("---\n", 2)
    if len(parts) < 3:
        return None
    data = yaml.safe_load(parts[1]) or {}
    if not isinstance(data, dict):
        return None
    return data


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


def check_id_uniqueness(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    facts = ctx.data["facts"]
    id_sources = {
        "stakeholders": [item["id"] for item in facts["stakeholders"]],
        "requests": [item["id"] for item in facts["requests"]],
        "requirements": [item["id"] for item in facts["requirements"]],
        "acceptance": [item["id"] for item in facts["acceptance"]],
        "source_documents": [item["id"] for item in facts["source_documents"]],
        "validation_rules": [item["id"] for item in ctx.data["validation_rules"]],
    }
    duplicates = {name: _list_duplicates(values) for name, values in id_sources.items()}
    duplicates = {name: values for name, values in duplicates.items() if values}
    if duplicates:
        return _warning(
            rule,
            checked_paths,
            "id_uniqueness",
            reason="duplicate ids detected",
            expected={"unique_id_groups": list(id_sources)},
            observed={"duplicates": duplicates},
        )
    return _ok(rule, checked_paths)


def check_stakeholder_reference_integrity(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    facts = ctx.data["facts"]
    stakeholder_ids = set(_id_map(facts["stakeholders"]))
    missing_requests = [
        item["id"]
        for item in facts["requests"]
        if item.get("stakeholder_id") not in stakeholder_ids
    ]
    missing_requirements = {
        item["id"]: [sid for sid in item.get("stakeholder_ids", []) if sid not in stakeholder_ids]
        for item in facts["requirements"]
    }
    missing_requirements = {key: value for key, value in missing_requirements.items() if value}
    if missing_requests or missing_requirements:
        return _warning(
            rule,
            checked_paths,
            "stakeholder_reference_integrity",
            reason="missing stakeholder definitions",
            expected={"known_stakeholder_ids": sorted(stakeholder_ids)},
            observed={
                "request_ids_with_missing_stakeholders": missing_requests,
                "requirement_ids_with_missing_stakeholders": missing_requirements,
            },
        )
    return _ok(rule, checked_paths)


def check_request_reference_integrity(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    facts = ctx.data["facts"]
    request_ids = set(_id_map(facts["requests"]))
    missing = {
        item["id"]: [
            request_id
            for request_id in item.get("derived_from_request_ids", [])
            if request_id not in request_ids
        ]
        for item in facts["requirements"]
    }
    missing = {key: value for key, value in missing.items() if value}
    if missing:
        return _warning(
            rule,
            checked_paths,
            "request_reference_integrity",
            reason="derived_from_request_ids contains unknown ids",
            expected={"known_request_ids": sorted(request_ids)},
            observed={"missing_request_refs": missing},
        )
    return _ok(rule, checked_paths)


def check_requirement_has_code_hints(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    missing: dict[str, list[str]] = {}
    for requirement in ctx.data["facts"]["requirements"]:
        if requirement.get("status") != "active":
            continue
        requirement_missing = [
            key
            for key in ("affected_paths", "verification_refs", "source_refs")
            if not requirement.get(key)
        ]
        if requirement_missing:
            missing[requirement["id"]] = requirement_missing
    if missing:
        return _warning(
            rule,
            checked_paths,
            "requirement_has_code_hints",
            reason="active requirements are missing code hint fields",
            expected={"required_keys": ["affected_paths", "verification_refs", "source_refs"]},
            observed={"missing_keys_by_requirement": missing},
        )
    return _ok(rule, checked_paths)


def check_requirement_acceptance_integrity(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    acceptance_map = _id_map(ctx.data["facts"]["acceptance"])
    requirement_ids = set(_id_map(ctx.data["facts"]["requirements"]))
    missing: dict[str, dict[str, Any]] = {}
    tracked_priorities = {"p0", "p1"}

    for requirement in ctx.data["facts"]["requirements"]:
        if requirement.get("status") != "active":
            continue
        if requirement.get("priority") not in tracked_priorities:
            continue

        requirement_errors: dict[str, Any] = {}
        acceptance_ids = list(requirement.get("acceptance_ids", []))
        if not acceptance_ids:
            requirement_errors["missing_acceptance_ids"] = True
        unresolved = [item for item in acceptance_ids if item not in acceptance_map]
        if unresolved:
            requirement_errors["unknown_acceptance_ids"] = unresolved

        mismatched_links: dict[str, str | None] = {}
        missing_fields: dict[str, list[str]] = {}
        for acceptance_id in acceptance_ids:
            acceptance = acceptance_map.get(acceptance_id)
            if acceptance is None:
                continue
            if acceptance.get("requirement_id") != requirement["id"]:
                mismatched_links[acceptance_id] = acceptance.get("requirement_id")
            acceptance_missing = [
                key for key in ("given", "when", "then") if not acceptance.get(key)
            ]
            if acceptance_missing:
                missing_fields[acceptance_id] = acceptance_missing
        if mismatched_links:
            requirement_errors["mismatched_acceptance_requirement_id"] = mismatched_links
        if missing_fields:
            requirement_errors["acceptance_missing_fields"] = missing_fields

        if requirement_errors:
            missing[requirement["id"]] = requirement_errors

    orphan_acceptance = {
        item["id"]: item.get("requirement_id")
        for item in ctx.data["facts"]["acceptance"]
        if item.get("requirement_id") not in requirement_ids
    }
    if missing or orphan_acceptance:
        return _warning(
            rule,
            checked_paths,
            "requirement_acceptance_integrity",
            reason="acceptance linkage is incomplete or points at the wrong requirement",
            expected={"tracked_priorities": sorted(tracked_priorities)},
            observed={
                "acceptance_errors_by_requirement": missing,
                "acceptance_with_unknown_requirement": orphan_acceptance,
            },
        )
    return _ok(rule, checked_paths)


def check_acceptance_has_verification(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    missing: dict[str, dict[str, Any]] = {}
    for acceptance in ctx.data["facts"]["acceptance"]:
        if acceptance.get("status", "active") != "active":
            continue
        verification = acceptance.get("verification")
        acceptance_errors: dict[str, Any] = {}
        if not isinstance(verification, dict):
            acceptance_errors["missing_verification"] = True
        else:
            mode = verification.get("mode")
            refs = verification.get("refs")
            if mode not in VALID_ACCEPTANCE_VERIFICATION_MODES:
                acceptance_errors["invalid_mode"] = mode
            if not isinstance(refs, list) or not refs:
                acceptance_errors["missing_refs"] = refs
        if acceptance_errors:
            missing[acceptance["id"]] = acceptance_errors
    if missing:
        return _warning(
            rule,
            checked_paths,
            "acceptance_has_verification",
            reason="acceptance scenarios must declare verification mode and refs",
            expected={"valid_modes": sorted(VALID_ACCEPTANCE_VERIFICATION_MODES)},
            observed={"acceptance_verification_errors": missing},
        )
    return _ok(rule, checked_paths)


def check_source_traceability_integrity(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    source_documents = _id_map(ctx.data["facts"]["source_documents"])
    text_cache: dict[str, str] = {}
    observed: dict[str, dict[str, Any]] = {}

    for section_name in ("requests", "requirements", "acceptance"):
        section_errors: dict[str, Any] = {}
        for item in ctx.data["facts"][section_name]:
            if item.get("status", "active") not in TRACKED_TRACE_STATUSES:
                continue
            trace_refs = list(item.get("source_trace_refs", []))
            item_errors: dict[str, Any] = {}
            if not trace_refs:
                item_errors["missing_source_trace_refs"] = True
            else:
                invalid_format: list[str] = []
                unknown_doc_ids: list[str] = []
                missing_doc_paths: list[str] = []
                missing_trace_tokens: list[str] = []
                for trace_ref in trace_refs:
                    if not isinstance(trace_ref, str) or ":" not in trace_ref:
                        invalid_format.append(trace_ref)
                        continue
                    doc_id, trace_token = trace_ref.split(":", 1)
                    if not doc_id or not trace_token:
                        invalid_format.append(trace_ref)
                        continue
                    source_document = source_documents.get(doc_id)
                    if source_document is None:
                        unknown_doc_ids.append(trace_ref)
                        continue
                    doc_path_str = source_document["path"]
                    doc_path = ctx.repo_root / doc_path_str
                    if not doc_path.exists():
                        missing_doc_paths.append(doc_path_str)
                        continue
                    if doc_path_str not in text_cache:
                        text_cache[doc_path_str] = doc_path.read_text(encoding="utf-8")
                    if trace_token not in text_cache[doc_path_str]:
                        missing_trace_tokens.append(trace_ref)
                if invalid_format:
                    item_errors["invalid_format"] = invalid_format
                if unknown_doc_ids:
                    item_errors["unknown_doc_ids"] = sorted(dict.fromkeys(unknown_doc_ids))
                if missing_doc_paths:
                    item_errors["missing_doc_paths"] = sorted(dict.fromkeys(missing_doc_paths))
                if missing_trace_tokens:
                    item_errors["missing_trace_tokens"] = sorted(dict.fromkeys(missing_trace_tokens))
            if item_errors:
                section_errors[item["id"]] = item_errors
        if section_errors:
            observed[section_name] = section_errors

    if observed:
        return _warning(
            rule,
            checked_paths,
            "source_traceability_integrity",
            reason="tracked items must keep live source_trace_refs",
            expected={
                "source_documents": sorted(source_documents),
                "trace_format": "doc_id:stable_ref",
            },
            observed=observed,
        )
    return _ok(rule, checked_paths)


def check_referenced_paths_exist(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    missing_requirements: dict[str, list[str]] = {}
    for requirement in ctx.data["facts"]["requirements"]:
        if requirement.get("status") != "active":
            continue
        paths_to_check = (
            list(requirement.get("affected_paths", []))
            + list(requirement.get("verification_refs", []))
            + list(requirement.get("source_refs", []))
        )
        stale = [path_value for path_value in paths_to_check if not (ctx.repo_root / path_value).exists()]
        if stale:
            missing_requirements[requirement["id"]] = stale

    missing_acceptance: dict[str, list[str]] = {}
    for acceptance in ctx.data["facts"]["acceptance"]:
        if acceptance.get("status", "active") != "active":
            continue
        verification = acceptance.get("verification", {})
        refs = verification.get("refs", []) if isinstance(verification, dict) else []
        stale = [path_value for path_value in refs if not (ctx.repo_root / path_value).exists()]
        if stale:
            missing_acceptance[acceptance["id"]] = stale

    if missing_requirements or missing_acceptance:
        return _warning(
            rule,
            checked_paths,
            "referenced_paths_exist",
            reason="one or more referenced paths do not exist",
            expected={"repo_root": str(ctx.repo_root)},
            observed={
                "missing_paths_by_requirement": missing_requirements,
                "missing_paths_by_acceptance": missing_acceptance,
            },
        )
    return _ok(rule, checked_paths)


def check_tasknote_frontmatter_integrity(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    contracts = ctx.data["facts"]["tasknote_contracts"]
    requirement_map = _id_map(ctx.data["facts"]["requirements"])
    requirement_ids = set(requirement_map)
    stakeholder_ids = set(_id_map(ctx.data["facts"]["stakeholders"]))
    acceptance_map = _id_map(ctx.data["facts"]["acceptance"])
    acceptance_ids = set(acceptance_map)
    note_paths = sorted(ctx.repo_root.glob(contracts["note_glob"]))
    errors: dict[str, dict[str, Any]] = {}
    for note_path in note_paths:
        frontmatter = _load_frontmatter(note_path)
        if not frontmatter or contracts["opt_in_frontmatter_key"] not in frontmatter:
            continue
        note_errors: dict[str, Any] = {}
        missing_keys = [
            key for key in contracts["required_frontmatter_keys"] if key not in frontmatter
        ]
        if missing_keys:
            note_errors["missing_keys"] = missing_keys
        unresolved_requirements = [
            item for item in frontmatter.get("requirement_ids", []) if item not in requirement_ids
        ]
        if unresolved_requirements:
            note_errors["unknown_requirement_ids"] = unresolved_requirements
        unresolved_stakeholders = [
            item for item in frontmatter.get("stakeholder_ids", []) if item not in stakeholder_ids
        ]
        if unresolved_stakeholders:
            note_errors["unknown_stakeholder_ids"] = unresolved_stakeholders
        unresolved_acceptance = [
            item for item in frontmatter.get("acceptance_ids", []) if item not in acceptance_ids
        ]
        if unresolved_acceptance:
            note_errors["unknown_acceptance_ids"] = unresolved_acceptance
        if (
            "acceptance_ids" in frontmatter
            and "requirement_ids" in frontmatter
            and isinstance(frontmatter["acceptance_ids"], list)
            and isinstance(frontmatter["requirement_ids"], list)
        ):
            accepted_requirement_ids = set(frontmatter["requirement_ids"])
            mismatched_acceptance = [
                item
                for item in frontmatter["acceptance_ids"]
                if item in acceptance_map
                and acceptance_map[item].get("requirement_id") not in accepted_requirement_ids
            ]
            if mismatched_acceptance:
                note_errors["acceptance_ids_not_linked_to_requirement_ids"] = mismatched_acceptance
        if "done_checks" in frontmatter and not isinstance(frontmatter["done_checks"], list):
            note_errors["done_checks_not_list"] = True
        if note_errors:
            errors[str(note_path.relative_to(ctx.repo_root))] = note_errors
    if errors:
        return _warning(
            rule,
            checked_paths,
            "tasknote_frontmatter_integrity",
            reason="one or more opt-in task notes have invalid frontmatter",
            expected={"required_frontmatter_keys": contracts["required_frontmatter_keys"]},
            observed={"tasknote_errors": errors},
        )
    return _ok(rule, checked_paths)


def check_normalized_requirement_lists(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    requirement_drift: dict[str, dict[str, dict[str, list[str]]]] = {}
    requirement_list_keys = (
        "derived_from_request_ids",
        "stakeholder_ids",
        "acceptance_ids",
        "source_trace_refs",
        "affected_paths",
        "verification_refs",
        "source_refs",
    )
    for requirement in ctx.data["facts"]["requirements"]:
        item_drift: dict[str, dict[str, list[str]]] = {}
        for key in requirement_list_keys:
            current = list(requirement.get(key, []))
            normalized = sorted(dict.fromkeys(current))
            if current != normalized:
                item_drift[key] = {
                    "current": current,
                    "normalized": normalized,
                }
        if item_drift:
            requirement_drift[requirement["id"]] = item_drift

    request_drift: dict[str, dict[str, dict[str, list[str]]]] = {}
    for request in ctx.data["facts"]["requests"]:
        item_drift: dict[str, dict[str, list[str]]] = {}
        for key in ("source_trace_refs", "source_refs"):
            current = list(request.get(key, []))
            normalized = sorted(dict.fromkeys(current))
            if current != normalized:
                item_drift[key] = {
                    "current": current,
                    "normalized": normalized,
                }
        if item_drift:
            request_drift[request["id"]] = item_drift

    if requirement_drift or request_drift:
        return _warning(
            rule,
            checked_paths,
            "normalized_requirement_lists",
            reason="request or requirement list ordering or duplicates differ from normalized form",
            observed={
                "requirement_list_drift": requirement_drift,
                "request_list_drift": request_drift,
            },
        )
    return _ok(rule, checked_paths)


CHECK_REGISTRY = {
    "id_uniqueness": check_id_uniqueness,
    "stakeholder_reference_integrity": check_stakeholder_reference_integrity,
    "request_reference_integrity": check_request_reference_integrity,
    "requirement_has_code_hints": check_requirement_has_code_hints,
    "requirement_acceptance_integrity": check_requirement_acceptance_integrity,
    "acceptance_has_verification": check_acceptance_has_verification,
    "source_traceability_integrity": check_source_traceability_integrity,
    "referenced_paths_exist": check_referenced_paths_exist,
    "tasknote_frontmatter_integrity": check_tasknote_frontmatter_integrity,
    "normalized_requirement_lists": check_normalized_requirement_lists,
}


def run_rule(ctx: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checks = rule.get("evidence", {}).get("checks", [])
    for check_name in checks:
        outcome = CHECK_REGISTRY[check_name](ctx, rule)
        if outcome.status != "ok":
            return outcome
    return _ok(rule, _scope_paths(rule))


def run_checker(
    repo_root: Path,
    rules_path: Path,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    data = load_rules(rules_path)
    ctx = CheckContext(repo_root=repo_root, rules_path=rules_path, data=data)
    results: list[dict[str, Any]] = []
    warning_count = 0
    executed_rules = 0
    selected_rules = data["validation_rules"]
    if rule_ids is not None:
        selected_rules = [rule for rule in selected_rules if rule["id"] in rule_ids]
    for rule in selected_rules:
        executed_rules += 1
        outcome = run_rule(ctx, rule)
        if outcome.status == "warning":
            warning_count += 1
        results.append(
            {
                "rule_id": rule["id"],
                "status": outcome.status,
                "checked_paths": outcome.checked_paths,
                "failed_checks": outcome.failed_checks,
                "message": outcome.message,
                "suggested_actions": outcome.suggested_actions,
                "expected": outcome.expected,
                "observed": outcome.observed,
                "coverage": rule["coverage"],
            }
        )
    total_rules = len(selected_rules)
    return {
        "run_ok": True,
        "has_warnings": warning_count > 0,
        "summary": {
            "total_rules": total_rules,
            "executed_rules": executed_rules,
            "skipped_rules": 0,
            "warning_rules": warning_count,
        },
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    description = "stakeholder voices deterministic checker"
    if __doc__:
        description = __doc__.splitlines()[0]
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--rules-path", type=Path, default=ROOT / "docs" / "stakeholder_voices.yml")
    parser.add_argument("--rule-id", action="append", default=None)
    args = parser.parse_args(argv)

    payload = run_checker(ROOT, args.rules_path, rule_ids=set(args.rule_id) if args.rule_id else None)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
