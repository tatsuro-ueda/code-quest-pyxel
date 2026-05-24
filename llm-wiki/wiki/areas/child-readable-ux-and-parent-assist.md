---
status: active
last_updated: '2026-05-24'
sources:
- ../summaries/knowledge/ux-policy-summary.md
- ../summaries/knowledge/product-requirements-platform-summary.md
- ../summaries/knowledge/product-requirements-narrative-summary.md
- ../summaries/tasknotes/steering/done/20260412-j31-fix-selector-links-summary.md
- ../summaries/tasknotes/steering/done/20260412-j38-preview-build-flow-summary.md
- ../summaries/tasknotes/steering/done/20260413-j37-dialogue-page-advance-summary.md
- ../summaries/tasknotes/steering/done/20260413-j38-dungeon-boss-trigger-summary.md
- ../summaries/tasknotes/steering/done/20260414-j33-selector-change-list-ssot-summary.md
- ../summaries/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime-summary.md
- ../summaries/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen-summary.md
- ../summaries/tasknotes/steering/done/20260416-j48-preview-must-reflect-current-request-summary.md
- ../../raw/knowledge/docs/ux-policy.md
- ../../raw/knowledge/docs/product-requirements-platform.md
- ../../raw/knowledge/docs/product-requirements-narrative.md
- ../../raw/tasknotes/steering/done/20260412-j31-fix-selector-links.md
- ../../raw/tasknotes/steering/done/20260412-j38-preview-build-flow.md
- ../../raw/tasknotes/steering/done/20260413-j37-dialogue-page-advance.md
- ../../raw/tasknotes/steering/done/20260413-j38-dungeon-boss-trigger.md
- ../../raw/tasknotes/steering/done/20260414-j33-selector-change-list-ssot.md
- ../../raw/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime.md
- ../../raw/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen.md
- ../../raw/tasknotes/steering/done/20260416-j48-preview-must-reflect-current-request.md
- ../summaries/tasknotes/steering/done/20260420-cj26-codemaker-resource-import-summary.md
- ../../raw/tasknotes/steering/done/20260420-cj26-codemaker-resource-import.md
- ../summaries/tasknotes/steering/done/20260420-cj26-static-codemaker-upload-summary.md
- ../../raw/tasknotes/steering/done/20260420-cj26-static-codemaker-upload.md
- ../summaries/tasknotes/steering/done/20260505-index-html-kid-pixel-redesign-summary.md
- ../../raw/tasknotes/steering/done/20260505-index-html-kid-pixel-redesign.md
- ../summaries/tasknotes/steering/done/20260517-town-menu-show-inn-cost-summary.md
- ../../raw/tasknotes/steering/done/20260517-town-menu-show-inn-cost.md
- ../summaries/tasknotes/steering/done/20260517-shop-owned-marker-clipping-summary.md
- ../../raw/tasknotes/steering/done/20260517-shop-owned-marker-clipping.md
- ../summaries/tasknotes/steering/done/20260517-inn-skip-when-full-hp-summary.md
- ../../raw/tasknotes/steering/done/20260517-inn-skip-when-full-hp.md
- ../summaries/tasknotes/steering/done/2026年5月24日 アプリ：Code Maker版ステータスバーのzone名描画で未定義エラー-summary.md
- ../../raw/tasknotes/steering/done/2026年5月24日 アプリ：Code Maker版ステータスバーのzone名描画で未定義エラー.md
---


# Child Readable UX And Parent Assist

## 核心

`ux-policy` は、子どもに見える画面を `読める` `今やることが分かる` `押した実感が返る` に固定する。同時に `platform` と `narrative` は、親が通訳や決定者になりすぎず、説明と承認と導線が子ども側で理解できることを要求している。

## 見える interaction rule

- ひらがな中心で内部用語を出しすぎない
- 同時に複数の案内を重ねない
- 押した直後の feedback を返す
- 危険操作は確認を入れて無言で通さない
- selector page で `あそんでみる` が dead link にならず、子どもが親のデバッグなしで遊び始められる状態を保つ
- 複数フレーズ会話では current page だけを見せ、前ページが残らないようにする
- selector の変更説明は、実際の preview 差分と一致している必要がある
- `おためしばん` は `今の依頼を表す版` として読める必要がある
- preview source が無いときは、古い card を見せるより card 自体を出さないほうが child-facing に正直である

## 親の補助境界

- 親は技術翻訳や実装手数を引き受けても、決定権は奪わない
- 次の目的地や変更説明は、親の口頭補足なしでも分かる形を目指す
- 共有や approval UI も子どもが自分で比較判断できる説明面を持つ

## この repo への含意

- UX review では文言、layout、input feedback、agency の 4 つを同時に見る
- Code Maker 境界や CJ44 simplicity は UX の外側の話ではなく、子どもの理解可能性に直結する
- child-facing selector の wrapper artifact 欠損も UX 破綻として扱い、単なる build 失敗で片付けない
- preview/current の compare route が崩れないことも、子どもが自分で選ぶための
  読みやすさ条件に含まれる
- 最奥の目印キャラのような `次に踏む場所が見て分かる` 手がかりは、
  口頭説明の代わりになる child-facing UX である
- stale な説明や stale preview は、build の問題である前に
  `子どもが読んで誤解する UX` の問題である
- preview の説明を build-owned に寄せると、親の口頭補足なしでも比較しやすくなる
- Code Maker import UI は、zip 内 code を使わず resource だけを戻すことを parent の口頭補足なしでも誤解しにくい形で見せる必要がある。
- static host では、動かない server-dependent カードを残すより browser 保存で本当に動く導線を見せる方が child-facing に正直である。

- the kid-pixel index redesign improved the first page children see without disturbing the existing Code Maker and play flows.

- showing inn cost up front, replacing clipped shop ownership badges with short readable messages, and skipping inn stays at full HP/MP all reduce small but compounding child confusion at decision points.

- the Code Maker status-bar alias fix matters here too because an undefined zone-name crash breaks one of the first child-facing cues in the editor shell.

## 関連ページ

- [Platform Sharing And Approval Ops](./platform-sharing-and-approval-ops.md)
- [Narrative Branching And Player Guidance](./narrative-branching-and-player-guidance.md)
- [Parent Support Without Control](./parent-support-without-control.md)
- [Approval Loop And Child Agency](./approval-loop-and-child-agency.md)
