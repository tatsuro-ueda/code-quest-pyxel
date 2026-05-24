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
- [Tasknote Summary: G12 code-maker.zip rebuild](../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md): Code Maker zip を Web 版の `main.py` と `pyxres` にそろえ、artifact diff と headless 起動まで確認した summary
- [Tasknote Raw: G12 code-maker.zip rebuild](../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md): Code Maker packaging の実施記録
- [Tasknote Summary: G15 test pinning](../summaries/tasknotes/done/20260412-g15-test-pinning-summary.md): 壊れた pytest lane を復旧し、130 テスト全通過で failure signal を戻した summary
- [Tasknote Raw: G15 test pinning](../../raw/tasknotes/done/20260412-g15-test-pinning.md): テスト復旧と挙動固定の実施記録
- [Tasknote Summary: Guardrails 1 SSoT + Codegen](../summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md): YAML 正本、codegen、loader 境界で data 不整合を減らした summary
- [Tasknote Raw: Guardrails 1 SSoT + Codegen](../../raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md): SSoT と codegen 基盤導入の実施記録
- [Tasknote Summary: Guardrails 2 Hooks](../summaries/tasknotes/steering/done/20260412-guardrails-2-hooks-summary.md): generated / `.pyxres` / wrong import path を hook で block し、正しい編集経路へ戻す summary
- [Tasknote Raw: Guardrails 2 Hooks](../../raw/tasknotes/steering/done/20260412-guardrails-2-hooks.md): hook guardrail 設計・実装の元 tasknote
- [Tasknote Summary: Guardrails 3 Headless Test](../summaries/tasknotes/steering/done/20260412-guardrails-3-headless-test-summary.md): `tools/test_headless.py` による headless 起動 gate の設計をまとめた summary
- [Tasknote Raw: Guardrails 3 Headless Test](../../raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md): headless test 基盤の元 tasknote
- [Tasknote Summary: Guardrails 4 pyxres Validation](../summaries/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation-summary.md): `.pyxres` guardrail の旧前提と current truth への読み替えをまとめた summary
- [Tasknote Raw: Guardrails 4 pyxres Validation](../../raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md): pyxres 整合チェックの元 tasknote
- [Tasknote Summary: Guardrails 5 Save Compat](../summaries/tasknotes/steering/done/20260412-guardrails-5-save-compat-summary.md): 固定 save fixture と load test で既存データ破壊を防ぐ build gate をまとめた summary
- [Tasknote Raw: Guardrails 5 Save Compat](../../raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md): save compatibility guardrail の元 tasknote
- [Tasknote Summary: J31 fix selector links](../summaries/tasknotes/steering/done/20260412-j31-fix-selector-links-summary.md): selector page の `play.html` 404 を wrapper 再生成で復旧した summary
- [Tasknote Raw: J31 fix selector links](../../raw/tasknotes/steering/done/20260412-j31-fix-selector-links.md): selector link restore の元 tasknote
- [Tasknote Summary: J36 dialogue SSoT](../summaries/tasknotes/steering/done/20260412-j36-dialogue-ssot-summary.md): dialogue を YAML 正本 + generated + sync へ寄せた SSoT migration の summary
- [Tasknote Raw: J36 dialogue SSoT](../../raw/tasknotes/steering/done/20260412-j36-dialogue-ssot.md): dialogue SSoT migration の元 tasknote
- [Tasknote Summary: Guardrails 6 Web Delivery Test](../summaries/tasknotes/steering/done/20260412-guardrails-6-web-delivery-test-summary.md): Playwright による browser 実行 gate で Web 版破壊を approval queue 手前で止める summary
- [Tasknote Raw: Guardrails 6 Web Delivery Test](../../raw/tasknotes/steering/done/20260412-guardrails-6-web-delivery-test.md): web delivery guardrail の元 tasknote
- [Tasknote Summary: J38 preview build flow](../summaries/tasknotes/steering/done/20260412-j38-preview-build-flow-summary.md): preview/current build を分離し、未承認変更が current に混ざらないようにした summary
- [Tasknote Raw: J38 preview build flow](../../raw/tasknotes/steering/done/20260412-j38-preview-build-flow.md): preview/current build 分離の元 tasknote
- [Tasknote Summary: J21 access log visibility](../summaries/tasknotes/steering/done/20260413-j21-access-log-visibility-summary.md): shared play の長短を same-origin logging で後から読めるようにした summary
- [Tasknote Raw: J21 access log visibility](../../raw/tasknotes/steering/done/20260413-j21-access-log-visibility.md): play session logging 導入の元 tasknote
- [Tasknote Summary: J37 dialogue page advance](../summaries/tasknotes/steering/done/20260413-j37-dialogue-page-advance-summary.md): 複数フレーズ会話で current page だけを描くように責務をそろえた summary
- [Tasknote Raw: J37 dialogue page advance](../../raw/tasknotes/steering/done/20260413-j37-dialogue-page-advance.md): dialogue paging 修正の元 tasknote
- [Tasknote Summary: J38 dungeon boss trigger](../summaries/tasknotes/steering/done/20260413-j38-dungeon-boss-trigger-summary.md): ダンジョン最奥に explicit boss trigger と目印を置いて終点導線を復旧した summary
- [Tasknote Raw: J38 dungeon boss trigger](../../raw/tasknotes/steering/done/20260413-j38-dungeon-boss-trigger.md): ダンジョン終点ボス導線復旧の元 tasknote
- [Tasknote Summary: J42 RPG loop journey](../summaries/tasknotes/steering/done/20260413-j42-rpg-loop-journey-summary.md): バグ修正を完走体験の保護へ結び直し、CJ42 と guardrail 対象 journey を広げた summary
- [Tasknote Raw: J42 RPG loop journey](../../raw/tasknotes/steering/done/20260413-j42-rpg-loop-journey.md): RPG 完走体験と guardrail 接続の元 tasknote
- [Tasknote Summary: J39 run fail enemy turn](../summaries/tasknotes/steering/done/20260413-j39-run-fail-enemy-turn-summary.md): 逃走失敗後の敵ターン欠落を phase 責務の修正で戦闘ループへ戻した summary
- [Tasknote Raw: J39 run fail enemy turn](../../raw/tasknotes/steering/done/20260413-j39-run-fail-enemy-turn.md): 逃走失敗後の敵ターン修正の元 tasknote
- [Tasknote Summary: J33 selector change list SSoT](../summaries/tasknotes/steering/done/20260414-j33-selector-change-list-ssot-summary.md): selector の変更説明を SoT failure と捉え、stale metadata を guardrail で止める summary
- [Tasknote Raw: J33 selector change list SSoT](../../raw/tasknotes/steering/done/20260414-j33-selector-change-list-ssot.md): selector change list SSoT 修正の元 tasknote
- [Tasknote Summary: J43 public access log runtime](../summaries/tasknotes/steering/done/20260414-j43-public-access-log-runtime-summary.md): 実公開 URL の play log 欠落を runtime server 差し替えで復旧した summary
- [Tasknote Raw: J43 public access log runtime](../../raw/tasknotes/steering/done/20260414-j43-public-access-log-runtime.md): 実公開アクセスログ復旧の元 tasknote
- [Tasknote Summary: J44 stale preview selector runtime](../summaries/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime-summary.md): preview source 不在時は stale preview を見せない運用へ切り替えた summary
- [Tasknote Raw: J44 stale preview selector runtime](../../raw/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime.md): stale preview 遮断の元 tasknote
- [Tasknote Summary: J45 noise guardian event only preview](../summaries/tasknotes/steering/done/20260414-j45-noise-guardian-event-only-preview-summary.md): イベント専用敵ノイズガーディアンを通常遭遇から外し preview で検証した summary
- [Tasknote Raw: J45 noise guardian event only preview](../../raw/tasknotes/steering/done/20260414-j45-noise-guardian-event-only-preview.md): ノイズガーディアン event-only 修正の元 tasknote
- [Tasknote Summary: J46 web cache bust preview current](../summaries/tasknotes/steering/done/20260414-j46-web-cache-bust-preview-current-summary.md): build token 付き URL で preview/current の cache bust を導入した summary
- [Tasknote Raw: J46 web cache bust preview current](../../raw/tasknotes/steering/done/20260414-j46-web-cache-bust-preview-current.md): preview/current cache bust の元 tasknote
- [Tasknote Summary: J47 preview first selector autogen](../summaries/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen-summary.md): preview-first 運用に合わせて selector 説明を diff 自動生成へ寄せた summary
- [Tasknote Raw: J47 preview first selector autogen](../../raw/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen.md): preview-first selector 自動説明の元 tasknote
- [Tasknote Summary: J48 preview must reflect current request](../summaries/tasknotes/steering/done/20260416-j48-preview-must-reflect-current-request-summary.md): おためしばんは今の依頼を表す版だと CJ31/CJG31 に固定した summary
- [Tasknote Raw: J48 preview must reflect current request](../../raw/tasknotes/steering/done/20260416-j48-preview-must-reflect-current-request.md): preview meaning 明文化の元 tasknote
- [Tasknote Summary: J49 bind preview to open request note](../summaries/tasknotes/steering/done/20260416-j49-bind-preview-to-open-request-note-summary.md): 次の依頼で前 preview を current に回す promotion rule を探った summary
- [Tasknote Raw: J49 bind preview to open request note](../../raw/tasknotes/steering/done/20260416-j49-bind-preview-to-open-request-note.md): preview/current promotion rule の元 tasknote

