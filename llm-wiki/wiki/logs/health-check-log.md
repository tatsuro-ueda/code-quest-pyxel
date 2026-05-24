# Health Check Log

## [2026-05-23] lint | first-cycle wiki

- scope:
  - `llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md`
  - `llm-wiki/wiki/areas/persistent-wiki-vs-rag.md`
  - `llm-wiki/wiki/areas/ingest-query-lint-loop.md`
  - `llm-wiki/wiki/areas/schema-driven-wiki-maintainer.md`
  - `llm-wiki/wiki/query/2026-05-23-why-persistent-wiki-beats-rag.md`
  - `llm-wiki/wiki/indexes/master-index.md`
- contradictions: none
- stale_claims: none
- orphan_pages: none
- missing_concepts:
  - optional CLI tooling と Obsidian 補助機能は言及されているが、専用ページはまだ無い
- missing_crossrefs:
  - none
- fix_now:
  - none
- next_ingest:
  - optional tooling を wiki に常設するなら、qmd / Obsidian 補助機能を扱う source を 1 本追加したい
- candidate_source:
  - `llm-wiki/wiki/candidates/2026-05-23-qmd-and-obsidian-tooling-candidate.md`
- notes:
  - source 1 本と saved answer 1 本の small wiki でも core 5 点検は実施可能

## [2026-05-24] lint | post-ingest wiki

- scope:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/areas/*.md`
  - `llm-wiki/wiki/query/*.md`
  - `llm-wiki/wiki/summaries/knowledge/*.md`
  - `llm-wiki/wiki/summaries/checklists/*.md`
  - `llm-wiki/wiki/summaries/knowledge/docs/*.md`
  - `llm-wiki/wiki/summaries/tasknotes/steering/**/*.md`
- contradictions: none in the indexed wiki graph
- stale_claims:
  - `llm-wiki/wiki/summaries/knowledge/docs/*.md` の generated-style summary 群は、2026-05-23 に作成した curated summary 群（`llm-wiki/wiki/summaries/knowledge/*-summary.md`）へ実質的に置き換わっているが、active のまま live wiki 内に残っている
  - `llm-wiki/wiki/summaries/knowledge/docs/architecture_rules-summary.md` は `status: draft` かつ `replacement_of: docs/repository-structure.md` を持つが、現在の canonical operating map は `Repository Structure Summary` 側にあり、replacement claim は未統合のまま stale
- orphan_pages:
  - `llm-wiki/wiki/summaries/knowledge/docs/*.md`（10 pages）
  - `llm-wiki/wiki/summaries/tasknotes/steering/**/*.md`（5 pages）
- missing_concepts:
  - `Code Maker が子どもの正式な編集面であり、editor で見えたものが runtime の真実である` という概念は map / platform / guardrails / AV に分散しているが、専用 concept page がまだ無い
  - `Code Maker zip の持ち出し・取り込み・resource carry-back` の運用境界は platform / guardrails に分散しているが、専用 concept page がまだ無い
- missing_crossrefs:
  - `Approval Loop And Child Agency` と `Child Readable UX And Parent Assist`
  - `Parent Support Without Control` と `Platform Sharing And Approval Ops`
  - `Guardrail Layering And AI Change Boundaries` と `View Presenter Model Boundaries`
  - `Guardrails Protect The Loop` と `Repository Operating Structure`
- fix_now:
  - orphan な duplicate summary subtree を `archive` 扱いへ移すか、live wiki で使うなら専用 index を与える
  - 上記 4 組の missing crossrefs を追加して、approval / UX / guardrail / repo-structure の導線を強める
- next_ingest:
  - 外部 source を増やすより先に、既存 source から `Code Maker editing truth` と `resource carry-back pipeline` の 2 概念を synthesized page として切り出したい
- candidate_source:
  - none
- notes:
  - 現在の主要 graph（master index から辿れる summary / area / query）は整合している
  - 問題の中心は `core pages の矛盾` ではなく、live wiki 内に残った orphan duplicate と、横断導線の薄さにある

## [2026-05-24] fix | post-ingest wiki cleanup

- action:
  - `llm-wiki/wiki/summaries/knowledge/docs/*.md` の旧 generated-style summary 10 pages を `llm-wiki/archive/summaries/knowledge/docs/` へ移動
  - missing crossrefs 4 組を area pages 同士で相互追加
- resolved:
  - live wiki 内の duplicate generated summary orphan は解消
  - `Approval Loop And Child Agency` ↔ `Child Readable UX And Parent Assist`
  - `Parent Support Without Control` ↔ `Platform Sharing And Approval Ops`
  - `Guardrail Layering And AI Change Boundaries` ↔ `View Presenter Model Boundaries`
  - `Guardrails Protect The Loop` ↔ `Repository Operating Structure`
- remaining_orphans:
  - `llm-wiki/wiki/summaries/tasknotes/steering/**/*.md`（tasknote summary subtree のみ）
- notes:
  - live wiki の主要 graph は、curated summary / area / query へほぼ一本化できた

## [2026-05-24] lint | post-health-check-skill contract

- scope:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/areas/*.md`
  - `llm-wiki/wiki/query/*.md`
  - `llm-wiki/wiki/summaries/knowledge/*.md`
  - `llm-wiki/wiki/summaries/checklists/*.md`
  - `llm-wiki/wiki/summaries/tasknotes/**/*.md`
  - `llm-wiki/wiki/logs/health-check-log.md`
