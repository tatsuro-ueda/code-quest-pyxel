# Master Index

この index は `llm-wiki/wiki/` の入口です。query 時はまずここを読み、関連ページへ進みます。

## Sources

- [Karpathy LLM Wiki Summary](../summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md): persistent wiki、ingest、query、lint、schema の核をまとめた summary
- [Karpathy LLM Wiki Raw](../../raw/knowledge/2026-04-04-karpathy-llm-wiki.md): 2026-04-04 公開の元 source
- [Customer Jobs Summary](../summaries/knowledge/customer-jobs-summary.md): 子ども、親、友達の顧客ジョブと競合理解をまとめた summary
- [Customer Jobs Raw](../../raw/knowledge/docs/customer-jobs.md): 顧客ジョブの正本 source
- [Customer Journeys Summary](../summaries/knowledge/customer-journeys-summary.md): Buy/Make、journey 群、承認ループ、ガードレールをまとめた summary
- [Customer Journeys Raw](../../raw/knowledge/docs/customer-journeys.md): カスタマージャーニー設計の正本 source
- [Framework Rule Summary](../summaries/knowledge/framework-rule-summary.md): SSoT、Golden Path、M1-M5 をまとめた summary
- [Framework Rule Raw](../../raw/knowledge/docs/framework-rule.md): コーディング原則と MVP 規約の正本 source
- [Old Customer Jobs Summary](../summaries/knowledge/old-customer-jobs-summary.md): 親子開発の好循環と親の役割境界の原型 summary
- [Old Customer Jobs Raw](../../raw/knowledge/docs/old-customer-jobs.md): 顧客ジョブ旧版の正本 source
- [Product Requirements AV Summary](../summaries/knowledge/product-requirements-av-summary.md): BGM / SFX / VFX と Code Maker audio 境界をまとめた summary
- [Product Requirements AV Raw](../../raw/knowledge/docs/product-requirements-av.md): AV 要求の正本 source
- [Product Requirements Battle Summary](../summaries/knowledge/product-requirements-battle-summary.md): 敵 / 呪文 / バランス調整 loop をまとめた summary
- [Product Requirements Battle Raw](../../raw/knowledge/docs/product-requirements-battle.md): Battle 要求の正本 source
- [Product Requirements Guardrails Summary](../summaries/knowledge/product-requirements-guardrails-summary.md): AI 改造 guardrail と resource 境界をまとめた summary
- [Product Requirements Guardrails Raw](../../raw/knowledge/docs/product-requirements-guardrails.md): Guardrails 要求の正本 source
- [Product Requirements Map Summary](../summaries/knowledge/product-requirements-map-summary.md): tilemap authorship と地形意味付けをまとめた summary
- [Product Requirements Map Raw](../../raw/knowledge/docs/product-requirements-map.md): Map 要求の正本 source
- [Product Requirements Narrative Summary](../summaries/knowledge/product-requirements-narrative-summary.md): dialogue / guidance / branching / ending をまとめた summary
- [Product Requirements Narrative Raw](../../raw/knowledge/docs/product-requirements-narrative.md): Narrative 要求の正本 source
- [Product Requirements Platform Summary](../summaries/knowledge/product-requirements-platform-summary.md): sharing / approval / Code Maker 境界をまとめた summary
- [Product Requirements Platform Raw](../../raw/knowledge/docs/product-requirements-platform.md): Platform 要求の正本 source
- [Repository Structure Summary](../summaries/knowledge/repository-structure-summary.md): repo の責務分担表と build runbook をまとめた summary
- [Repository Structure Raw](../../raw/knowledge/docs/repository-structure.md): リポジトリ構造定義の正本 source
- [Story Concepts Summary](../summaries/knowledge/story-concepts-summary.md): theme、zone arc、landmark symbolism をまとめた summary
- [Story Concepts Raw](../../raw/knowledge/docs/story-concepts.md): ストーリーコンセプトの正本 source
- [UX Policy Summary](../summaries/knowledge/ux-policy-summary.md): child-readable UX と parent assist 境界をまとめた summary
- [UX Policy Raw](../../raw/knowledge/docs/ux-policy.md): UX policy の正本 source
- [Architecture Checklist Summary](../summaries/checklists/architecture-checklist-summary.md): Code Maker と docs/pyxres の守り方
- [Framework Checklist Summary](../summaries/checklists/framework-checklist-summary.md): M1-M5 と done の扱い
- [UX Checklist Summary](../summaries/checklists/ux-checklist-summary.md): UX policy の checklist summary

