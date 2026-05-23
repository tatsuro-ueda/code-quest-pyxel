# wiki index

repo-local wiki の入口。summary / checklist / tasknote をここから辿る。

## navigation

- [log.md](log.md)
- [indexes/tasknotes.md](indexes/tasknotes.md)
- [query/README.md](query/README.md)
- [candidates/concepts.md](candidates/concepts.md)
- [candidates/entities.md](candidates/entities.md)

## knowledge summaries

- [architecture_rules](summaries/knowledge/docs/architecture_rules-summary.md) — この source は yaml 形式で、top-level keys は meta、facts、validation_rules です。facts 配下では principles、tree、flows、entry_points を持ちます。
  - source: `raw/knowledge/docs/architecture_rules.yml`
- [顧客のジョブ](summaries/knowledge/docs/customer-jobs-summary.md) — この source は「顧客のジョブ」を扱う markdown で、主要トピックは 顧客セグメント、JPL 子ども（プレイヤー） [JOB:JPL_CHILD_PLAYER]、JCR 子ども（クリエイター） [JOB:JCR_CHILD_CREATOR]、JCT 子ども（批評家） [JOB:JCT_CHILD_CRITIC] です。👉 「遊びの没入が途切れる状態」から
  - source: `raw/knowledge/docs/customer-jobs.md`
- [カスタマージャーニー集](summaries/knowledge/docs/customer-journeys-summary.md) — この source は「カスタマージャーニー集」を扱う markdown で、主要トピックは ソリューションの構成、Buy（採用した外部依存）、Make（プロダクトが自前で備えるもの）、カスタマージャーニー一覧 です。Buy 4 つと Make 3 つ、合わせて 7 要素が揃って初めて好循環が回る。
  - source: `raw/knowledge/docs/customer-journeys.md`
- [コーディング原則](summaries/knowledge/docs/framework-rule-summary.md) — この source は「コーディング原則」を扱う markdown で、主要トピックは 1. 正本を一つにする（SSoT / Single Source of Truth）、2. 本番の通り道を必ず通す（Golden Path Test / End-to-End Smoke Test）、3. Migration Safety、4. No Silent Failure です。データや状態の「正しい置き場所」を一つに決め、他は必ずそこを経由して参照する。
  - source: `raw/knowledge/docs/framework-rule.md`
- [プロダクト要求: AV（BGM・SFX・VFX）](summaries/knowledge/docs/product-requirements-av-summary.md) — この source は「プロダクト要求: AV（BGM・SFX・VFX）」を扱う markdown で、主要トピックは CJG15: フィールドBGMをゾーンごとに付ける、CJG16: 戦闘BGMを付ける、CJG17: 効果音をイベントに紐づける、CJG24: 効果音を自分で作る です。この `CJG15` では、「場所が変わると音の雰囲気も変わり、その場所らしさがすぐ伝わる」を約束する。
  - source: `raw/knowledge/docs/product-requirements-av.md`
- [プロダクト要求: Battle（戦闘・敵・呪文・バランス）](summaries/knowledge/docs/product-requirements-battle-summary.md) — この source は「プロダクト要求: Battle（戦闘・敵・呪文・バランス）」を扱う markdown で、主要トピックは CJG08: 敵が強すぎる、CJG10: 新しい敵を追加したい、CJG13: 新しい呪文がほしい、CJG29: 全体のバランスを調整する です。この `CJG08` では、「強すぎる敵をすぐ調整できて、直したせいで別の仕組みが壊れない」を約束する。
  - source: `raw/knowledge/docs/product-requirements-battle.md`
- [プロダクト要求: Narrative（ダイアログ・ストーリー・ナビ）](summaries/knowledge/docs/product-requirements-narrative-summary.md) — この source は「プロダクト要求: Narrative（ダイアログ・ストーリー・ナビ）」を扱う markdown で、主要トピックは CJG09: セリフを変えたい、CJG14: マップが広すぎて迷う、CJG27: ストーリーの分岐を作る、CJG30: エンディングを自分たちで書く です。この `CJG09` では、「NPC のセリフを変えたら、その町らしさやキャラらしさがすぐゲームに出る」を約束する。
  - source: `raw/knowledge/docs/product-requirements-narrative.md`
- [プロダクト要求: Platform（配信・Code Maker制約・体験設計）](summaries/knowledge/docs/product-requirements-platform-summary.md) — この source は「プロダクト要求: Platform（配信・Code Maker制約・体験設計）」を扱う markdown で、主要トピックは CJG12: 歩いたら壁にハマった、CJG20: 演出を実際に当てて違いを体験する、CJG21: 友達に見せる、CJG22: 友達のフィードバックを反映する です。この `CJG12` では、「バグを見つけても親子の流れが止まらず、すぐ直して安全に試し直せる」を約束する。
  - source: `raw/knowledge/docs/product-requirements-platform.md`