- [Tasknote Summary: CJ26 codemaker resource import](../summaries/tasknotes/steering/done/20260420-cj26-codemaker-resource-import-summary.md): Code Maker zip から code を拾わず resource だけを戻す import 経路と approve/reject 閉路を固めた summary
- [Tasknote Raw: CJ26 codemaker resource import](../../raw/tasknotes/steering/done/20260420-cj26-codemaker-resource-import.md): CJ26 codemaker resource import の元 tasknote
- [Tasknote Summary: CJ26 static codemaker upload](../summaries/tasknotes/steering/done/20260420-cj26-static-codemaker-upload-summary.md): static 配信でも Code Maker zip を browser 保存経由で戻せる honest upload UX を整えた summary
- [Tasknote Raw: CJ26 static codemaker upload](../../raw/tasknotes/steering/done/20260420-cj26-static-codemaker-upload.md): CJ26 static codemaker upload の元 tasknote
- [Tasknote Summary: CJ26 codemaker resource truth runtime](../summaries/tasknotes/steering/done/20260420-cj26-codemaker-resource-truth-runtime-summary.md): Code Maker で直した image bank を runtime self-heal で巻き戻させない責務整理の summary
- [Tasknote Raw: CJ26 codemaker resource truth runtime](../../raw/tasknotes/steering/done/20260420-cj26-codemaker-resource-truth-runtime.md): CJ26 codemaker resource truth runtime の元 tasknote
- [Tasknote Summary: CJ26 codemaker audio code import](../summaries/tasknotes/steering/done/20260420-cj26-codemaker-audio-code-import-summary.md): Sound/Music の authoring と runtime playback を分ける audio import 設計を固めた summary
- [Tasknote Raw: CJ26 codemaker audio code import](../../raw/tasknotes/steering/done/20260420-cj26-codemaker-audio-code-import.md): CJ26 codemaker audio code import の元 tasknote
- [Tasknote Summary: CJ24 codemaker sfx roundtrip](../summaries/tasknotes/steering/done/20260420-cj24-codemaker-sfx-roundtrip-summary.md): Sound エディタの SFX を imported slot truth として本編へ残す round-trip 修正の summary
- [Tasknote Raw: CJ24 codemaker sfx roundtrip](../../raw/tasknotes/steering/done/20260420-cj24-codemaker-sfx-roundtrip.md): CJ24 codemaker sfx roundtrip の元 tasknote
- [Tasknote Summary: Src method level comments](../summaries/tasknotes/steering/done/20260421-src-method-level-comments-summary.md): 責務コメントを `src/generated` を触らずに src へ展開し可読性を上げた summary
- [Tasknote Raw: Src method level comments](../../raw/tasknotes/steering/done/20260421-src-method-level-comments.md): Src method level comments の元 tasknote
- [Tasknote Summary: CJ26 distribute loaded resource](../summaries/tasknotes/steering/done/20260422-cj26-distribute-loaded-resource-summary.md): 読み込んだ resource と配布 artifact の resource source を server-first で一致させる運用の summary
- [Tasknote Raw: CJ26 distribute loaded resource](../../raw/tasknotes/steering/done/20260422-cj26-distribute-loaded-resource.md): CJ26 distribute loaded resource の元 tasknote
- [Tasknote Summary: J52 main runtime full extraction](../summaries/tasknotes/steering/done/20260422-j52-main-runtime-full-extraction-summary.md): root `main.py` を thin wrapper 化し runtime 正本を `src/runtime` へ移した summary
- [Tasknote Raw: J52 main runtime full extraction](../../raw/tasknotes/steering/done/20260422-j52-main-runtime-full-extraction.md): J52 main runtime full extraction の元 tasknote
- [Tasknote Summary: J53 runtime modularize and single distribution](../summaries/tasknotes/steering/done/20260422-j53-runtime-modularize-and-single-distribution-summary.md): runtime monolith 分解、Code Maker bundler、単一本番配布までを段階的に完了した summary
- [Tasknote Raw: J53 runtime modularize and single distribution](../../raw/tasknotes/steering/done/20260422-j53-runtime-modularize-and-single-distribution.md): J53 runtime modularize and single distribution の元 tasknote
- [Tasknote Summary: Town framework rule align](../summaries/tasknotes/steering/done/20260424-town-framework-rule-align-summary.md): town/shop bugfix を PlayerModel 導入と scene 分解まで広げて framework-rule に合わせた summary
- [Tasknote Raw: Town framework rule align](../../raw/tasknotes/steering/done/20260424-town-framework-rule-align.md): Town framework rule align の元 tasknote

