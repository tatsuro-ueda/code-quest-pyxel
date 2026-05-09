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


def load_guardian_module():
    try:
        import architecture_guardian
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/architecture_guardian.py is missing: {exc}") from exc
    return architecture_guardian


def tree_node(path: str, kind: str, **extra):
    node = {"path": path, "kind": kind}
    node.update(extra)
    return node


class ArchitectureGuardianTest(unittest.TestCase):
    def test_guardian_cli_runs_clean_on_real_repo(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "architecture_guardian.py")],
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

    def test_write_yaml_inserts_blank_lines_between_path_entries(self):
        guardian = load_guardian_module()

        with tempfile.TemporaryDirectory() as tmp:
            rules_path = Path(tmp) / "architecture_rules.yml"
            guardian.write_yaml(
                rules_path,
                {
                    "meta": {"document_id": "test"},
                    "facts": {
                        "tree": {
                            "path": ".",
                            "kind": "root",
                            "children": [
                                tree_node("alpha.txt", "file", summary="first file"),
                                tree_node("beta.txt", "file", summary="second file"),
                                tree_node(
                                    "src",
                                    "directory",
                                    children=[
                                        tree_node("src/a.py", "file", summary="nested first"),
                                        tree_node("src/b.py", "file", summary="nested second"),
                                    ],
                                ),
                            ],
                        }
                    },
                    "validation_rules": [
                        {
                            "id": "sample_rule",
                            "summary": "sample",
                            "severity": "warning",
                            "enforcement": {"mode": "manual"},
                            "scope": {"paths": ["alpha.txt"]},
                            "evidence": {"checks": ["manual_check"]},
                            "message": "sample message",
                            "suggested_actions": ["sample action"],
                            "coverage": {
                                "deterministic_review": "keep_manual",
                                "next_checker_unit": None,
                                "guardian_autofix": "not_recommended",
                                "rationale": "sample",
                            },
                        }
                    ],
                },
            )

            text = rules_path.read_text(encoding="utf-8")

            self.assertRegex(text, r"children:\n\n\s+- path: alpha\.txt")
            self.assertRegex(text, r"summary: first file\n\n\s+- path: beta\.txt")
            self.assertRegex(text, r"children:\n\n\s+- path: src/a\.py")
            self.assertRegex(text, r"summary: nested first\n\n\s+- path: src/b\.py")
            self.assertRegex(text, r"validation_rules:\n\n\s+- id: sample_rule")

    def test_guardian_autofixes_generated_rule_until_clean(self):
        guardian = load_guardian_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "assets").mkdir(parents=True, exist_ok=True)
            (repo_root / "src" / "generated").mkdir(parents=True, exist_ok=True)
            (repo_root / "tools").mkdir(parents=True, exist_ok=True)
            (repo_root / "assets" / "dialogue.yaml").write_text("lines: []\n", encoding="utf-8")
            (repo_root / "src" / "generated" / "dialogue.py").write_text("# stale\n", encoding="utf-8")
            (repo_root / "tools" / "gen_data.py").write_text(
                textwrap.dedent(
                    """
                    from pathlib import Path

                    root = Path(__file__).resolve().parent.parent
                    (root / "src" / "generated" / "dialogue.py").write_text(
                        "# regenerated\\nDATA = []\\n",
                        encoding="utf-8",
                    )
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

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
                                    tree_node("assets", "directory", children=[tree_node("assets/dialogue.yaml", "file", status="active")]),
                                    tree_node("tools", "directory", children=[tree_node("tools/gen_data.py", "file", status="active")]),
                                    tree_node(
                                        "src",
                                        "directory",
                                        children=[
                                            tree_node(
                                                "src/generated",
                                                "directory",
                                                children=[
                                                    tree_node(
                                                        "src/generated/dialogue.py",
                                                        "file",
                                                        id="generated_dialogue",
                                                        status="generated",
                                                        hand_editable=True,
                                                        generated_from=["assets/dialogue.yaml"],
                                                    )
                                                ],
                                            )
                                        ],
                                    ),
                                ],
                            }
                        },
                        "validation_rules": [
                            {
                                "id": "generated_files_edit_policy",
                                "summary": "generated must be regenerated",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["src/generated", "assets", "tools/gen_data.py"]},
                                "evidence": {"checks": ["generated_entries_mark_non_hand_editable_and_sources"]},
                                "message": "generated drift",
                                "suggested_actions": ["run gen_data"],
                                "coverage": {
                                    "deterministic_review": "implemented",
                                    "next_checker_unit": None,
                                    "guardian_autofix": "implemented",
                                    "rationale": "fixture",
                                },
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = guardian.run_guardian(repo_root, rules_path, max_cycles=5)

            self.assertEqual(result["status"], "AUTOFIXED")
            self.assertLessEqual(result["cycles"], 5)
            self.assertFalse(result["final_check"]["has_warnings"])
            fixed_yaml = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
            generated_node = fixed_yaml["facts"]["tree"]["children"][2]["children"][0]["children"][0]
            self.assertFalse(generated_node["hand_editable"])
            self.assertIn("DATA = []", (repo_root / "src" / "generated" / "dialogue.py").read_text(encoding="utf-8"))

    def test_guardian_returns_needs_human_when_issue_remains(self):
        guardian = load_guardian_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "src" / "runtime").mkdir(parents=True, exist_ok=True)
            (repo_root / "main.py").write_text("print('broken')\n", encoding="utf-8")
            (repo_root / "src" / "runtime" / "main_runtime.py").write_text(
                "# =====================================================================\n# ENTRY POINT\n# =====================================================================\n",
                encoding="utf-8",
            )
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
                                    tree_node("main.py", "file", role="wrapper", status="active"),
                                    tree_node(
                                        "src",
                                        "directory",
                                        children=[
                                            tree_node(
                                                "src/runtime",
                                                "directory",
                                                children=[
                                                    tree_node("src/runtime/main_runtime.py", "file", role="shim", status="active")
                                                ],
                                            )
                                        ],
                                    ),
                                ],
                            },
                            "entry_points": [
                                {
                                    "id": "runtime_entry_chain",
                                    "summary": "runtime chain",
                                    "paths": ["main.py", "src/runtime/main_runtime.py", "src/runtime/app.py"],
                                    "nodes": [
                                        {"id": "runtime_main_wrapper", "path": "main.py", "role": "wrapper", "status": "active"},
                                        {"id": "runtime_shim", "path": "src/runtime/main_runtime.py", "role": "shim", "status": "active"},
                                        {
                                            "id": "runtime_game",
                                            "path": "src/runtime/app.py",
                                            "symbol": "Game",
                                            "role": "application_root",
                                            "status": "active",
                                        },
                                    ],
                                }
                            ],
                        },
                        "validation_rules": [
                            {
                                "id": "runtime_entry_chain",
                                "summary": "runtime chain",
                                "severity": "warning",
                                "enforcement": {"mode": "deterministic"},
                                "scope": {"paths": ["main.py", "src/runtime/main_runtime.py", "src/runtime/app.py"]},
                                "evidence": {"checks": ["wrapper_chain_present"]},
                                "message": "runtime drift",
                                "suggested_actions": ["restore runtime entry chain"],
                                "coverage": {
                                    "deterministic_review": "implemented",
                                    "next_checker_unit": None,
                                    "guardian_autofix": "implemented",
                                    "rationale": "fixture",
                                },
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = guardian.run_guardian(repo_root, rules_path, max_cycles=5)

            self.assertEqual(result["status"], "NEEDS_HUMAN")
            self.assertLessEqual(result["cycles"], 5)
            self.assertTrue(result["final_check"]["has_warnings"])

    def test_guardian_autofixes_codemaker_manifest_missing_required_paths(self):
        guardian = load_guardian_module()

        with tempfile.TemporaryDirectory() as tmp:
            repo_root = Path(tmp)
            (repo_root / "tools").mkdir(parents=True, exist_ok=True)
            (repo_root / "src" / "shared" / "services").mkdir(parents=True, exist_ok=True)
            (repo_root / "src" / "shared" / "ui").mkdir(parents=True, exist_ok=True)

            manifest_path = repo_root / "tools" / "codemaker_manifest.txt"
            manifest_path.write_text(
                textwrap.dedent(
                    """
                    # --- 5. shared/services
                    src/shared/services/input_bindings.py
                    # --- 6. shared/ui
                    src/shared/ui/hud.py
                    # --- 7. scenes
                    """
                ).lstrip(),
                encoding="utf-8",
            )
            (repo_root / "src" / "shared" / "services" / "input_bindings.py").write_text(
                "# ok\n", encoding="utf-8"
            )
            (repo_root / "src" / "shared" / "services" / "debug_service.py").write_text(
                "# needs autofix\n", encoding="utf-8"
            )
            (repo_root / "src" / "shared" / "ui" / "hud.py").write_text(
                "# ok\n", encoding="utf-8"
            )
            (repo_root / "src" / "shared" / "ui" / "text_renderer.py").write_text(
                "# needs autofix\n", encoding="utf-8"
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
                                        "src/shared/services/debug_service.py",
                                        "src/shared/ui/hud.py",
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
                                "coverage": {
                                    "deterministic_review": "implemented",
                                    "next_checker_unit": None,
                                    "guardian_autofix": "implemented",
                                    "rationale": "fixture",
                                },
                            }
                        ],
                    },
                    allow_unicode=True,
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            result = guardian.run_guardian(repo_root, rules_path, max_cycles=5)

            self.assertEqual(result["status"], "AUTOFIXED")
            self.assertFalse(result["final_check"]["has_warnings"])
            manifest_text = manifest_path.read_text(encoding="utf-8")
            self.assertIn("src/shared/services/debug_service.py", manifest_text)
            self.assertIn("src/shared/ui/text_renderer.py", manifest_text)


if __name__ == "__main__":
    unittest.main()
