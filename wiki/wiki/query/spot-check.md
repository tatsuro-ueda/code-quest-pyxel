# query spot checks

repo-local rollout の `read-only query` を、実データに対して短く答える形で確認した記録。

## Q: code-quest-pyxel の architecture の核は何か

### A

核は 2 本あります。`architecture_rules.yml` は Code Maker / `.pyxres` / `dist` / docs 差分の扱いを定める architecture の正本候補で、`framework-rule.md` は M1-M5 の layer 境界と検証ルールを定める active な運用規約です。

### 根拠

- `wiki/wiki/summaries/knowledge/docs/architecture_rules-summary.md`
- `wiki/wiki/summaries/knowledge/docs/framework-rule-summary.md`
- `wiki/wiki/summaries/checklists/architecture-checklist-summary.md`
- `wiki/wiki/summaries/checklists/framework-checklist-summary.md`

### 情報不足

- `architecture_rules.yml` は `draft` で、完全移行前の候補段階

## Q: 子ども向けの UI 表記ルールは何か

### A

初版 `ux-policy.md` では、ひらがな中心、今の操作だけを見せる、押した実感を返す、危険操作を無言で通さない、の 4 つを中核にしています。`ux-checklist` はこの方針を実装前チェックへ落とした入口です。

### 根拠

- `wiki/wiki/summaries/knowledge/docs/ux-policy-summary.md`
- `wiki/wiki/summaries/checklists/ux-checklist-summary.md`

### 情報不足

- `ux-policy.md` は `draft` の初版

## Q: SSoT ポリシーとは何か

### A

正しい置き場所を 1 つに決め、他はそこを経由して参照する、という方針です。この repo では docs の要求、Code Maker / `.pyxres` の編集面、`dist` は配布物であって source ではない、という線引きまで含みます。

### 根拠

- `wiki/wiki/summaries/knowledge/docs/framework-rule-summary.md`
- `wiki/wiki/summaries/checklists/architecture-checklist-summary.md`

### 情報不足

- source ごとの細かな例外は raw docs 側に残る

## Q: battle 周りで今触っている task は何か

### A

現行の open task では `battle-stale-spell-message` があり、じゅもん未習得メッセージが次の item 選択へ重なる不具合を対象にしています。repo-local rollout では `battle current-state` はまだ作らず、open tasknote を入口にします。

### 根拠

- `wiki/wiki/indexes/tasknotes.md`
- `wiki/wiki/summaries/tasknotes/steering/done/20260517 アプリ：battle-stale-spell-message-summary.md`

### 情報不足

- `areas/current-state` は current rollout で未採用
