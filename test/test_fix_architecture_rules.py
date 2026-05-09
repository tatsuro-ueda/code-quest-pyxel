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


def load_fixer_module():
    try:
        import fix_architecture_rules
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/fix_architecture_rules.py is missing: {exc}") from exc
    return fix_architecture_rules


def tree_node(path: str, kind: str, **extra):
    node = {"path": path, "kind": kind}
    node.update(extra)
    return node


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


class FixArchitectureRulesTest(unittest.TestCase):
    def test_fix_cli_runs_clean_on_real_repo(self):
        completed = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "fix_architecture_rules.py")],
            capture_output=True,
            text=True,
            cwd=ROOT,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "OK")
        self.assertTrue(payload["check"]["run_ok"])
        self.assertFalse(payload["check"]["has_warnings"])
        self.assertEqual(payload["applied_fixes"], [])

    def test_write_yaml_inserts_blank_lines_between_path_entries(self):
        fixer = load_fixer_module()

        with tempfile.TemporaryDirectory() as tmp:
            rules_path = Path(tmp) / "architecture_rules.yml"
            fixer.write_yaml(
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
                            "coverage": coverage_metadata(
                                deterministic_review="keep_manual",
                                repair_autofix="not_recommended",
                            ),
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

    def test_run_fixer_applies_generated_rule_fix_once(self):
        fixer = load_fixer_module()

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

            result = fixer.run_fixer(repo_root, rules_path)
            fixed_yaml = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
            generated_text = (repo_root / "src" / "generated" / "dialogue.py").read_text(encoding="utf-8")

        self.assertEqual(result["status"], "FIXED")
        self.assertTrue(result["check"]["has_warnings"])
        self.assertGreaterEqual(len(result["applied_fixes"]), 1)
        generated_node = fixed_yaml["facts"]["tree"]["children"][2]["children"][0]["children"][0]
        self.assertFalse(generated_node["hand_editable"])
        self.assertIn("DATA = []", generated_text)


if __name__ == "__main__":
    unittest.main()