- contradictions: none in the indexed wiki graph
- stale_claims:
  - `llm-wiki/wiki/indexes/master-index.md` の `Health Check Log` 説明が `core 5 点検の履歴` のままで、current schema の `core 6 + data_gaps` 契約へ追随していない
  - `llm-wiki/wiki/areas/ingest-query-lint-loop.md` の `lint` 節が `contradictions / stale claims / orphan pages / missing concepts / missing crossrefs` の 5 項目止まりで、`data_gaps` をまだ含んでいない
- orphan_pages:
  - `llm-wiki/wiki/summaries/tasknotes/steering/20260418 アプリ：cj09-glitch-lord-conversation-mode-summary.md`
  - `llm-wiki/wiki/summaries/tasknotes/steering/done/20260509-stakeholder-voices-bootstrap-summary.md`
  - `llm-wiki/wiki/summaries/tasknotes/steering/done/20260517 アプリ：battle-stale-spell-message-summary.md`
  - `llm-wiki/wiki/summaries/tasknotes/steering/done/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す-summary.md`
  - `llm-wiki/wiki/summaries/tasknotes/steering/done/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する-summary.md`
- missing_concepts:
  - `health-check-wiki` を read-only lint route、`update-schema` を stable rule promotion route として分ける current contract は schema / skill / tasknote にあるが、llm-wiki compiled page 側にはまだまとまっていない
  - `Code Maker が子どもの正式な編集面であり、editor で見えたものが runtime の真実である` という概念は依然として map / platform / guardrails / AV に分散している
  - `Code Maker zip の持ち出し・取り込み・resource carry-back` の運用境界は依然として platform / guardrails に分散している
- missing_crossrefs:
  - none
- data_gaps:
  - current wiki だけでは `health-check-wiki` と `update-schema` の役割分離、および `data_gaps` を含む 6 分類 lint の現行運用を十分に説明できない
- fix_now:
  - 上記 5 本の orphan tasknote summary を `master-index` へ載せるか、`archive` へ退避するかを決める
  - `master-index` の `Health Check Log` 説明を `core 6 + data_gaps` に更新する
  - `Ingest Query Lint Loop` の `lint` 節へ `data_gaps` を追加する
- next_ingest:
  - `health-check-wiki` と `update-schema` の分離、および `core 6 + data_gaps` lint contract を 1 本の compiled page として切り出したい
  - 既存 source から `Code Maker editing truth` と `resource carry-back pipeline` の 2 概念を synthesized page として切り出したい
- candidate_source:
  - none
- notes:
  - indexed graph 自体の矛盾や crossref 破綻は見当たらない
  - 今回の中心は、active page の lint 契約が `core 5` 表記のまま残っている点と、unindexed tasknote summary 5 本が live wiki 側に残っている点である

