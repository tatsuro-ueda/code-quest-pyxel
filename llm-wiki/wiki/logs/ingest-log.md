# Ingest Log

## [2026-05-24] ingest | G12 code-maker.zip rebuild

- source_id: `2026-04-12-g12-rebuild-codemaker-zip`
- source_path: `llm-wiki/raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md`
- created_pages:
  - `llm-wiki/wiki/summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md`
- updated_pages:
  - `llm-wiki/wiki/areas/single-source-of-truth-and-golden-path.md`
  - `llm-wiki/wiki/areas/guardrail-layering-and-ai-change-boundaries.md`
  - `llm-wiki/wiki/areas/repository-operating-structure.md`
  - `llm-wiki/wiki/areas/platform-sharing-and-approval-ops.md`
  - `llm-wiki/wiki/indexes/master-index.md`
- related_page_count: 4
- risks:
  - packaging の学びは入ったが、zip freshness を定期的に点検する自動 gate まではまだ無い
- notes:
  - Code Maker artifact freshness を SSoT、guardrail、repository、platform の各 page へ波及させた

## [2026-05-24] ingest | G15 test pinning

- source_id: `2026-04-12-g15-test-pinning`
- source_path: `llm-wiki/raw/tasknotes/done/20260412-g15-test-pinning.md`
- created_pages:
  - `llm-wiki/wiki/summaries/tasknotes/done/20260412-g15-test-pinning-summary.md`
- updated_pages:
  - `llm-wiki/wiki/areas/guardrails-protect-the-loop.md`
  - `llm-wiki/wiki/areas/no-silent-failure-and-migration-safety.md`
  - `llm-wiki/wiki/areas/guardrail-layering-and-ai-change-boundaries.md`
  - `llm-wiki/wiki/indexes/master-index.md`
- related_page_count: 3
- risks:
  - CI が無いままでは、同種の broken test lane が次も長期間放置される可能性がある
- notes:
  - pytest lane 復旧を guardrail、migration safety、layering の各 page へ接続した

## [2026-05-24] ingest | Guardrails 1 SSoT + Codegen

- source_id: `2026-04-12-guardrails-1-ssot-codegen`
- source_path: `llm-wiki/raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md`
- created_pages:
  - `llm-wiki/wiki/summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md`
- updated_pages:
  - `llm-wiki/wiki/areas/single-source-of-truth-and-golden-path.md`
  - `llm-wiki/wiki/areas/guardrail-layering-and-ai-change-boundaries.md`
  - `llm-wiki/wiki/areas/repository-operating-structure.md`
  - `llm-wiki/wiki/areas/guardrails-protect-the-loop.md`
  - `llm-wiki/wiki/indexes/master-index.md`
- related_page_count: 4
- risks:
  - codegen lane は入ったが、`gen` 実行忘れを防ぐ hook や CI は別 guardrail として残っている
- notes:
  - YAML SSoT、generated code、loader 境界の structural guardrail を既存 area pages へ接続した

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

## [2026-05-23] ingest | Customer Jobs

- source_id: `customer-jobs`
- source_path: `llm-wiki/raw/knowledge/docs/customer-jobs.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/customer-jobs-summary.md`
  - `llm-wiki/wiki/areas/continuous-experience-loop.md`
  - `llm-wiki/wiki/areas/parent-support-without-control.md`
  - `llm-wiki/wiki/areas/low-friction-sharing.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
- related_page_count: 3
- risks:
  - customer jobs source は価値仮説が中心で、具体 feature へ落とすには journeys や requirements との併読が必要
- notes:
  - 子どもの連続体験、親の支え方、低摩擦共有の 3 テーマへ波及させた

## [2026-05-23] ingest | Customer Journeys

- source_id: `customer-journeys`
- source_path: `llm-wiki/raw/knowledge/docs/customer-journeys.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/customer-journeys-summary.md`
  - `llm-wiki/wiki/areas/fast-feedback-development-loop.md`
  - `llm-wiki/wiki/areas/approval-loop-and-child-agency.md`
  - `llm-wiki/wiki/areas/guardrails-protect-the-loop.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
  - `llm-wiki/wiki/areas/continuous-experience-loop.md`
  - `llm-wiki/wiki/areas/parent-support-without-control.md`
  - `llm-wiki/wiki/areas/low-friction-sharing.md`