- [Tasknote Summary: Guardrails prd framework rule sync](../summaries/tasknotes/steering/done/20260424-guardrails-prd-framework-rule-sync-summary.md): guardrails PRD を M1〜M5 と現行 repo layout に同期し CJG37/44 と G16〜G20 を整理した summary
- [Tasknote Raw: Guardrails prd framework rule sync](../../raw/tasknotes/steering/done/20260424-guardrails-prd-framework-rule-sync.md): Guardrails prd framework rule sync の元 tasknote
- [Tasknote Summary: Play session ip ua browser](../summaries/tasknotes/steering/done/20260422-play-session-ip-ua-browser-summary.md): play session DB に IP/UA と browser 分類を追加し observability を report へ返した summary
- [Tasknote Raw: Play session ip ua browser](../../raw/tasknotes/steering/done/20260422-play-session-ip-ua-browser.md): Play session ip ua browser の元 tasknote
- [Tasknote Summary: Player dict residue crash fix](../summaries/tasknotes/steering/done/20260425-player-dict-residue-crash-fix-summary.md): PlayerModel 移行後に残った `game.player` 参照漏れ crash を潰し grep ルールを足した summary
- [Tasknote Raw: Player dict residue crash fix](../../raw/tasknotes/steering/done/20260425-player-dict-residue-crash-fix.md): Player dict residue crash fix の元 tasknote
- [Tasknote Summary: Shop keyerror shop list unpack](../summaries/tasknotes/steering/done/20260425-shop-keyerror-shop-list-unpack-summary.md): shop KeyError と item-use shim ずれを SSoT 経路へ戻し smoke test 課題を明文化した summary
- [Tasknote Raw: Shop keyerror shop list unpack](../../raw/tasknotes/steering/done/20260425-shop-keyerror-shop-list-unpack.md): Shop keyerror shop list unpack の元 tasknote
- [Tasknote Summary: Tests that prevent runtime crashes](../summaries/tasknotes/steering/done/20260425-tests-that-prevent-runtime-crashes-summary.md): runtime crash-prevention test の新設前に既存 `test_cjg_*` 群の十分性を監査して撤収した summary
- [Tasknote Raw: Tests that prevent runtime crashes](../../raw/tasknotes/steering/done/20260425-tests-that-prevent-runtime-crashes.md): Tests that prevent runtime crashes の元 tasknote
- [Tasknote Summary: Autonomous rule compliance loop](../summaries/tasknotes/steering/done/20260425-autonomous-rule-compliance-loop-summary.md): M1〜M5 compliance loop を回し AGENTS 整備まで閉じて judgment item 6 件を抽出した summary
- [Tasknote Raw: Autonomous rule compliance loop](../../raw/tasknotes/steering/done/20260425-autonomous-rule-compliance-loop.md): Autonomous rule compliance loop の元 tasknote
- [Tasknote Summary: Menu shim crash fix](../summaries/tasknotes/steering/done/20260425-menu-shim-crash-fix-summary.md): nonexistent Game shim を呼ぶ menu crash を scene API 直呼びと regression test で潰した summary
- [Tasknote Raw: Menu shim crash fix](../../raw/tasknotes/steering/done/20260425-menu-shim-crash-fix.md): Menu shim crash fix の元 tasknote
- [Tasknote Summary: Brushup customer journeys](../summaries/tasknotes/steering/done/20260425-brushup-customer-journeys-summary.md): 42 journey に competitor-before とカテゴリタグを追加し競合分析を要求化しやすくした summary
- [Tasknote Raw: Brushup customer journeys](../../raw/tasknotes/steering/done/20260425-brushup-customer-journeys.md): Brushup customer journeys の元 tasknote
- [Tasknote Summary: Pyxres as world map SSOT](../summaries/tasknotes/steering/done/20260425-pyxres-as-world-map-ssot-summary.md): pyxres world map を起動時 procedural bake で上書きしない guard を入れ probe で確認した summary
- [Tasknote Raw: Pyxres as world map SSOT](../../raw/tasknotes/steering/done/20260425-pyxres-as-world-map-ssot.md): Pyxres as world map SSOT の元 tasknote

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
- [Health Check Log](../logs/health-check-log.md): core 6 + data_gaps を含む health-check の履歴
