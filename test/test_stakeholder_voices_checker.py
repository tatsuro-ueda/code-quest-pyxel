from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))


def load_checker_module():
    try:
        import check_stakeholder_voices
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/check_stakeholder_voices.py is missing: {exc}") from exc
    return check_stakeholder_voices


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


def make_rules_document(
    *,
    requirements: list[dict],
    acceptance: list[dict],
    validation_rules: list[dict],
    stakeholders: list[dict] | None = None,
    requests: list[dict] | None = None,
    source_documents: list[dict] | None = None,
    required_frontmatter_keys: list[str] | None = None,
) -> dict:
    return {
        "meta": {"document_id": "stakeholder_voices"},
        "facts": {
            "stakeholders": stakeholders
            or [
                {
                    "id": "st_repo_developer",
                    "type": "developer",
                    "label": "Developer",
                    "status": "active",
                }
            ],
            "requests": requests
            or [
                {
                    "id": "rq_dev_safe",
                    "stakeholder_id": "st_repo_developer",
                    "status": "active",
                    "summary": "safe edits",
                    "source_refs": ["docs/framework-rule.md"],
                }
            ],
            "source_documents": source_documents
            or [
                {
                    "id": "customer_journeys",
                    "path": "docs/customer-journeys.md",
                },
                {
                    "id": "product_requirements_platform",
                    "path": "docs/product-requirements-platform.md",
                },
                {
                    "id": "product_requirements_guardrails",
                    "path": "docs/product-requirements-guardrails.md",
                },
                {
                    "id": "framework_rule",
                    "path": "docs/framework-rule.md",
                },
            ],
            "requirements": requirements,
            "acceptance": acceptance,
            "tasknote_contracts": {
                "note_glob": "steering/*.md",
                "opt_in_frontmatter_key": "requirement_ids",
                "required_frontmatter_keys": required_frontmatter_keys
                or [
                    "requirement_ids",
                    "acceptance_ids",
                    "stakeholder_ids",
                    "affected_paths",
                    "verification_refs",
                    "done_checks",
                ],
            },
        },
        "validation_rules": validation_rules,
    }