- related_page_count: 6
- risks:
  - journey 文書は具体例が多いため、個別 CJ のニュアンスは summary や area だけでは取り切れない
- notes:
  - Buy / Make、承認ループ、ガードレール、共有 loop を area pages へ展開した

## [2026-05-23] ingest | Framework Rule

- source_id: `framework-rule`
- source_path: `llm-wiki/raw/knowledge/docs/framework-rule.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/framework-rule-summary.md`
  - `llm-wiki/wiki/areas/single-source-of-truth-and-golden-path.md`
  - `llm-wiki/wiki/areas/view-presenter-model-boundaries.md`
  - `llm-wiki/wiki/areas/no-silent-failure-and-migration-safety.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
  - `llm-wiki/wiki/areas/guardrails-protect-the-loop.md`
- related_page_count: 4
- risks:
  - framework-rule は規約本体で密度が高く、実運用時は checklist や AGENTS と併読が必要
- notes:
  - SSoT、Golden Path、M1-M5 の境界を独立 area pages として抽出した

## [2026-05-23] ingest | Old Customer Jobs

- source_id: `old-customer-jobs`
- source_path: `llm-wiki/raw/knowledge/docs/old-customer-jobs.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/old-customer-jobs-summary.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
  - `llm-wiki/wiki/areas/continuous-experience-loop.md`
  - `llm-wiki/wiki/areas/parent-support-without-control.md`
  - `llm-wiki/wiki/areas/low-friction-sharing.md`
  - `llm-wiki/wiki/areas/fast-feedback-development-loop.md`
- related_page_count: 4
- risks:
  - current customer-jobs より古い整理なので、現行文書との差分は「矛盾」より「背景動機」として扱う方が安全
- notes:
  - 親は AI 翻訳者であって決定者ではない、という境界を既存 page 群へ補強した

## [2026-05-23] ingest | Product Requirements AV

- source_id: `product-requirements-av`
- source_path: `llm-wiki/raw/knowledge/docs/product-requirements-av.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/product-requirements-av-summary.md`
  - `llm-wiki/wiki/areas/audio-feedback-and-polish.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
- related_page_count: 2
- risks:
  - zone 固有 BGM や Sound editor end-to-end の未達が残る
- notes:
  - AV を `authoring 境界 + scene feedback` の 2 軸で要約した

## [2026-05-23] ingest | Product Requirements Battle

- source_id: `product-requirements-battle`
- source_path: `llm-wiki/raw/knowledge/docs/product-requirements-battle.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/product-requirements-battle-summary.md`
  - `llm-wiki/wiki/areas/battle-balance-and-spell-design.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
- related_page_count: 2
- risks:
  - speed 目標はあるが automated guarantee ではない
- notes:
  - 敵、呪文、全体調整を `安全な変更単位` として抽出した

## [2026-05-23] ingest | Product Requirements Guardrails

- source_id: `product-requirements-guardrails`
- source_path: `llm-wiki/raw/knowledge/docs/product-requirements-guardrails.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/product-requirements-guardrails-summary.md`
  - `llm-wiki/wiki/areas/guardrail-layering-and-ai-change-boundaries.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
  - `llm-wiki/wiki/areas/guardrails-protect-the-loop.md`
  - `llm-wiki/wiki/areas/view-presenter-model-boundaries.md`
  - `llm-wiki/wiki/areas/single-source-of-truth-and-golden-path.md`
  - `llm-wiki/wiki/areas/no-silent-failure-and-migration-safety.md`
- related_page_count: 6
- risks:
  - 文書は目標状態を含むため、現状との差分管理を継続しないと stale になりやすい
- notes:
  - layer 分類、startup gate、resource boundary を既存 guardrail pages へ波及させた

## [2026-05-23] ingest | Product Requirements Map

- source_id: `product-requirements-map`
- source_path: `llm-wiki/raw/knowledge/docs/product-requirements-map.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/product-requirements-map-summary.md`
  - `llm-wiki/wiki/areas/map-authorship-and-tile-expression.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
