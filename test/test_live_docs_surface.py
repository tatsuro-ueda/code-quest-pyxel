from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

OBSOLETE_DOC_FILES = [
    ROOT / "docs" / "architecture_rules.yml",
    ROOT / "docs" / "stakeholder_voices.yml",
]

OBSOLETE_TOOL_FILES = [
    ROOT / "tools" / "check_architecture_rules.py",
    ROOT / "tools" / "fix_architecture_rules.py",
    ROOT / "tools" / "repair_architecture_rules.py",
    ROOT / "tools" / "report_source_trace_coverage.py",
    ROOT / "tools" / "check_stakeholder_voices.py",
    ROOT / "tools" / "fix_stakeholder_voices.py",
    ROOT / "tools" / "repair_stakeholder_voices.py",
    ROOT / "tools" / "architecture_rules" / "__init__.py",
    ROOT / "tools" / "architecture_rules" / "check_architecture_rules.py",
    ROOT / "tools" / "architecture_rules" / "fix_architecture_rules.py",
    ROOT / "tools" / "architecture_rules" / "repair_architecture_rules.py",
    ROOT / "tools" / "stakeholder_voices" / "__init__.py",
    ROOT / "tools" / "stakeholder_voices" / "check_stakeholder_voices.py",
    ROOT / "tools" / "stakeholder_voices" / "fix_stakeholder_voices.py",
    ROOT / "tools" / "stakeholder_voices" / "repair_stakeholder_voices.py",
    ROOT / "tools" / "stakeholder_voices" / "source_trace_coverage.py",
]

LIVE_DOC_FILES = [
    ROOT / "README.md",
    ROOT / "docs" / "repository-structure.md",
    ROOT / "test" / "test_cjg_framework_rule_guards.py",
]

OBSOLETE_REFERENCES = [
    "architecture_rules.yml",
    "stakeholder_voices.yml",
    "check_architecture_rules.py",
    "fix_architecture_rules.py",
    "repair_architecture_rules.py",
    "check_stakeholder_voices.py",
    "fix_stakeholder_voices.py",
    "repair_stakeholder_voices.py",
    "report_source_trace_coverage.py",
]


class TestLiveDocsSurface(unittest.TestCase):
    def test_obsolete_yaml_docs_are_gone(self):
        missing = [path for path in OBSOLETE_DOC_FILES if path.exists()]
        self.assertEqual(missing, [], f"obsolete YAML docs still exist: {missing}")

    def test_obsolete_docs_toolchain_files_are_gone(self):
        remaining = [path for path in OBSOLETE_TOOL_FILES if path.exists()]
        self.assertEqual(
            remaining,
            [],
            f"obsolete docs toolchain files still exist: {remaining}",
        )

    def test_live_docs_do_not_advertise_the_removed_toolchain(self):
        offenders: list[str] = []
        for path in LIVE_DOC_FILES:
            text = path.read_text(encoding="utf-8")
            for needle in OBSOLETE_REFERENCES:
                if needle in text:
                    offenders.append(f"{path.relative_to(ROOT)}: {needle}")
        self.assertEqual(offenders, [], f"live docs still reference removed toolchain: {offenders}")


if __name__ == "__main__":
    unittest.main()
