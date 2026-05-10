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


def load_report_module():
    try:
        import report_source_trace_coverage
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/report_source_trace_coverage.py is missing: {exc}") from exc
    return report_source_trace_coverage


def make_rules_document(
    *,
    source_documents: list[dict],
    requests: list[dict],
    requirements: list[dict] | None = None,
    acceptance: list[dict] | None = None,
) -> dict:
    return {
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
            "requests": requests,
            "source_documents": source_documents,
            "requirements": requirements or [],
            "acceptance": acceptance or [],
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
        "validation_rules": [],
    }


class SourceTraceCoverageReportTest(unittest.TestCase):
    def test_build_report_counts_total_referenced_and_missing_refs(self):
        report_module = load_report_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "customer-jobs.md").write_text(
                "# jobs\n\n## A [JOB:JPL_CHILD_PLAYER]\n## B [JOB:JCR_CHILD_CREATOR]\n",
                encoding="utf-8",
            )
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        source_documents=[
                            {
                                "id": "customer_jobs",
                                "path": "docs/customer-jobs.md",
                                "extraction": {
                                    "regex": ["JOB:[A-Z0-9_]+"],
                                },
                            }
                        ],
                        requests=[
                            {
                                "id": "rq_child_edit_ownership",
                                "stakeholder_id": "st_repo_developer",
                                "status": "active",
                                "summary": "child wants ownership",
                                "source_refs": ["docs/customer-jobs.md"],
                                "source_trace_refs": ["customer_jobs:JOB:JCR_CHILD_CREATOR"],
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            report = report_module.build_report(repo_root, rules_path)

        self.assertEqual(report["status"], "OK")
        self.assertEqual(report["summary"]["total_documents"], 1)
        self.assertEqual(report["summary"]["broken_documents"], 0)
        self.assertEqual(report["documents"][0]["doc_id"], "customer_jobs")
        self.assertEqual(report["documents"][0]["total_refs"], 2)
        self.assertEqual(
            report["documents"][0]["referenced_refs"],
            ["JOB:JCR_CHILD_CREATOR"],
        )
        self.assertEqual(
            report["documents"][0]["missing_refs"],
            ["JOB:JPL_CHILD_PLAYER"],
        )

    def test_build_report_fails_closed_when_source_document_has_no_extraction_contract(self):
        report_module = load_report_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "customer-jobs.md").write_text(
                "# jobs\n\n## A [JOB:JPL_CHILD_PLAYER]\n",
                encoding="utf-8",
            )
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        source_documents=[
                            {
                                "id": "customer_jobs",
                                "path": "docs/customer-jobs.md",
                            }
                        ],
                        requests=[
                            {
                                "id": "rq_child_edit_ownership",
                                "stakeholder_id": "st_repo_developer",
                                "status": "active",
                                "summary": "child wants ownership",
                                "source_refs": ["docs/customer-jobs.md"],
                                "source_trace_refs": ["customer_jobs:JOB:JPL_CHILD_PLAYER"],
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            report = report_module.build_report(repo_root, rules_path)

        self.assertEqual(report["status"], "BROKEN_TRACEABILITY")
        self.assertGreaterEqual(len(report["errors"]), 1)
        self.assertEqual(report["errors"][0]["kind"], "invalid_extraction_contract")

    def test_build_report_fails_closed_when_trace_ref_uses_unknown_doc_id(self):
        report_module = load_report_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "docs" / "customer-jobs.md").write_text(
                "# jobs\n\n## A [JOB:JPL_CHILD_PLAYER]\n",
                encoding="utf-8",
            )
            rules_path = repo_root / "stakeholder_voices.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    make_rules_document(
                        source_documents=[
                            {
                                "id": "customer_jobs",
                                "path": "docs/customer-jobs.md",
                                "extraction": {
                                    "regex": ["JOB:[A-Z0-9_]+"],
                                },
                            }
                        ],
                        requests=[
                            {
                                "id": "rq_child_edit_ownership",
                                "stakeholder_id": "st_repo_developer",
                                "status": "active",
                                "summary": "child wants ownership",
                                "source_refs": ["docs/customer-jobs.md"],
                                "source_trace_refs": ["unknown_doc:JOB:JPL_CHILD_PLAYER"],
                            }
                        ],
                    ),
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            report = report_module.build_report(repo_root, rules_path)

        self.assertEqual(report["status"], "BROKEN_TRACEABILITY")
        self.assertGreaterEqual(len(report["errors"]), 1)
        self.assertEqual(report["errors"][0]["kind"], "unknown_doc_id")

    def test_cli_runs_on_real_repo_and_returns_document_summaries(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "report_source_trace_coverage.py")],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "OK")
        self.assertGreaterEqual(payload["summary"]["total_documents"], 9)
        document_ids = {item["doc_id"] for item in payload["documents"]}
        self.assertIn("customer_jobs", document_ids)
        self.assertIn("framework_rule", document_ids)
        self.assertIn("product_requirements_av", document_ids)
        self.assertIn("product_requirements_narrative", document_ids)

    def test_real_repo_report_covers_all_map_prd_refs(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_map")

        self.assertEqual(
            document["referenced_refs"],
            ["CJG01", "CJG02", "CJG03", "CJG04", "CJG05", "CJG06", "CJG07"],
        )
        self.assertEqual(document["missing_refs"], [])

    def test_real_repo_report_covers_all_battle_prd_refs(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_battle")

        self.assertEqual(
            document["referenced_refs"],
            ["CJG08", "CJG10", "CJG13", "CJG29"],
        )
        self.assertEqual(document["missing_refs"], [])

    def test_real_repo_report_covers_all_platform_prd_refs(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_platform")

        self.assertEqual(
            document["referenced_refs"],
            ["CJG12", "CJG20", "CJG21", "CJG22", "CJG23", "CJG25", "CJG26", "CJG31", "CJG32", "CJG33", "CJG34", "CJG43"],
        )
        self.assertEqual(document["missing_refs"], [])

    def test_real_repo_report_covers_all_guardrails_prd_refs(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_guardrails")

        self.assertEqual(
            document["referenced_refs"],
            ["CJG35", "CJG36", "CJG37", "CJG38", "CJG39", "CJG40", "CJG41", "CJG44"],
        )
        self.assertEqual(document["missing_refs"], [])

    def test_real_repo_report_covers_all_av_prd_refs(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_av")

        self.assertEqual(
            document["referenced_refs"],
            ["CJG15", "CJG16", "CJG17", "CJG18", "CJG19", "CJG20", "CJG24", "CJG44"],
        )
        self.assertEqual(document["missing_refs"], [])

    def test_real_repo_report_reduces_customer_job_missing_refs_to_autonomy_only(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "customer_jobs")

        self.assertEqual(document["missing_refs"], [])

    def test_real_repo_report_reduces_customer_journey_missing_refs_to_story_tail(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "customer_journeys")

        self.assertEqual(document["missing_refs"], [])

    def test_real_repo_report_covers_all_narrative_prd_refs(self):
        report_module = load_report_module()

        payload = report_module.build_report(ROOT, ROOT / "docs" / "stakeholder_voices.yml")
        document = next(item for item in payload["documents"] if item["doc_id"] == "product_requirements_narrative")

        self.assertEqual(document["referenced_refs"], ["CJG09", "CJG14", "CJG27", "CJG30"])
        self.assertEqual(document["missing_refs"], [])


if __name__ == "__main__":
    unittest.main()