- related_page_count: 2
- risks:
  - editor/runtime 一致の未達が残るため、将来 query で gap が出やすい
- notes:
  - tile authorship を `visible meaning` と `movement rule` の一致として整理した

## [2026-05-23] ingest | Product Requirements Narrative

- source_id: `product-requirements-narrative`
- source_path: `llm-wiki/raw/knowledge/docs/product-requirements-narrative.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/product-requirements-narrative-summary.md`
  - `llm-wiki/wiki/areas/narrative-branching-and-player-guidance.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
- related_page_count: 2
- risks:
  - generic guidance UI は未実装で、一部は concept 先行の要件である
- notes:
  - dialogue、guidance、branching、ending ownership を 1 本の narrative lane に整理した

## [2026-05-23] ingest | Product Requirements Platform

- source_id: `product-requirements-platform`
- source_path: `llm-wiki/raw/knowledge/docs/product-requirements-platform.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/product-requirements-platform-summary.md`
  - `llm-wiki/wiki/areas/platform-sharing-and-approval-ops.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
  - `llm-wiki/wiki/areas/approval-loop-and-child-agency.md`
  - `llm-wiki/wiki/areas/parent-support-without-control.md`
  - `llm-wiki/wiki/areas/low-friction-sharing.md`
- related_page_count: 5
- risks:
  - environment 差分や description 自動生成は今後も stale 化しやすい
- notes:
  - sharing、approval、Code Maker carry-out/carry-back を 1 本の ops lane に集約した

## [2026-05-23] ingest | Repository Structure

- source_id: `repository-structure`
- source_path: `llm-wiki/raw/knowledge/docs/repository-structure.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/repository-structure-summary.md`
  - `llm-wiki/wiki/areas/repository-operating-structure.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
  - `llm-wiki/wiki/areas/view-presenter-model-boundaries.md`
  - `llm-wiki/wiki/areas/single-source-of-truth-and-golden-path.md`
  - `llm-wiki/wiki/areas/no-silent-failure-and-migration-safety.md`
  - `llm-wiki/wiki/areas/guardrails-protect-the-loop.md`
- related_page_count: 6
- risks:
  - 行数や scene 数などの時点情報は定期点検しないと stale になりやすい
- notes:
  - repo map を guardrail と runtime entry の文脈へ接続した

## [2026-05-23] ingest | Story Concepts

- source_id: `story-concepts`
- source_path: `llm-wiki/raw/knowledge/docs/story-concepts.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/story-concepts-summary.md`
  - `llm-wiki/wiki/areas/story-theme-and-landmark-symbolism.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
- related_page_count: 2
- risks:
  - story spine は text quality 依存が大きく、 summary だけで tone を代替しきれない
- notes:
  - zone arc、Glitch、world tree / tower symbolism を cross-page theme に抽出した

## [2026-05-23] ingest | UX Policy

- source_id: `ux-policy`
- source_path: `llm-wiki/raw/knowledge/docs/ux-policy.md`
- created_pages:
  - `llm-wiki/wiki/summaries/knowledge/ux-policy-summary.md`
  - `llm-wiki/wiki/areas/child-readable-ux-and-parent-assist.md`
- updated_pages:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/logs/source-inbox.md`
  - `llm-wiki/wiki/areas/parent-support-without-control.md`
  - `llm-wiki/wiki/areas/low-friction-sharing.md`
- related_page_count: 4
- risks:
  - policy 自体は短く、 feature 判断時は platform / narrative と併読が前提になる
- notes:
  - readability、one next action、safe confirmation、parent assist を横断 area へ整理した