## [2026-05-24] lint | current wiki

- scope:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/areas/*.md`
  - `llm-wiki/wiki/query/*.md`
  - `llm-wiki/wiki/summaries/knowledge/*.md`
  - `llm-wiki/wiki/summaries/checklists/*.md`
  - `llm-wiki/wiki/summaries/tasknotes/**/*.md`
  - `llm-wiki/wiki/logs/health-check-log.md`
- contradictions: none in the indexed wiki graph
- stale_claims:
  - `llm-wiki/wiki/indexes/master-index.md` の `Health Check Log` 説明がまだ `core 5 点検の履歴` のままで、current schema の `core 6 + data_gaps` 契約へ追随していない
  - `llm-wiki/wiki/areas/ingest-query-lint-loop.md` の `lint` 節が `contradictions / stale claims / orphan pages / missing concepts / missing crossrefs` の 5 項目止まりで、`data_gaps` をまだ含んでいない
- orphan_pages: none
- missing_concepts:
  - `health-check` を read-only lint route、`update-schema` を stable rule promotion route として分ける current contract は、schema と skill と log にはあるが、compiled wiki の area page としてはまだまとまっていない
- missing_crossrefs:
  - none
- data_gaps:
  - none
- fix_now:
  - `master-index` の `Health Check Log` 説明を `core 6 + data_gaps` に更新する
  - `Ingest Query Lint Loop` の `lint` 節へ `data_gaps` を追加する
- next_ingest:
  - `health-check` と `update-schema` の役割分離、および `core 6 + data_gaps` lint contract を 1 本の compiled page として切り出したい
- candidate_source:
  - none
- notes:
  - Python helper の `orphan_signals` と `missing_target_signals` は空で、前回問題だった unindexed tasknote summary は `master-index` への接続で解消している
  - helper の `crossref_signals` は hub-and-spoke な summary / log page にも広く反応するため、今回の health-check では issue 化せず human judgment で除外した

## [2026-05-24] lint | current wiki after wording alignment

- scope:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/areas/*.md`
  - `llm-wiki/wiki/query/*.md`
  - `llm-wiki/wiki/summaries/knowledge/*.md`
  - `llm-wiki/wiki/summaries/checklists/*.md`
  - `llm-wiki/wiki/summaries/tasknotes/**/*.md`
  - `llm-wiki/wiki/logs/health-check-log.md`
- contradictions: none in the indexed wiki graph
- stale_claims: none
- orphan_pages: none
- missing_concepts: none
- missing_crossrefs: none
- data_gaps: none
- fix_now:
  - none
- next_ingest:
  - none
- candidate_source:
  - none
- notes:
  - `master-index` の `Health Check Log` 説明と `Ingest Query Lint Loop` の `lint` 節は、current schema の `core 6 + data_gaps` 契約へ追随した
  - `health-check` と `update-schema` の役割分離は、現時点では compiled page でなく schema に置く判断とした
  - Python helper の `orphan_signals` と `missing_target_signals` は空で、helper の `crossref_signals` は今回も human judgment で issue 化しなかった

## [2026-05-24] lint | current wiki

