from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def load_repair_module():
    try:
        import repair_stakeholder_voices
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/repair_stakeholder_voices.py is missing: {exc}") from exc
    return repair_stakeholder_voices


def coverage_metadata(
    *,
    deterministic_review: str,
    next_checker_unit: str | None = None,
    repair_autofix: str,
    rationale: str = "fixture",
) -> dict:
    return {
        "deterministic_review": deterministic_review,
        "next_checker_unit": next_checker_unit,
        "repair_autofix": repair_autofix,
        "rationale": rationale,
    }


class RepairStakeholderVoicesTest(unittest.TestCase):
    def test_repair_cli_runs_clean_on_real_repo(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "repair_stakeholder_voices.py")],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "OK")
        self.assertEqual(payload["cycles"], 1)
        self.assertTrue(payload["final_check"]["run_ok"])
        self.assertFalse(payload["final_check"]["has_warnings"])

    def test_run_repair_autofixes_normalized_lists_until_clean(self):
        repair = load_repair_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "source.md").write_text("# source\n", encoding="utf-8")
            (repo_root / "src").mkdir(parents=True, exist_ok=True)
            (repo_root / "src" / "app.py").write_text("# app\n", encoding="utf-8")
            (repo_root / "test").mkdir(parents=True, exist_ok=True)
            (repo_root / "test" / "test_one.py").write_text("# test\n", encoding="utf-8")
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    {
                        "meta": {"document_id": "stakeholder_voices"},
                        "facts": {
                            "stakeholders": [
                                {
                                    "id": "st_repo_developer",
                                    "type": "developer",
                                    "label": "Developer",
                                    "status": "active",
                                }
                            ],
                            "requests": [
                                {
                                    "id": "rq_dev_safe",
                                    "stakeholder_id": "st_repo_developer",
                                    "status": "active",
                                    "summary": "safe edits",
                                    "source_refs": ["docs/source.md", "docs/source.md"],
                                    "source_trace_refs": [
                                        "framework_rule:M1",
                                        "framework_rule:M1",
                                    ],
                                }
                            ],
                            "source_documents": [
                                {
                                    "id": "framework_rule",
                                    "path": "docs/source.md",
                                }
                            ],
                            "requirements": [
                                {
                                    "id": "req_safe_architecture_boundaries",
                                    "status": "active",
                                    "kind": "engineering_guardrail",
                                    "priority": "p0",
                                    "derived_from_request_ids": [
                                        "rq_dev_safe",
                                        "rq_dev_safe",
                                    ],
                                    "acceptance_ids": [
                                        "acc_safe_architecture_boundaries_guard",
                                        "acc_safe_architecture_boundaries_guard",
                                    ],
                                    "stakeholder_ids": [
                                        "st_repo_developer",
                                        "st_repo_developer",
                                    ],
                                    "source_trace_refs": [
                                        "framework_rule:M1",
                                        "framework_rule:M1",
                                    ],
                                    "summary": "safe boundaries",
                                    "must": ["static checks exist"],
                                    "must_not": ["hidden coupling"],
                                    "affected_paths": ["src/app.py", "src/app.py"],
                                    "verification_refs": [
                                        "test/test_one.py",
                                        "test/test_one.py",
                                    ],
                                    "source_refs": ["docs/source.md", "docs/source.md"],
                                }
                            ],
                            "acceptance": [
                                {
                                    "id": "acc_safe_architecture_boundaries_guard",
                                    "status": "active",
                                    "requirement_id": "req_safe_architecture_boundaries",
                                    "priority": "p0",
                                    "summary": "guard catches drift",
                                    "given": "rules exist",
                                    "when": "the checker runs",
                                    "then": ["drift is visible"],
                                    "verification": {
                                        "mode": "deterministic",
                                        "refs": ["test/test_one.py"],
                                    },
                                }
                            ],
                            "tasknote_contracts": {
                                "note_glob": "steering/*.md",
                                "opt_in_frontmatter_key": "requirement_ids",
                                "required_frontmatter_keys": [
                                    "requirement_ids",
                                    "acceptance_ids",
                                    "stakeholder_ids",
                                    "affected_paths",
                                    "verification_refs",
                                    "done_checks",
                                ],
                            },
                        },
                        "validation_rules": [
                            {
                                "id": "normalized_requirement_lists",
                                "summary": "lists stay sorted and unique",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["normalized_requirement_lists"]},
                                "message": "normalize lists",
                                "suggested_actions": ["dedupe lists"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="implemented",
                                ),
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = repair.run_repair(repo_root, rules_path, max_cycles=5)

        self.assertEqual(result["status"], "AUTOFIXED")
        self.assertLessEqual(result["cycles"], 5)
        self.assertFalse(result["final_check"]["has_warnings"])

    def test_run_repair_returns_needs_human_when_missing_paths_remain(self):
        repair = load_repair_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    {
                        "meta": {"document_id": "stakeholder_voices"},
                        "facts": {
                            "stakeholders": [
                                {
                                    "id": "st_repo_developer",
                                    "type": "developer",
                                    "label": "Developer",
                                    "status": "active",
                                }
                            ],
                            "requests": [
                                {
                                    "id": "rq_dev_safe",
                                    "stakeholder_id": "st_repo_developer",
                                    "status": "active",
                                    "summary": "safe edits",
                                    "source_refs": ["docs/framework-rule.md"],
                                }
                            ],
                            "source_documents": [
                                {
                                    "id": "framework_rule",
                                    "path": "docs/framework-rule.md",
                                }
                            ],
                            "requirements": [
                                {
                                    "id": "req_safe_architecture_boundaries",
                                    "status": "active",
                                    "kind": "engineering_guardrail",
                                    "priority": "p0",
                                    "derived_from_request_ids": ["rq_dev_safe"],
                                    "acceptance_ids": ["acc_safe_architecture_boundaries_guard"],
                                    "stakeholder_ids": ["st_repo_developer"],
                                    "source_trace_refs": ["framework_rule:M1"],
                                    "summary": "safe boundaries",
                                    "must": ["static checks exist"],
                                    "must_not": ["hidden coupling"],
                                    "affected_paths": ["src/missing.py"],
                                    "verification_refs": ["test/missing_test.py"],
                                    "source_refs": ["docs/framework-rule.md"],
                                }
                            ],
                            "acceptance": [
                                {
                                    "id": "acc_safe_architecture_boundaries_guard",
                                    "status": "active",
                                    "requirement_id": "req_safe_architecture_boundaries",
                                    "priority": "p0",
                                    "summary": "guard catches drift",
                                    "given": "rules exist",
                                    "when": "the checker runs",
                                    "then": ["drift is visible"],
                                    "verification": {
                                        "mode": "deterministic",
                                        "refs": ["docs/framework-rule.md"],
                                    },
                                }
                            ],
                            "tasknote_contracts": {
                                "note_glob": "steering/*.md",
                                "opt_in_frontmatter_key": "requirement_ids",
                                "required_frontmatter_keys": [
                                    "requirement_ids",
                                    "acceptance_ids",
                                    "stakeholder_ids",
                                    "affected_paths",
                                    "verification_refs",
                                    "done_checks",
                                ],
                            },
                        },
                        "validation_rules": [
                            {
                                "id": "referenced_paths_exist",
                                "summary": "paths stay live",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["referenced_paths_exist"]},
                                "message": "stale paths",
                                "suggested_actions": ["fix paths"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = repair.run_repair(repo_root, rules_path, max_cycles=3)

        self.assertEqual(result["status"], "NEEDS_HUMAN")
        self.assertLessEqual(result["cycles"], 3)
        self.assertTrue(result["final_check"]["has_warnings"])


if __name__ == "__main__":
    unittest.main()
