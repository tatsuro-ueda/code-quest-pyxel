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


def load_checker_module():
    try:
        import check_architecture_rules
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/check_architecture_rules.py is missing: {exc}") from exc
    return check_architecture_rules


def find_tree_node(node: dict, path_value: str) -> dict | None:
    if node.get("path") == path_value:
        return node
    for child in node.get("children", []):
        found = find_tree_node(child, path_value)
        if found is not None:
            return found
    return None


class ArchitectureRulesCheckerTest(unittest.TestCase):
    def test_real_rules_expose_tree_first_facts(self):
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))

        self.assertIn("tree", data["facts"])
        self.assertNotIn("repository", data["facts"])
        self.assertNotIn("runtime", data["facts"])
        self.assertNotIn("generated", data["facts"])
        self.assertNotIn("distribution", data["facts"])
        self.assertIsNotNone(find_tree_node(data["facts"]["tree"], "src/runtime/app.py"))
        self.assertIsNotNone(find_tree_node(data["facts"]["tree"], "src/generated/dialogue.py"))
        self.assertIn("entry_points", data["facts"])

    def test_validation_rules_include_suggested_actions(self):
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
        rules = data["validation_rules"]

        self.assertTrue(rules)
        for rule in rules:
            self.assertIn("suggested_actions", rule)
            self.assertIsInstance(rule["suggested_actions"], list)

    def test_validation_rules_include_coverage_metadata(self):
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
        rules = data["validation_rules"]

        self.assertTrue(rules)
        for rule in rules:
            self.assertIn("coverage", rule)
            coverage = rule["coverage"]
            self.assertIsInstance(coverage, dict)
            self.assertIn("deterministic_review", coverage)
            self.assertIn("next_checker_unit", coverage)
            self.assertIn("guardian_autofix", coverage)
            self.assertIn("rationale", coverage)

    def test_run_checker_executes_deterministic_rules_and_skips_others(self):
        checker = load_checker_module()

        result = checker.run_checker(ROOT, ROOT / "docs" / "architecture_rules.yml")

        self.assertTrue(result["run_ok"])
        self.assertEqual(result["summary"]["total_rules"], 8)
        self.assertEqual(result["summary"]["executed_rules"], 4)
        self.assertEqual(result["summary"]["skipped_rules"], 4)

        by_rule = {item["rule_id"]: item for item in result["results"]}
        self.assertEqual(by_rule["runtime_entry_chain"]["status"], "ok")
        self.assertEqual(by_rule["dist_not_source"]["status"], "ok")
        self.assertEqual(by_rule["generated_files_edit_policy"]["status"], "ok")
        self.assertEqual(by_rule["build_runbook_paths"]["status"], "ok")
        self.assertEqual(by_rule["code_maker_primary_editor"]["status"], "skipped")
        self.assertEqual(by_rule["pyxres_source_of_truth"]["status"], "skipped")
        self.assertEqual(
            by_rule["scene_mvp_boundary"]["coverage"]["deterministic_review"],
            "candidate",
        )
        self.assertEqual(
            by_rule["shared_service_vs_state_boundary"]["coverage"]["deterministic_review"],
            "candidate",
        )

    def test_run_checker_reports_coverage_review(self):
        checker = load_checker_module()

        result = checker.run_checker(ROOT, ROOT / "docs" / "architecture_rules.yml")

        self.assertEqual(
            result["coverage_review"]["mode_counts"],
            {
                "deterministic": 4,
                "llm_assisted": 3,
                "manual": 1,
            },
        )
        self.assertEqual(
            result["coverage_review"]["deterministic_candidate_rule_ids"],
            [
                "scene_mvp_boundary",
                "shared_service_vs_state_boundary",
            ],
        )
        self.assertEqual(
            result["coverage_review"]["next_checker_units"],
            [
                {
                    "rule_id": "scene_mvp_boundary",
                    "unit": "scene_static_boundary_checks",
                },
                {
                    "rule_id": "shared_service_vs_state_boundary",
                    "unit": "shared_directory_role_checks",
                },
            ],
        )
        self.assertEqual(result["coverage_review"]["guardian_candidate_rule_ids"], [])
        self.assertEqual(
            result["coverage_review"]["guardian_implemented_rule_ids"],
            [
                "runtime_entry_chain",
                "dist_not_source",
                "generated_files_edit_policy",
                "build_runbook_paths",
            ],
        )
        self.assertEqual(
            result["coverage_review"]["keep_non_deterministic_rule_ids"],
            [
                "code_maker_primary_editor",
                "pyxres_source_of_truth",
            ],
        )

    def test_run_checker_can_filter_single_rule(self):
        checker = load_checker_module()

        result = checker.run_checker(
            ROOT,
            ROOT / "docs" / "architecture_rules.yml",
            rule_ids={"runtime_entry_chain"},
        )

        self.assertTrue(result["run_ok"])
        self.assertEqual(result["summary"]["total_rules"], 1)
        self.assertEqual(result["summary"]["executed_rules"], 1)
        self.assertEqual([item["rule_id"] for item in result["results"]], ["runtime_entry_chain"])

    def test_cli_stdout_is_valid_json_for_default_repo(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "check_architecture_rules.py")],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["run_ok"])
        self.assertEqual(payload["summary"]["executed_rules"], 4)
        self.assertEqual(payload["summary"]["skipped_rules"], 4)

    def test_cli_fail_on_warning_returns_exit_one(self):
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
        dialogue_node = find_tree_node(data["facts"]["tree"], "src/generated/dialogue.py")
        self.assertIsNotNone(dialogue_node)
        dialogue_node["hand_editable"] = True

        with tempfile.TemporaryDirectory() as tmp:
            broken_yaml = Path(tmp) / "architecture_rules.yml"
            broken_yaml.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "check_architecture_rules.py"),
                    "--rules-path",
                    str(broken_yaml),
                    "--fail-on-warning",
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
                check=False,
            )

        self.assertEqual(completed.returncode, 1, completed.stdout)

    def test_run_checker_rejects_rule_missing_suggested_actions(self):
        checker = load_checker_module()
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
        del data["validation_rules"][0]["suggested_actions"]

        with tempfile.TemporaryDirectory() as tmp:
            broken_yaml = Path(tmp) / "architecture_rules.yml"
            broken_yaml.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            with self.assertRaises(KeyError):
                checker.run_checker(ROOT, broken_yaml)

    def test_cli_returns_warning_with_suggested_actions_and_exit_zero(self):
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
        for rule in data["validation_rules"]:
            if rule["id"] == "generated_files_edit_policy":
                rule["suggested_actions"] = [
                    "src/generated を手編集せず、assets 側を直して gen_data.py を実行する"
                ]
                break
        dialogue_node = find_tree_node(data["facts"]["tree"], "src/generated/dialogue.py")
        self.assertIsNotNone(dialogue_node)
        dialogue_node["hand_editable"] = True

        with tempfile.TemporaryDirectory() as tmp:
            broken_yaml = Path(tmp) / "architecture_rules.yml"
            broken_yaml.write_text(
                yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                encoding="utf-8",
            )
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "check_architecture_rules.py"),
                    "--repo-root",
                    str(ROOT),
                    "--rules-path",
                    str(broken_yaml),
                ],
                capture_output=True,
                text=True,
                cwd=ROOT,
                check=False,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["has_warnings"])
        by_rule = {item["rule_id"]: item for item in payload["results"]}
        self.assertEqual(by_rule["generated_files_edit_policy"]["status"], "warning")
        self.assertEqual(
            by_rule["generated_files_edit_policy"]["failed_checks"],
            ["generated_entries_mark_non_hand_editable_and_sources"],
        )
        self.assertEqual(
            by_rule["generated_files_edit_policy"]["expected"],
            {
                "hand_editable": False,
                "generated_from_prefix": "assets/",
            },
        )
        self.assertEqual(
            by_rule["generated_files_edit_policy"]["observed"],
            {
                "entry_id": "generated_dialogue",
                "hand_editable": True,
            },
        )
        self.assertEqual(
            by_rule["generated_files_edit_policy"]["suggested_actions"],
            ["src/generated を手編集せず、assets 側を直して gen_data.py を実行する"],
        )


if __name__ == "__main__":
    unittest.main()
