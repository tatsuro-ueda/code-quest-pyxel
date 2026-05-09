from __future__ import annotations

"""stakeholder voice rule を check -> fix -> recheck で収束させる repair CLI。"""

import argparse
import json
from pathlib import Path

from . import check_stakeholder_voices, fix_stakeholder_voices


ROOT = Path(__file__).resolve().parents[2]


def run_repair(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
    max_cycles: int = 5,
) -> dict:
    history: list[dict] = []
    cycle = 0
    initial_check = check_stakeholder_voices.run_checker(repo_root, rules_path, rule_ids=rule_ids)
    if not initial_check["has_warnings"]:
        return {
            "status": "OK",
            "cycles": 1,
            "history": [{"cycle": 1, "check": initial_check, "applied_fixes": []}],
            "final_check": initial_check,
        }

    check = initial_check
    while cycle < max_cycles and check["has_warnings"]:
        cycle += 1
        fix_result = fix_stakeholder_voices.run_fixer(repo_root, rules_path, rule_ids=rule_ids)
        history.append(
            {
                "cycle": cycle,
                "check": fix_result["check"],
                "applied_fixes": fix_result["applied_fixes"],
                "post_check": fix_result["post_check"],
                "fix_status": fix_result["status"],
            }
        )
        check = fix_result["post_check"]
        if not fix_result["applied_fixes"]:
            break

    final_check = check_stakeholder_voices.run_checker(repo_root, rules_path, rule_ids=rule_ids)
    if not final_check["has_warnings"]:
        status = "AUTOFIXED"
    else:
        status = "NEEDS_HUMAN"
    return {
        "status": status,
        "cycles": max(cycle, 1),
        "history": history,
        "final_check": final_check,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="stakeholder voices repair loop")
    parser.add_argument("--rules-path", type=Path, default=ROOT / "docs" / "stakeholder_voices.yml")
    parser.add_argument("--rule-id", action="append", default=None)
    parser.add_argument("--max-cycles", type=int, default=5)
    args = parser.parse_args(argv)

    payload = run_repair(
        ROOT,
        args.rules_path,
        rule_ids=set(args.rule_id) if args.rule_id else None,
        max_cycles=args.max_cycles,
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["status"] in {"OK", "AUTOFIXED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
