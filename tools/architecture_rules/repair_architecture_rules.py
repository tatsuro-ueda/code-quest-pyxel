from __future__ import annotations

"""architecture rule を check -> fix -> recheck で収束させる repair CLI。"""

import argparse
import json
from pathlib import Path
from typing import Any

from . import check_architecture_rules, fix_architecture_rules


ROOT = Path(__file__).resolve().parents[2]


def run_repair(
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
            # 毎サイクルの最初に checker の生結果を history へ積み、
            # 「何を見てどこで止まったか」を後から追えるようにする。
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

            fix_result = fix_architecture_rules.run_fixer(
                repo_root,
                rules_path,
                rule_ids=rule_ids,
                check=check,
            )
            # fixer が内部例外を返した場合は再試行しても改善しないので即終了。
            if fix_result["status"] == "ERROR":
                return {
                    "status": "ERROR",
                    "cycles": cycle,
                    "history": history,
                    "applied_fixes": applied_fixes,
                    "error": fix_result["error"],
                }
            # 「直せる rule が残っていない」状態なので、人手判断に切り替える。
            if fix_result["status"] != "FIXED":
                return {
                    "status": "NEEDS_HUMAN",
                    "cycles": cycle,
                    "history": history,
                    "applied_fixes": applied_fixes,
                    "final_check": check,
                }

            autofixed = True
            applied_fixes.extend({"cycle": cycle, **fix} for fix in fix_result["applied_fixes"])

        # 上限回数に達した場合も最後に再検査し、直り切ったのか未収束なのかを確定させる。
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
    result = run_repair(
        args.repo_root,
        args.rules_path,
        max_cycles=args.max_cycles,
        rule_ids=set(args.rule_id) if args.rule_id else None,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] in {"OK", "AUTOFIXED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