## Areas

- [Persistent Wiki Vs RAG](../areas/persistent-wiki-vs-rag.md): Karpathy が plain RAG より persistent wiki を推す理由
- [Ingest Query Lint Loop](../areas/ingest-query-lint-loop.md): ingest / query / lint の役割分担と循環
- [Schema Driven Wiki Maintainer](../areas/schema-driven-wiki-maintainer.md): schema が disciplined maintainer を作る理由
- [Continuous Experience Loop](../areas/continuous-experience-loop.md): 子どもの `遊ぶ -> 作る -> 判断する -> 共有する` の連続体験
- [Parent Support Without Control](../areas/parent-support-without-control.md): 親が主体性を奪わずに支える条件
- [Low Friction Sharing](../areas/low-friction-sharing.md): 子どもの共有ジョブと友達の低摩擦体験をつなぐ観点
- [Fast Feedback Development Loop](../areas/fast-feedback-development-loop.md): 親子の `作る -> 遊ぶ -> 直す` を短時間で閉じる loop
- [Approval Loop And Child Agency](../areas/approval-loop-and-child-agency.md): 承認キューで子どもの主導権を守る考え方
- [Guardrails Protect The Loop](../areas/guardrails-protect-the-loop.md): ガードレールを好循環保護の前提として捉えるページ
- [Single Source Of Truth And Golden Path](../areas/single-source-of-truth-and-golden-path.md): SSoT と本番導線確認の規律
- [View Presenter Model Boundaries](../areas/view-presenter-model-boundaries.md): M1-M4 の境界規約をまとめたページ
- [No Silent Failure And Migration Safety](../areas/no-silent-failure-and-migration-safety.md): silent failure 禁止と移行安全性の原則
- [Audio Feedback And Polish](../areas/audio-feedback-and-polish.md): 音と演出を feedback loop の本体として扱うページ
- [Battle Balance And Spell Design](../areas/battle-balance-and-spell-design.md): 敵 / 呪文 / balance 変更の安全な単位をまとめたページ
- [Guardrail Layering And AI Change Boundaries](../areas/guardrail-layering-and-ai-change-boundaries.md): AI が触る層と守る層の分け方
- [Map Authorship And Tile Expression](../areas/map-authorship-and-tile-expression.md): 地形編集と runtime truth の一致を扱うページ
- [Narrative Branching And Player Guidance](../areas/narrative-branching-and-player-guidance.md): narrative の readability / guidance / branching を扱うページ
- [Platform Sharing And Approval Ops](../areas/platform-sharing-and-approval-ops.md): sharing、approval、rollback の運用ページ
- [Repository Operating Structure](../areas/repository-operating-structure.md): repo の責務分担と build runbook の意味を扱うページ
- [Story Theme And Landmark Symbolism](../areas/story-theme-and-landmark-symbolism.md): story spine と landmark 表現の接続を扱うページ
- [Child Readable UX And Parent Assist](../areas/child-readable-ux-and-parent-assist.md): child-readable UX と親の補助境界を扱うページ

## Queries

- [Why Persistent Wiki Beats RAG](../query/2026-05-23-why-persistent-wiki-beats-rag.md): persistent wiki が compounding artifact になる理由を整理した saved answer
- [What Protects Child Agency In Co-Development](../query/2026-05-24-what-protects-child-agency-in-co-development.md): 子どもの主体性を守るために必要な親の役割、approval loop、UX、fast feedback を整理した saved answer

## Candidates

- [Candidate Source: qmd And Obsidian Tooling](../candidates/2026-05-23-qmd-and-obsidian-tooling-candidate.md): optional search/tooling を深める次 source 候補

## Logs

- [Source Inbox](../logs/source-inbox.md): raw source を受け付けた履歴
- [Ingest Log](../logs/ingest-log.md): source を wiki へ反映した履歴
- [Health Check Log](../logs/health-check-log.md): core 5 点検の履歴
