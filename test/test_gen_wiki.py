from __future__ import annotations

import shutil
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))


def load_gen_wiki_module():
    try:
        import gen_wiki
    except ImportError as exc:  # pragma: no cover - TDD red path
        raise AssertionError(f"tools/gen_wiki.py is missing: {exc}") from exc
    return gen_wiki


class GenerateWikiTest(unittest.TestCase):
    def test_generate_wiki_copies_markdown_sources_and_writes_mirrored_summaries(self):
        gen_wiki = load_gen_wiki_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)
            (repo_root / "steering" / "done").mkdir(parents=True, exist_ok=True)

            knowledge_path = repo_root / "docs" / "customer-jobs.md"
            knowledge_path.write_text(
                textwrap.dedent(
                    """
                    # 顧客のジョブ

                    すぐに価値へ到達したい。

                    ## 子ども

                    - 自分で作った感を失いたくない

                    ## 親

                    - 子どもの熱が冷める前に反映したい
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )
            tasknote_path = repo_root / "steering" / "done" / "example-tasknote.md"
            tasknote_path.write_text(
                textwrap.dedent(
                    """
                    ---
                    status: done
                    ---

                    # 代表タスクノート

                    spot ingest の形だけ先に決める。

                    ## Result

                    - raw と summary を mirror する
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            wiki_root = repo_root / "wiki"
            result = gen_wiki.generate_wiki(
                knowledge_paths=["docs/customer-jobs.md"],
                tasknote_paths=["steering/done/example-tasknote.md"],
                repo_root=repo_root,
                wiki_root=wiki_root,
                today="2026-05-22",
            )

            raw_knowledge = wiki_root / "raw" / "knowledge" / "docs" / "customer-jobs.md"
            raw_tasknote = wiki_root / "raw" / "tasknotes" / "steering" / "done" / "example-tasknote.md"
            knowledge_summary = (
                wiki_root
                / "wiki"
                / "summaries"
                / "knowledge"
                / "docs"
                / "customer-jobs-summary.md"
            )
            tasknote_summary = (
                wiki_root
                / "wiki"
                / "summaries"
                / "tasknotes"
                / "steering"
                / "done"
                / "example-tasknote-summary.md"
            )

            self.assertEqual(
                result["raw_paths"],
                [raw_knowledge, raw_tasknote],
            )
            self.assertEqual(
                result["summary_paths"],
                [knowledge_summary, tasknote_summary],
            )
            self.assertEqual(raw_knowledge.read_text(encoding="utf-8"), knowledge_path.read_text(encoding="utf-8"))
            self.assertEqual(raw_tasknote.read_text(encoding="utf-8"), tasknote_path.read_text(encoding="utf-8"))

            knowledge_text = knowledge_summary.read_text(encoding="utf-8")
            self.assertIn("source: raw/knowledge/docs/customer-jobs.md", knowledge_text)
            self.assertIn("source_type: knowledge", knowledge_text)
            self.assertIn("last_ingested: 2026-05-22", knowledge_text)
            self.assertIn("size_class: small", knowledge_text)
            self.assertIn("# 顧客のジョブ", knowledge_text)
            self.assertIn("## TL;DR", knowledge_text)
            self.assertIn("## 主要トピック", knowledge_text)
            self.assertIn("- 子ども", knowledge_text)
            self.assertIn("- 親", knowledge_text)
            self.assertIn("## キーワード", knowledge_text)
            self.assertIn("customer-jobs", knowledge_text)
            self.assertIn("## 注意点", knowledge_text)

            tasknote_text = tasknote_summary.read_text(encoding="utf-8")
            self.assertIn("source: raw/tasknotes/steering/done/example-tasknote.md", tasknote_text)
            self.assertIn("source_type: tasknote", tasknote_text)
            self.assertIn("# 代表タスクノート", tasknote_text)
            self.assertIn("- Result", tasknote_text)

    def test_generate_wiki_summarizes_yaml_top_level_keys(self):
        gen_wiki = load_gen_wiki_module()

        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / "docs").mkdir(parents=True, exist_ok=True)

            yaml_path = repo_root / "docs" / "stakeholder_voices.yml"
            yaml_path.write_text(
                textwrap.dedent(
                    """
                    meta:
                      document_id: stakeholder_voices
                    facts:
                      stakeholders:
                        - id: st_child_user
                          label: 子ども
                      requests:
                        - id: rq_child_edit_ownership
                          summary: Code Maker で触った内容がそのままゲームに出てほしい
                    validation_rules:
                      - id: sample_rule
                        summary: sample
                    """
                ).strip()
                + "\n",
                encoding="utf-8",
            )

            wiki_root = repo_root / "wiki"
            result = gen_wiki.generate_wiki(
                knowledge_paths=["docs/stakeholder_voices.yml"],
                tasknote_paths=[],
                repo_root=repo_root,
                wiki_root=wiki_root,
                today="2026-05-22",
            )

            raw_yaml = wiki_root / "raw" / "knowledge" / "docs" / "stakeholder_voices.yml"
            summary_yaml = (
                wiki_root
                / "wiki"
                / "summaries"
                / "knowledge"
                / "docs"
                / "stakeholder_voices-summary.md"
            )

            self.assertEqual(result["raw_paths"], [raw_yaml])
            self.assertEqual(result["summary_paths"], [summary_yaml])

            summary_text = summary_yaml.read_text(encoding="utf-8")
            self.assertIn("source: raw/knowledge/docs/stakeholder_voices.yml", summary_text)
            self.assertIn("# stakeholder_voices", summary_text)
            self.assertIn("- meta", summary_text)
            self.assertIn("- facts", summary_text)
            self.assertIn("- validation_rules", summary_text)
            self.assertIn("stakeholders", summary_text)
            self.assertIn("requests", summary_text)


if __name__ == "__main__":
    unittest.main()
