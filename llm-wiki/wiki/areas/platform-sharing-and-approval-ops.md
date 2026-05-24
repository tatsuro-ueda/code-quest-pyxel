---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/product-requirements-platform-summary.md
  - ../summaries/knowledge/ux-policy-summary.md
  - ../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-5-save-compat-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j31-fix-selector-links-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-6-web-delivery-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j38-preview-build-flow-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j21-access-log-visibility-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j33-selector-change-list-ssot-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j43-public-access-log-runtime-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j46-web-cache-bust-preview-current-summary.md
  - ../summaries/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen-summary.md
  - ../summaries/tasknotes/steering/done/20260416-j48-preview-must-reflect-current-request-summary.md
  - ../summaries/tasknotes/steering/done/20260416-j49-bind-preview-to-open-request-note-summary.md
  - ../../raw/knowledge/docs/product-requirements-platform.md
  - ../../raw/knowledge/docs/ux-policy.md
  - ../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md
  - ../../raw/tasknotes/steering/done/20260412-j31-fix-selector-links.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-6-web-delivery-test.md
  - ../../raw/tasknotes/steering/done/20260412-j38-preview-build-flow.md
  - ../../raw/tasknotes/steering/done/20260413-j21-access-log-visibility.md
  - ../../raw/tasknotes/steering/done/20260414-j33-selector-change-list-ssot.md
  - ../../raw/tasknotes/steering/done/20260414-j43-public-access-log-runtime.md
  - ../../raw/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime.md
  - ../../raw/tasknotes/steering/done/20260414-j46-web-cache-bust-preview-current.md
  - ../../raw/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen.md
  - ../../raw/tasknotes/steering/done/20260416-j48-preview-must-reflect-current-request.md
  - ../../raw/tasknotes/steering/done/20260416-j49-bind-preview-to-open-request-note.md
---

# Platform Sharing And Approval Ops

## 核心

`product-requirements-platform` は、共有、再修正、承認、巻き戻しを 1 つの運用系としてまとめる。友達に URL を送るだけで遊べ、感想を受けて数分で直し、子どもが development と production を比べて採否を決めるところまでが platform の仕事になる。

## 共有と承認の loop

- URL だけで即プレイできる低摩擦共有
- フィードバックをその場で修正して再共有できる loop
- play log で「届いたか」を次の行動へつなげる
- preview/current を分けた compare flow で、未承認変更が current に混ざらない状態を保つ
- shared wrapper に残る play session の長短を、次の声かけや修正判断へつなげる
- 開発版 / 本番版の比較で承認、却下、再提案、巻き戻しを回す
- approval queue に出す前に save compatibility を通し、既存セーブを壊す版を共有前に止める
- selector の change list は実差分から再生成し、古い metadata を approval 材料に残さない
- preview source が無いときは preview card を出さず、stale artifact を shared 導線に乗せない
- current / preview は build token 付き URL で配り、比較のたびに古い HTML を握らせない
- 実公開 URL は play-session POST を受ける runtime server で配り、shared feedback を事実として残す
- preview は `今の依頼内容を表す版` として扱い、次の依頼が来たら前の preview を current へ回す昇格ルールまで含めて運用する

## Code Maker との接続

- 持ち出す zip はその時点の候補と一致している必要がある
- 取り込むときは resource を戻し、 zip 内の main.py は採用しない
- 編集面で見えたものが実ゲームの真実であることを壊さない
- zip を持ち出す前に、zip 内 `main.py` と `my_resource.pyxres` が現行 candidate と一致しているかを artifact で確かめる

## この repo への含意

- platform 変更では deployment だけでなく child agency まで done 条件に入る
- build や selector は単なる配布物生成でなく、 approval queue の UI/ops でもある
- UX policy の読みやすさと危険操作確認は、この approval flow の説明面を支える
- selector page の `あそんでみる` が dead link になると、共有と承認の loop 自体が始まらない
- `play.html` 復旧のような wrapper artifact 修正も platform ops の一部として扱う必要がある
- `tools/test_web_compat.py` の browser gate は、URL を送ったあとに
  dead-on-arrival になる版を共有前に止める
- selector 説明、preview visibility、cache bust、promotion rule は全部
  `approval queue の信頼性` の一部として見る必要がある
- `python -m http.server` のような静的配信だけでは、共有体験の事実収集まで完結しない

## 関連ページ

- [Approval Loop And Child Agency](./approval-loop-and-child-agency.md)
- [Low Friction Sharing](./low-friction-sharing.md)
- [Child Readable UX And Parent Assist](./child-readable-ux-and-parent-assist.md)
- [Parent Support Without Control](./parent-support-without-control.md)
