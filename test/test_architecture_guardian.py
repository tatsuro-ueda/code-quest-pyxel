from __future__ import annotations

import json
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


class ArchitectureGuardianTest(unittest.TestCase):
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
                            "generated": {
                                "entries": [
                                    {
                                        "id": "generated_dialogue",
                                        "path": "src/generated/dialogue.py",
                                        "status": "generated",
                                        "hand_editable": True,
                                        "generated_from": ["assets/dialogue.yaml"],
                                    }
                                ]
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
            self.assertFalse(fixed_yaml["facts"]["generated"]["entries"][0]["hand_editable"])
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
                            "runtime": {
                                "entry_chain": [
                                    {"id": "runtime_main_wrapper", "path": "main.py", "role": "wrapper", "status": "active"},
                                    {"id": "runtime_shim", "path": "src/runtime/main_runtime.py", "role": "shim", "status": "active"},
                                    {
                                        "id": "runtime_game",
                                        "path": "src/runtime/app.py",
                                        "symbol": "Game",
                                        "role": "application_root",
                                        "status": "active",
                                    },
                                ]
                            }
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


if __name__ == "__main__":
    unittest.main()