class StakeholderVoicesCheckerTest(unittest.TestCase):
    def test_real_rules_expose_requirement_first_facts(self):
        data = yaml.safe_load((ROOT / "docs" / "stakeholder_voices.yml").read_text(encoding="utf-8"))

        self.assertIn("stakeholders", data["facts"])
        self.assertIn("requests", data["facts"])
        self.assertIn("requirements", data["facts"])
        self.assertIn("acceptance", data["facts"])
        self.assertIn("source_documents", data["facts"])
        self.assertIn("tasknote_contracts", data["facts"])
        self.assertIn("validation_rules", data)
        self.assertGreaterEqual(len(data["facts"]["source_documents"]), 7)
        self.assertGreaterEqual(len(data["facts"]["requirements"]), 10)
        self.assertGreaterEqual(len(data["facts"]["acceptance"]), 10)

    def test_run_checker_executes_deterministic_rules_without_warnings_on_real_repo(self):
        checker = load_checker_module()

        result = checker.run_checker(ROOT, ROOT / "docs" / "stakeholder_voices.yml")

        self.assertTrue(result["run_ok"])
        self.assertFalse(result["has_warnings"])
        self.assertEqual(result["summary"]["total_rules"], 10)
        self.assertEqual(result["summary"]["executed_rules"], 10)
        self.assertEqual(result["summary"]["skipped_rules"], 0)

    def test_cli_stdout_is_valid_json_for_default_repo(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_stakeholder_voices.py")],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["run_ok"])
        self.assertEqual(payload["summary"]["executed_rules"], 10)

    def test_run_checker_warns_when_requirement_references_missing_request(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        requirements=[
                            {
                                "id": "req_fast_feedback_loop",
                                "status": "active",
                                "kind": "experience",
                                "priority": "p1",
                                "derived_from_request_ids": ["rq_missing"],
                                "stakeholder_ids": ["st_repo_developer"],
                                "acceptance_ids": ["acc_fast_feedback_loop_replay"],
                                "summary": "short loop",
                                "must": ["retry quickly"],
                                "must_not": ["wait too long"],
                                "affected_paths": ["tools/build_web_release.py"],
                                "verification_refs": ["tools/build_web_release.py"],
                                "source_refs": ["docs/customer-journeys.md"],
                            }
                        ],
                        acceptance=[
                            {
                                "id": "acc_fast_feedback_loop_replay",
                                "requirement_id": "req_fast_feedback_loop",
                                "priority": "p1",
                                "summary": "short replay loop",
                                "given": "a fresh build exists",
                                "when": "a change lands",
                                "then": ["the child can retry quickly"],
                                "verification": {
                                    "mode": "deterministic",
                                    "refs": ["tools/build_web_release.py"],
                                },
                            }
                        ],
                        validation_rules=[
                            {
                                "id": "request_reference_integrity",
                                "summary": "requirements point to real requests",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["request_reference_integrity"]},
                                "message": "missing request reference",
                                "suggested_actions": ["fix derived_from_request_ids"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        self.assertEqual(result["results"][0]["status"], "warning")
        self.assertEqual(result["results"][0]["failed_checks"], ["request_reference_integrity"])

    def test_run_checker_warns_when_p0_requirement_lacks_acceptance(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        requirements=[
                            {
                                "id": "req_safe_architecture_boundaries",
                                "status": "active",
                                "kind": "engineering_guardrail",
                                "priority": "p0",
                                "derived_from_request_ids": ["rq_dev_safe"],
                                "stakeholder_ids": ["st_repo_developer"],
                                "summary": "safe boundaries",
                                "must": ["static checks exist"],
                                "must_not": ["hidden coupling"],
                                "affected_paths": ["tools/check_stakeholder_voices.py"],
                                "verification_refs": ["tools/check_stakeholder_voices.py"],
                                "source_refs": ["docs/framework-rule.md"],
                            }
                        ],
                        acceptance=[],
                        validation_rules=[
                            {
                                "id": "requirement_acceptance_integrity",
                                "summary": "active P0/P1 requirements link to acceptance",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["requirement_acceptance_integrity"]},
                                "message": "missing acceptance link",
                                "suggested_actions": ["add acceptance_ids and acceptance entries"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        self.assertEqual(result["results"][0]["failed_checks"], ["requirement_acceptance_integrity"])

    def test_run_checker_warns_when_acceptance_has_no_verification(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        requirements=[
                            {
                                "id": "req_safe_architecture_boundaries",
                                "status": "active",
                                "kind": "engineering_guardrail",
                                "priority": "p0",
                                "derived_from_request_ids": ["rq_dev_safe"],
                                "stakeholder_ids": ["st_repo_developer"],
                                "acceptance_ids": ["acc_safe_architecture_boundaries_guard"],
                                "summary": "safe boundaries",
                                "must": ["static checks exist"],
                                "must_not": ["hidden coupling"],
                                "affected_paths": ["tools/check_stakeholder_voices.py"],
                                "verification_refs": ["tools/check_stakeholder_voices.py"],
                                "source_refs": ["docs/framework-rule.md"],
                            }
                        ],
                        acceptance=[
                            {
                                "id": "acc_safe_architecture_boundaries_guard",
                                "requirement_id": "req_safe_architecture_boundaries",
                                "priority": "p0",
                                "summary": "guard catches boundary drift",
                                "given": "architecture rules exist",
                                "when": "the checker runs",
                                "then": ["guard drift becomes visible"],
                                "verification": {
                                    "mode": "deterministic",
                                    "refs": [],
                                },
                            }
                        ],
                        validation_rules=[
                            {
                                "id": "acceptance_has_verification",
                                "summary": "acceptance stays verifiable",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["acceptance_has_verification"]},
                                "message": "acceptance verification drift",
                                "suggested_actions": ["add verification mode and refs"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        self.assertEqual(result["results"][0]["failed_checks"], ["acceptance_has_verification"])

    def test_run_checker_accepts_manual_verification_mode(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        requirements=[
                            {
                                "id": "req_child_keeps_decision_power",
                                "status": "active",
                                "kind": "experience",
                                "priority": "p0",
                                "derived_from_request_ids": ["rq_dev_safe"],
                                "stakeholder_ids": ["st_repo_developer"],
                                "acceptance_ids": ["acc_child_keeps_decision_power_review"],
                                "summary": "child decides",
                                "must": ["the child can accept or reject"],
                                "must_not": ["auto promotion"],
                                "affected_paths": ["tools/check_stakeholder_voices.py"],
                                "verification_refs": ["tools/check_stakeholder_voices.py"],
                                "source_refs": ["docs/framework-rule.md"],
                            }
                        ],
                        acceptance=[
                            {
                                "id": "acc_child_keeps_decision_power_review",
                                "requirement_id": "req_child_keeps_decision_power",
                                "priority": "p0",
                                "summary": "child compares versions",
                                "given": "a child has a candidate build",
                                "when": "the child compares versions",
                                "then": ["the child can accept or reject"],
                                "verification": {
                                    "mode": "manual",
                                    "refs": ["docs/customer-journeys.md"],
                                },
                            }
                        ],
                        validation_rules=[
                            {
                                "id": "acceptance_has_verification",
                                "summary": "acceptance stays verifiable",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["acceptance_has_verification"]},
                                "message": "acceptance verification drift",
                                "suggested_actions": ["add verification mode and refs"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertFalse(result["has_warnings"])

    def test_run_checker_warns_when_opt_in_tasknote_is_missing_acceptance_ids(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "steering").mkdir(parents=True, exist_ok=True)
            (repo_root / "steering" / "sample.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    requirement_ids:
                      - req_safe_architecture_boundaries
                    stakeholder_ids:
                      - st_repo_developer
                    affected_paths:
                      - tools/check_stakeholder_voices.py
                    verification_refs:
                      - python -m pytest test/test_stakeholder_voices_checker.py -q
                    done_checks: []
                    ---

                    # sample
                    """
                ),
                encoding="utf-8",
            )
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        requirements=[
                            {
                                "id": "req_safe_architecture_boundaries",
                                "status": "active",
                                "kind": "engineering_guardrail",
                                "priority": "p0",
                                "derived_from_request_ids": ["rq_dev_safe"],
                                "stakeholder_ids": ["st_repo_developer"],
                                "acceptance_ids": ["acc_safe_architecture_boundaries_guard"],
                                "summary": "safe boundaries",
                                "must": ["static checks exist"],
                                "must_not": ["hidden coupling"],
                                "affected_paths": ["tools/check_stakeholder_voices.py"],
                                "verification_refs": [
                                    "python -m pytest test/test_stakeholder_voices_checker.py -q"
                                ],
                                "source_refs": ["docs/framework-rule.md"],
                            }
                        ],
                        acceptance=[
                            {
                                "id": "acc_safe_architecture_boundaries_guard",
                                "requirement_id": "req_safe_architecture_boundaries",
                                "priority": "p0",
                                "summary": "guard catches boundary drift",
                                "given": "architecture rules exist",
                                "when": "the checker runs",
                                "then": ["guard drift becomes visible"],
                                "verification": {
                                    "mode": "deterministic",
                                    "refs": ["tools/check_stakeholder_voices.py"],
                                },
                            }
                        ],
                        validation_rules=[
                            {
                                "id": "tasknote_frontmatter_integrity",
                                "summary": "task notes keep required frontmatter",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["steering"]},
                                "evidence": {"checks": ["tasknote_frontmatter_integrity"]},
                                "message": "task note frontmatter drift",
                                "suggested_actions": ["restore required frontmatter keys"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        self.assertEqual(result["results"][0]["status"], "warning")
        self.assertEqual(result["results"][0]["failed_checks"], ["tasknote_frontmatter_integrity"])
        self.assertIn(
            "acceptance_ids",
            result["results"][0]["observed"]["tasknote_errors"]["steering/sample.md"]["missing_keys"],
        )

    def test_run_checker_warns_when_source_trace_ref_points_to_unknown_ref(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "customer-journeys.md").write_text(
                "# journeys\n\n### CJ31: 子どもが変更を承認する\n",
                encoding="utf-8",
            )
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        source_documents=[
                            {
                                "id": "customer_journeys",
                                "path": "docs/customer-journeys.md",
                            }
                        ],
                        requirements=[
                            {
                                "id": "req_child_keeps_decision_power",
                                "status": "active",
                                "kind": "experience",
                                "priority": "p0",
                                "derived_from_request_ids": ["rq_dev_safe"],
                                "acceptance_ids": ["acc_child_keeps_decision_power_review"],
                                "stakeholder_ids": ["st_repo_developer"],
                                "source_trace_refs": ["customer_journeys:CJ999"],
                                "summary": "child decides",
                                "must": ["the child can accept or reject"],
                                "must_not": ["auto promotion"],
                                "affected_paths": ["tools/check_stakeholder_voices.py"],
                                "verification_refs": ["tools/check_stakeholder_voices.py"],
                                "source_refs": ["docs/framework-rule.md"],
                            }
                        ],
                        acceptance=[
                            {
                                "id": "acc_child_keeps_decision_power_review",
                                "status": "active",
                                "requirement_id": "req_child_keeps_decision_power",
                                "priority": "p0",
                                "source_trace_refs": ["customer_journeys:CJ31"],
                                "summary": "child compares versions",
                                "given": "a child has a candidate build",
                                "when": "the child compares versions",
                                "then": ["the child can accept or reject"],
                                "verification": {
                                    "mode": "manual",
                                    "refs": ["docs/customer-journeys.md"],
                                },
                            }
                        ],
                        validation_rules=[
                            {
                                "id": "source_traceability_integrity",
                                "summary": "source trace refs resolve to live stable ids",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["source_traceability_integrity"]},
                                "message": "source trace refs may be broken",
                                "suggested_actions": ["fix doc ids or stable refs"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        self.assertEqual(result["results"][0]["failed_checks"], ["source_traceability_integrity"])

    def test_run_checker_warns_when_request_source_trace_ref_points_to_unknown_ref(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "customer-jobs.md").write_text(
                "# jobs\n\n## JCR 子ども（クリエイター） [JOB:JCR_CREATOR]\n",
                encoding="utf-8",
            )
            (repo_root / "docs" / "framework-rule.md").write_text("# rule\n", encoding="utf-8")
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        source_documents=[
                            {
                                "id": "customer_jobs",
                                "path": "docs/customer-jobs.md",
                            },
                            {
                                "id": "framework_rule",
                                "path": "docs/framework-rule.md",
                            },
                        ],
                        requests=[
                            {
                                "id": "rq_child_edit_ownership",
                                "stakeholder_id": "st_repo_developer",
                                "status": "active",
                                "summary": "child wants ownership",
                                "source_refs": ["docs/customer-jobs.md"],
                                "source_trace_refs": ["customer_jobs:JOB:JCR_MISSING"],
                            }
                        ],
                        requirements=[
                            {
                                "id": "req_safe_architecture_boundaries",
                                "status": "active",
                                "kind": "engineering_guardrail",
                                "priority": "p0",
                                "derived_from_request_ids": ["rq_child_edit_ownership"],
                                "acceptance_ids": ["acc_safe_architecture_boundaries_guard"],
                                "stakeholder_ids": ["st_repo_developer"],
                                "source_trace_refs": ["framework_rule:rule"],
                                "summary": "safe boundaries",
                                "must": ["static checks exist"],
                                "must_not": ["hidden coupling"],
                                "affected_paths": ["tools/check_stakeholder_voices.py"],
                                "verification_refs": ["tools/check_stakeholder_voices.py"],
                                "source_refs": ["docs/framework-rule.md"],
                            }
                        ],
                        acceptance=[
                            {
                                "id": "acc_safe_architecture_boundaries_guard",
                                "status": "active",
                                "requirement_id": "req_safe_architecture_boundaries",
                                "priority": "p0",
                                "source_trace_refs": ["framework_rule:rule"],
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
                        validation_rules=[
                            {
                                "id": "source_traceability_integrity",
                                "summary": "source trace refs resolve to live stable ids",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["stakeholder_voices.yml"]},
                                "evidence": {"checks": ["source_traceability_integrity"]},
                                "message": "source trace refs may be broken",
                                "suggested_actions": ["fix doc ids or stable refs"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    repair_autofix="not_recommended",
                                ),
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        self.assertEqual(result["results"][0]["failed_checks"], ["source_traceability_integrity"])
        self.assertIn("requests", result["results"][0]["observed"])


if __name__ == "__main__":
    unittest.main()