- scope:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/areas/*.md`
  - `llm-wiki/wiki/query/*.md`
  - `llm-wiki/wiki/summaries/knowledge/*.md`
  - `llm-wiki/wiki/summaries/checklists/*.md`
  - `llm-wiki/wiki/summaries/tasknotes/**/*.md`
  - `llm-wiki/wiki/candidates/*.md`
  - `llm-wiki/wiki/logs/*.md`
- contradictions: none
- stale_claims:
  - `llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md` の `lint: core 5 と data gap` という表現は、current repo の運用表記 `core 6 + data_gaps` とずれて見える。source summary と repo-local contract の境界を明示していないため、active wiki 上では wording drift として読まれうる
  - `llm-wiki/wiki/summaries/tasknotes/steering/done/20260507-src-header-functions-for-all-files-summary.md` の H1 が `battle/view.py` 個別 note と同じ題名のままで、body が説明している umbrella note の内容と一致していない
- orphan_pages: none
- missing_concepts: none
- missing_crossrefs: none
- data_gaps: none
- fix_now:
  - `2026-04-04-karpathy-llm-wiki-summary.md` の lint 表記を current repo の契約へそろえるか、`source 側では 5 + data gap / repo 運用では 6 categories` のように境界を明示する
  - `20260507-src-header-functions-for-all-files-summary.md` の H1 を umbrella note の実内容に合わせて改題し、`battle-view` summary との重複題名を解消する
- next_ingest:
  - none
- candidate_source:
  - none
- notes:
  - Python helper の `orphan_signals` と `missing_target_signals` は今回も 0 件だった
  - helper の `crossref_signals` は 99 件出たが、大半は summary / log / candidate の薄い接続を拾う広めの signal で、今回の issue には採用しなかった
  - 現在の中心は graph の欠損ではなく、active page の wording / title metadata drift である

## [2026-05-24] fix | current wiki drift repair

- action:
  - `llm-wiki/wiki/summaries/knowledge/2026-04-04-karpathy-llm-wiki-summary.md` の `lint` 行を current repo の `core 6 + data_gaps` 契約に合う表現へ更新
  - `llm-wiki/wiki/summaries/tasknotes/steering/done/20260507-src-header-functions-for-all-files-summary.md` の H1 を umbrella note の実内容に合う題名へ改題
- resolved:
  - `Karpathy LLM Wiki Summary` の wording drift
  - `Src header functions for all files` summary の title drift
- verification:
  - `python tools/llm_wiki_health_check_helper.py --repo-root .` を再実行し、`orphan_signal_count 0` と `missing_target_signal_count 0` を確認
  - 旧 wording と旧 H1 は `rg` 再確認で一致 0 件
- notes:
  - 今回は compiled wiki の active page 2 件だけを直し、過去の lint entry は履歴として保持した

## [2026-05-24] lint | current wiki

- scope:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/areas/*.md`
  - `llm-wiki/wiki/query/*.md`
  - `llm-wiki/wiki/summaries/knowledge/*.md`
  - `llm-wiki/wiki/logs/health-check-log.md`
- contradictions: none
- stale_claims: none
- orphan_pages:
  - `llm-wiki/wiki/query/2026年5月24日 最新のPRレビューチェックリスト（技術項目50件）.md` は saved query page として存在するが、`master-index` の active graph から到達できない
- missing_concepts: none
- missing_crossrefs: none
- data_gaps: none
- fix_now:
  - 上記 query page を `master-index.md` に載せるか、saved answer として保持しないなら `archive` / 削除のどちらかに整理する
- next_ingest:
  - none
- candidate_source:
  - none
- notes:
  - Python helper の `orphan_signals` は 1 件、`missing_target_signals` は 0 件で、今回の concrete drift は未索引 query 1 件だけだった
  - helper の `crossref_signals` は広めの connectivity signal なので、今回も human judgment で issue 化しなかった
  - indexed graph 本体の矛盾、stale wording、concept 欠落は spot-check 範囲では見当たらなかった

## [2026-05-24] lint | current wiki

- scope:
  - `llm-wiki/wiki/indexes/master-index.md`
  - `llm-wiki/wiki/areas/*.md`
  - `llm-wiki/wiki/query/*.md`
  - `llm-wiki/wiki/summaries/knowledge/*.md`
  - `llm-wiki/wiki/logs/health-check-log.md`
- contradictions: none
- stale_claims: none
- orphan_pages: none
- missing_concepts: none
- missing_crossrefs: none
- data_gaps: none
- fix_now:
  - none
- next_ingest:
  - none
- candidate_source:
  - none
- notes:
  - Python helper の `orphan_signals` は 0 件、`missing_target_signals` は 0 件だった
  - 前回 issue 化した `最新のPRレビューチェックリスト（技術項目50件）` query page は今回の点検時点で `llm-wiki/wiki/query/` 配下に存在せず、未索引 page としては残っていなかった
  - helper の `crossref_signals` は 151 件出たが、summary / log / candidate の薄い接続にも広く反応するため、今回も human judgment で issue 化しなかった
