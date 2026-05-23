# wiki

`wiki/` is the repo-local home for LLM Wiki artifacts.

This tree is not a new source of truth.

- `docs/` and structured project sources remain canonical.
- `wiki/raw/` is a generated snapshot layer built from canonical inputs.
- `wiki/wiki/` contains derived summaries, indexes, query artifacts, and maintenance notes.
- `wiki/checklists/` contains derived checklist docs that can be queried from the wiki layer.

## Default Rules

- Do not hand-edit canonical project meaning in `wiki/`.
- Prefer generating `raw/knowledge/` from `docs/` rather than copying docs manually.
- Keep YAML snapshots as `.yml`; write their derived summaries as `*-summary.md`.
- Query work is read-only:
  - do not update `raw/` during query sessions
  - always return evidence links
  - if information is missing, say it is missing
  - if `raw/` looks stale, record the issue in `wiki/maintenance.md`
- Current rollout stays close to Karpathy's minimal pattern:
  - prefer `index.md` and `log.md` before adding repo-specific navigation layers
  - treat `areas/` as reserved/optional, not part of the active rollout yet

## Layout

```text
wiki/
├── README.md
├── raw/
│   ├── knowledge/
│   └── tasknotes/
├── wiki/
│   ├── summaries/
│   │   ├── knowledge/
│   │   └── tasknotes/
│   ├── indexes/
│   ├── query/
│   ├── candidates/
│   └── maintenance.md
└── checklists/
```

## Source Notes

- `steering/2026年5月22日 LLM Wiki shared packageを導入して自律実行ルートを固定する.md`
- `steering/done/2026年5月22日 練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md`
- `steering/llm-wiki/child-tasknotes/03-練習用プロジェクト向けLLM Wiki skeletonと命名ルールを置く.md`
