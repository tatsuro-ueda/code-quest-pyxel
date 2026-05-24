---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/product-requirements-platform-summary.md
  - ../summaries/knowledge/ux-policy-summary.md
  - ../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-5-save-compat-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j31-fix-selector-links-summary.md
  - ../../raw/knowledge/docs/product-requirements-platform.md
  - ../../raw/knowledge/docs/ux-policy.md
  - ../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md
  - ../../raw/tasknotes/steering/done/20260412-j31-fix-selector-links.md
---

# Platform Sharing And Approval Ops

## 核心

`product-requirements-platform` は、共有、再修正、承認、巻き戻しを 1 つの運用系としてまとめる。友達に URL を送るだけで遊べ、感想を受けて数分で直し、子どもが development と production を比べて採否を決めるところまでが platform の仕事になる。

## 共有と承認の loop

- URL だけで即プレイできる低摩擦共有
- フィードバックをその場で修正して再共有できる loop
- play log で「届いたか」を次の行動へつなげる
- 開発版 / 本番版の比較で承認、却下、再提案、巻き戻しを回す
- approval queue に出す前に save compatibility を通し、既存セーブを壊す版を共有前に止める

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

## 関連ページ

- [Approval Loop And Child Agency](./approval-loop-and-child-agency.md)
- [Low Friction Sharing](./low-friction-sharing.md)
- [Child Readable UX And Parent Assist](./child-readable-ux-and-parent-assist.md)
- [Parent Support Without Control](./parent-support-without-control.md)
