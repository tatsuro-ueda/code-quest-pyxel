from __future__ import annotations

"""stakeholder voice warning に対して一度だけ deterministic fix を適用する。"""

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

from . import check_stakeholder_voices


ROOT = Path(__file__).resolve().parents[2]
REQUIREMENT_NORMALIZED_LIST_KEYS = (
    "derived_from_request_ids",
    "acceptance_ids",
    "stakeholder_ids",
    "source_trace_refs",
    "affected_paths",
    "verification_refs",
    "source_refs",
)
REQUEST_NORMALIZED_LIST_KEYS = (
    "source_trace_refs",
    "source_refs",
)


class _ReadableYamlDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> Any:
        return super().increase_indent(flow, False)


def load_yaml(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _format_yaml_for_humans(data: dict[str, Any]) -> str:
    dumped = yaml.dump(
        data,
        Dumper=_ReadableYamlDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
        width=88,
    )
    formatted: list[str] = []
    for raw_line in dumped.splitlines():
        line = raw_line.rstrip()
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        needs_separator = False
        if line in {"facts:", "validation_rules:"}:
            needs_separator = True
        elif stripped.startswith("- id:") and indent <= 4:
            needs_separator = True
        if needs_separator and formatted and formatted[-1] != "":
            formatted.append("")
        formatted.append(line)
    return "\n".join(formatted).lstrip("\n") + "\n"


def write_yaml(path: Path, data: dict[str, Any]) -> None:
    path.write_text(_format_yaml_for_humans(data), encoding="utf-8")


def normalize_requirement_lists(data: dict[str, Any]) -> list[dict[str, str]]:
    fixes: list[dict[str, str]] = []
    for requirement in data.get("facts", {}).get("requirements", []):
        requirement_id = requirement.get("id", "<unknown>")
        for key in REQUIREMENT_NORMALIZED_LIST_KEYS:
            current = list(requirement.get(key, []))
            normalized = sorted(dict.fromkeys(current))
            if current != normalized:
                requirement[key] = normalized
                fixes.append(
                    {
                        "kind": "yaml",
                        "path": "facts.requirements",
                        "detail": f"normalized {requirement_id}:{key}",
                    }
                )
    for request in data.get("facts", {}).get("requests", []):
        request_id = request.get("id", "<unknown>")
        for key in REQUEST_NORMALIZED_LIST_KEYS:
            current = list(request.get(key, []))
            normalized = sorted(dict.fromkeys(current))
            if current != normalized:
                request[key] = normalized
                fixes.append(
                    {
                        "kind": "yaml",
                        "path": "facts.requests",
                        "detail": f"normalized {request_id}:{key}",
                    }
                )
    return fixes


FIXER_REGISTRY = {
    "normalized_requirement_lists": normalize_requirement_lists,
}


def run_fixer(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    check = check_stakeholder_voices.run_checker(repo_root, rules_path, rule_ids=rule_ids)
    if not check["has_warnings"]:
        return {
            "status": "OK",
            "check": check,
            "post_check": check,
            "applied_fixes": [],
        }

    data = load_yaml(rules_path)
    applied_fixes: list[dict[str, str]] = []
    for result in check["results"]:
        if result["status"] != "warning":
            continue
        if result["rule_id"] not in FIXER_REGISTRY:
            continue
        applied_fixes.extend(FIXER_REGISTRY[result["rule_id"]](data))

    if applied_fixes:
        write_yaml(rules_path, data)

    post_check = check_stakeholder_voices.run_checker(repo_root, rules_path, rule_ids=rule_ids)
    if applied_fixes and not post_check["has_warnings"]:
        status = "FIXED"
    elif not applied_fixes and check["has_warnings"]:
        status = "NEEDS_HUMAN"
    elif post_check["has_warnings"]:
        status = "NEEDS_HUMAN"
    else:
        status = "OK"

    return {
        "status": status,
        "check": check,
        "post_check": post_check,
        "applied_fixes": applied_fixes,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="stakeholder voices deterministic fixer")
    parser.add_argument("--rules-path", type=Path, default=ROOT / "docs" / "stakeholder_voices.yml")
    parser.add_argument("--rule-id", action="append", default=None)
    args = parser.parse_args(argv)

    payload = run_fixer(ROOT, args.rules_path, rule_ids=set(args.rule_id) if args.rule_id else None)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] in {"OK", "FIXED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