- [リポジトリ構造定義書](summaries/knowledge/docs/repository-structure-summary.md) — この source は「リポジトリ構造定義書」を扱う markdown で、主要トピックは 1. 目的、2. 設計原則、3. 全体構造、3.5 build の起動方法（runbook） です。この文書は「どの file / 関数が何を担当するか」を固定する責務分担表である。`docs` と `code` がずれたら **未実装 / バグ / 仕様ずれ** として扱い、コードではなくこの文書を正本とする（AI が読める分担表の維持は [CJ37](customer-journeys.md) 「責務が曖昧で直すほど別の所が壊れる」のガードレール）。
  - source: `raw/knowledge/docs/repository-structure.md`
- [UX Policy](summaries/knowledge/docs/ux-policy-summary.md) — この source は「UX Policy」を扱う markdown で、主要トピックは 1. 子どもが読める表記を優先する、2. いま選んでいる操作だけを見せる、3. 押した実感を返す、4. 危険操作は無言で通さない です。子どもが「いま何が起きているか」を迷わず受け取れ、親が補助するときも主体性を奪わないための UI / 表記 / 操作方針。
  - source: `raw/knowledge/docs/ux-policy.md`

## tasknote summaries

- [2026年4月18日 アプリ：cj09-glitch-lord-conversation-mode](summaries/tasknotes/steering/20260418 アプリ：cj09-glitch-lord-conversation-mode-summary.md) — この source は「2026年4月18日 アプリ：cj09-glitch-lord-conversation-mode」を扱う markdown で、主要トピックは 1) 改善対象ジャーニー、人間の期待、現状、今回の方針 です。direction TB
  - source: `raw/tasknotes/steering/20260418 アプリ：cj09-glitch-lord-conversation-mode.md`
- [2026年5月9日 stakeholder_voices bootstrap](summaries/tasknotes/steering/done/20260509-stakeholder-voices-bootstrap-summary.md) — この source は「2026年5月9日 stakeholder_voices bootstrap」を扱う markdown で、主要トピックは 1) Journey（どこへ行くか）、2) Gherkin（完了条件）、シナリオ1：AI が根拠 YAML を更新しても参照切れを検知できる、シナリオ2：安全な YAML ドリフトは fix / repair で自動正規化できる です。I1[既存 docs]
  - source: `raw/tasknotes/steering/done/20260509-stakeholder-voices-bootstrap.md`
- [2026年5月17日 アプリ：battle-stale-spell-message](summaries/tasknotes/steering/done/20260517 アプリ：battle-stale-spell-message-summary.md) — この source は「2026年5月17日 アプリ：battle-stale-spell-message」を扱う markdown で、主要トピックは 1) Journey（どこへ行くか）、2) ユーザーストーリーマップ、話題1：再現条件を presenter 遷移へ閉じ込める、話題2：wiki/checklist の試運転に使う です。1. 前提条件
  - source: `raw/tasknotes/steering/done/20260517 アプリ：battle-stale-spell-message.md`
- [2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す](summaries/tasknotes/steering/done/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す-summary.md) — この source は「2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す」を扱う markdown で、主要トピックは 1) Journey（どこへ行くか）、2) ユーザーストーリーマップ、話題一覧、3) Gherkin（完了条件） です。1. 前提条件
  - source: `raw/tasknotes/steering/done/2026年5月22日 開発基盤：Karpathy方針でindexとlogの最小形を通す.md`
- [2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する](summaries/tasknotes/steering/done/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する-summary.md) — この source は「2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する」を扱う markdown で、主要トピックは 1) Journey（どこへ行くか）、2) ユーザーストーリーマップ、話題一覧、3) Gherkin（完了条件） です。1. 前提条件
  - source: `raw/tasknotes/steering/done/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する.md`

## checklist summaries

- [Architecture Checklist](summaries/checklists/architecture-checklist-summary.md) — この source は「Architecture Checklist」を扱う markdown で、主要トピックは Code Maker を子どもの正式編集面として守る、docs を要求として扱う、pyxres を正本として守る、dist を配布物として扱う です。`docs/architecture_rules.yml` を開発前に pass / fail で確認しやすい形へ落とした checklist。原典の `meta.status` が `draft` のため、この checklist も `draft` として扱う。
  - source: `raw/knowledge/checklists/architecture-checklist.md`
- [Framework Checklist](summaries/checklists/framework-checklist-summary.md) — この source は「Framework Checklist」を扱う markdown で、主要トピックは 正本と生成物、M1 View 境界、M2 ViewModel 境界、M3 Presenter 責務 です。`docs/framework-rule.md` の運用ルールを、開発前後に確認しやすい形へ圧縮した checklist。
  - source: `raw/knowledge/checklists/framework-checklist.md`
- [UX Checklist](summaries/checklists/ux-checklist-summary.md) — この source は「UX Checklist」を扱う markdown で、主要トピックは 子ども向け表記、画面の分かりやすさ、押した実感、危険操作 です。`docs/ux-policy.md` の初版を、変更前に確認しやすい yes / no 形式へ落とした checklist。
  - source: `raw/knowledge/checklists/ux-checklist.md`
