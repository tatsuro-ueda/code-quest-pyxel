# Ingest Log

## [2026-05-23] ingest | LLM Wiki

- source_id: `2026-04-04-karpathy-llm-wiki`
- source_path: `llm-wiki/raw/knowledge/2026-04-04-karpathy-llm-wiki.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md`
  - `llm-wiki/wiki/areas/persistent-wiki-vs-rag.md`
  - `llm-wiki/wiki/areas/ingest-query-lint-loop.md`
  - `llm-wiki/wiki/areas/schema-driven-wiki-maintainer.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
- related_page_count: 3
- risks:
  - optional tooling と image handling は source 1 本だけでは深掘り不足
- notes:
  - 初回 ingest の done 条件として raw / summary / index / related pages / ingest log を充足
