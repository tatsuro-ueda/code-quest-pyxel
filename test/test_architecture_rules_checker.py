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


def coverage_metadata(
    *,
    deterministic_review: str,
    next_checker_unit: str | None = None,
    guardian_autofix: str,
    rationale: str = "fixture",
) -> dict:
    return {
        "deterministic_review": deterministic_review,
        "next_checker_unit": next_checker_unit,
        "guardian_autofix": guardian_autofix,
        "rationale": rationale,
    }


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
            self.assertNotIn("repair_autofix", coverage)
            self.assertIn("rationale", coverage)
            self.assertEqual(len([key for key in coverage if key.endswith("_autofix")]), 1)

    def test_major_id_sections_put_label_ja_before_id(self):
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))

        self.assertTrue(all("label_ja" in item for item in data["facts"]["principles"]))
        self.assertTrue(all("label_ja" in item for item in data["facts"]["flows"]))
        self.assertTrue(all("label_ja" in item for item in data["facts"]["entry_points"]))
        self.assertTrue(all("label_ja" in item for item in data["facts"]["runbooks"]))
        self.assertTrue(all("label_ja" in item for item in data["facts"]["codemaker_bundle_contracts"]))
        self.assertTrue(all("label_ja" in item for item in data["facts"]["migration_notes"]))
        self.assertTrue(all("label_ja" in item for item in data["validation_rules"]))

        for item in data["facts"]["principles"]:
            self.assertEqual(list(item.keys())[:2], ["label_ja", "id"])
        for item in data["facts"]["flows"]:
            self.assertEqual(list(item.keys())[:2], ["label_ja", "id"])
        for item in data["facts"]["entry_points"]:
            self.assertEqual(list(item.keys())[:2], ["label_ja", "id"])
            for node in item.get("nodes", []):
                self.assertEqual(list(node.keys())[:2], ["label_ja", "id"])
        for item in data["facts"]["runbooks"]:
            self.assertEqual(list(item.keys())[:2], ["label_ja", "id"])
        for item in data["facts"]["codemaker_bundle_contracts"]:
            self.assertEqual(list(item.keys())[:2], ["label_ja", "id"])
        for item in data["facts"]["migration_notes"]:
            self.assertEqual(list(item.keys())[:2], ["label_ja", "id"])
        for item in data["validation_rules"]:
            self.assertEqual(list(item.keys())[:2], ["label_ja", "id"])

    def test_codemaker_contract_excludes_removed_legacy_shell_paths(self):
        data = yaml.safe_load((ROOT / "docs" / "architecture_rules.yml").read_text(encoding="utf-8"))
        contracts = data["facts"]["codemaker_bundle_contracts"]
        bundle = next(item for item in contracts if item["id"] == "codemaker_non_scene_bundle")
        required_paths = bundle["required_paths"]

        self.assertNotIn("src/app.py", required_paths)
        self.assertNotIn("src/core/scene_manager.py", required_paths)

    def test_run_checker_executes_deterministic_rules_and_skips_others(self):
        checker = load_checker_module()

        result = checker.run_checker(ROOT, ROOT / "docs" / "architecture_rules.yml")

        self.assertTrue(result["run_ok"])
        self.assertEqual(result["summary"]["total_rules"], 9)
        self.assertEqual(result["summary"]["executed_rules"], 7)
        self.assertEqual(result["summary"]["skipped_rules"], 2)

        by_rule = {item["rule_id"]: item for item in result["results"]}
        self.assertEqual(by_rule["runtime_entry_chain"]["status"], "ok")
        self.assertEqual(by_rule["dist_not_source"]["status"], "ok")
        self.assertEqual(by_rule["generated_files_edit_policy"]["status"], "ok")
        self.assertEqual(by_rule["codemaker_manifest_non_scene_paths"]["status"], "ok")
        self.assertEqual(by_rule["build_runbook_paths"]["status"], "ok")
        self.assertEqual(by_rule["scene_mvp_boundary"]["status"], "ok")
        self.assertEqual(by_rule["shared_service_vs_state_boundary"]["status"], "ok")
        self.assertEqual(by_rule["code_maker_primary_editor"]["status"], "skipped")
        self.assertEqual(by_rule["pyxres_source_of_truth"]["status"], "skipped")
        self.assertEqual(
            by_rule["scene_mvp_boundary"]["coverage"]["deterministic_review"],
            "implemented",
        )
        self.assertEqual(
            by_rule["shared_service_vs_state_boundary"]["coverage"]["deterministic_review"],
            "implemented",
        )

    def test_run_checker_reports_coverage_review(self):
        checker = load_checker_module()

        result = checker.run_checker(ROOT, ROOT / "docs" / "architecture_rules.yml")

        self.assertEqual(
            result["coverage_review"]["mode_counts"],
            {
                "deterministic": 7,
                "llm_assisted": 1,
                "manual": 1,
            },
        )
        self.assertEqual(result["coverage_review"]["deterministic_candidate_rule_ids"], [])
        self.assertEqual(result["coverage_review"]["next_checker_units"], [])
        self.assertEqual(result["coverage_review"]["repair_candidate_rule_ids"], [])
        self.assertEqual(
            result["coverage_review"]["repair_implemented_rule_ids"],
            [
                "runtime_entry_chain",
                "dist_not_source",
                "generated_files_edit_policy",
                "codemaker_manifest_non_scene_paths",
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
        self.assertEqual(payload["summary"]["executed_rules"], 7)
        self.assertEqual(payload["summary"]["skipped_rules"], 2)

    def test_run_checker_warns_when_codemaker_required_path_missing_from_manifest(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "tools").mkdir(parents=True, exist_ok=True)
            (repo_root / "src" / "shared" / "services").mkdir(parents=True, exist_ok=True)
            (repo_root / "src" / "shared" / "ui").mkdir(parents=True, exist_ok=True)
            (repo_root / "tools" / "codemaker_manifest.txt").write_text(
                "src/shared/services/input_bindings.py\n",
                encoding="utf-8",
            )
            (repo_root / "src" / "shared" / "services" / "input_bindings.py").write_text(
                "# ok\n",
                encoding="utf-8",
            )
            (repo_root / "src" / "shared" / "ui" / "text_renderer.py").write_text(
                "# missing from manifest\n",
                encoding="utf-8",
            )

            rules_path = repo_root / "architecture_rules.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    {
                        "meta": {"document_id": "test"},
                        "facts": {
                            "tree": {"path": ".", "kind": "root", "children": []},
                            "codemaker_bundle_contracts": [
                                {
                                    "id": "codemaker_non_scene_bundle",
                                    "manifest_path": "tools/codemaker_manifest.txt",
                                    "required_paths": [
                                        "src/shared/services/input_bindings.py",
                                        "src/shared/ui/text_renderer.py",
                                    ],
                                }
                            ],
                        },
                        "validation_rules": [
                            {
                                "id": "codemaker_manifest_non_scene_paths",
                                "summary": "bundle support files stay in manifest",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {
                                    "paths": [
                                        "tools/codemaker_manifest.txt",
                                        "architecture_rules.yml",
                                    ]
                                },
                                "evidence": {
                                    "checks": ["codemaker_manifest_includes_required_paths"]
                                },
                                "message": "codemaker manifest drift",
                                "suggested_actions": ["restore missing manifest paths"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    guardian_autofix="implemented",
                                ),
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        by_rule = {item["rule_id"]: item for item in result["results"]}
        self.assertEqual(
            by_rule["codemaker_manifest_non_scene_paths"]["failed_checks"],
            ["codemaker_manifest_includes_required_paths"],
        )
        self.assertEqual(
            by_rule["codemaker_manifest_non_scene_paths"]["observed"],
            {"missing_paths": ["src/shared/ui/text_renderer.py"]},
        )

    def test_run_checker_warns_when_scene_boundary_is_broken(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            scene_dir = repo_root / "src" / "scenes" / "title"
            scene_dir.mkdir(parents=True, exist_ok=True)
            (scene_dir / "model.py").write_text("import pyxel\npyxel.text(0, 0, 'x', 7)\n", encoding="utf-8")
            (scene_dir / "presenter.py").write_text("# ok\n", encoding="utf-8")
            (scene_dir / "view.py").write_text("# ok\n", encoding="utf-8")
            (scene_dir / "scene.py").write_text("# ok\n", encoding="utf-8")

            rules_path = repo_root / "architecture_rules.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    {
                        "meta": {"document_id": "test"},
                        "facts": {"tree": {"path": ".", "kind": "root", "children": []}},
                        "validation_rules": [
                            {
                                "id": "scene_mvp_boundary",
                                "summary": "scene boundary",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["src/scenes"]},
                                "evidence": {"checks": ["scene_static_boundary_checks"]},
                                "message": "scene boundary drift",
                                "suggested_actions": ["fix scene boundary"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    guardian_autofix="not_recommended",
                                ),
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        by_rule = {item["rule_id"]: item for item in result["results"]}
        self.assertEqual(
            by_rule["scene_mvp_boundary"]["failed_checks"],
            ["scene_static_boundary_checks"],
        )
        self.assertIn("model.py", by_rule["scene_mvp_boundary"]["message"])

    def test_run_checker_warns_when_shared_boundary_is_broken(self):
        checker = load_checker_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            state_dir = repo_root / "src" / "shared" / "state"
            services_dir = repo_root / "src" / "shared" / "services"
            state_dir.mkdir(parents=True, exist_ok=True)
            services_dir.mkdir(parents=True, exist_ok=True)
            (state_dir / "player_model.py").write_text("import pyxel\npyxel.text(0, 0, 'x', 7)\n", encoding="utf-8")
            (services_dir / "player_state.py").write_text("# shim\n", encoding="utf-8")
            (services_dir / "item_use.py").write_text("# shim\n", encoding="utf-8")

            rules_path = repo_root / "architecture_rules.yml"
            rules_path.write_text(
                yaml.safe_dump(
                    {
                        "meta": {"document_id": "test"},
                        "facts": {
                            "tree": {
                                "path": ".",
                                "kind": "root",
                                "children": [
                                    {
                                        "path": "src",
                                        "kind": "directory",
                                        "children": [
                                            {
                                                "path": "src/shared",
                                                "kind": "directory",
                                                "children": [
                                                    {
                                                        "path": "src/shared/services",
                                                        "kind": "directory",
                                                        "children": [
                                                            {
                                                                "path": "src/shared/services/player_state.py",
                                                                "kind": "file",
                                                                "status": "legacy",
                                                                "role": "legacy_player_snapshot",
                                                            },
                                                            {
                                                                "path": "src/shared/services/item_use.py",
                                                                "kind": "file",
                                                                "status": "legacy",
                                                                "role": "legacy_item_use_bridge",
                                                            },
                                                        ],
                                                    },
                                                    {
                                                        "path": "src/shared/state",
                                                        "kind": "directory",
                                                        "children": [
                                                            {
                                                                "path": "src/shared/state/player_model.py",
                                                                "kind": "file",
                                                                "status": "active",
                                                                "role": "player_source_of_truth",
                                                            }
                                                        ],
                                                    },
                                                ],
                                            }
                                        ],
                                    }
                                ],
                            }
                        },
                        "validation_rules": [
                            {
                                "id": "shared_service_vs_state_boundary",
                                "summary": "shared boundary",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["src/shared/services", "src/shared/state"]},
                                "evidence": {"checks": ["shared_directory_role_checks"]},
                                "message": "shared boundary drift",
                                "suggested_actions": ["fix shared boundary"],
                                "coverage": coverage_metadata(
                                    deterministic_review="implemented",
                                    guardian_autofix="not_recommended",
                                ),
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = checker.run_checker(repo_root, rules_path)

        self.assertTrue(result["run_ok"])
        self.assertTrue(result["has_warnings"])
        by_rule = {item["rule_id"]: item for item in result["results"]}
        self.assertEqual(
            by_rule["shared_service_vs_state_boundary"]["failed_checks"],
            ["shared_directory_role_checks"],
        )
        self.assertIn("player_model.py", by_rule["shared_service_vs_state_boundary"]["message"])

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
