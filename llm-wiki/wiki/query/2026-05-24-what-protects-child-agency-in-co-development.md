---
status: active
created: 2026-05-24
question_type: synthesis
sources:
  - ../areas/parent-support-without-control.md
  - ../areas/approval-loop-and-child-agency.md
  - ../areas/child-readable-ux-and-parent-assist.md
  - ../areas/platform-sharing-and-approval-ops.md
  - ../areas/fast-feedback-development-loop.md
---

# What Protects Child Agency In Co-Development

## Question

子どもの主体性を守りながら子どもといっしょにゲーム開発する上で大切なことは？

## Answer

llm-wiki の答えは、「親や AI がたくさん手伝ってもよいが、`何をよしとするか` を決める人は最後まで子どもであること」です。そのためには、親は実装やビルドや配信の手数を引き受けても、決定権までは持たない必要があります。[Parent Support Without Control](../areas/parent-support-without-control.md)

さらに大切なのは、それを気持ちの問題で終わらせず、仕組みにすることです。開発版と本番版を比べて、子どもが承認、却下、選択、巻き戻しまでできる approval loop があると、親や AI が「勝手に反映する」流れを止められます。[Approval Loop And Child Agency](../areas/approval-loop-and-child-agency.md) [Platform Sharing And Approval Ops](../areas/platform-sharing-and-approval-ops.md)

画面や説明の作り方も重要です。子どもが読める言葉で、今やることが分かり、親の口頭通訳なしでも比較判断できる UI でないと、表面上は選べても実質的には親主導になります。[Child Readable UX And Parent Assist](../areas/child-readable-ux-and-parent-assist.md)

最後に、開発の速さも主体性に関係します。`作る -> 遊ぶ -> 直す -> また遊ぶ` を短く回せると、子どもが見つけた違和感がそのまま次の判断につながります。逆に遅すぎると、子どもは乗客になりやすくなります。[Fast Feedback Development Loop](../areas/fast-feedback-development-loop.md)

## Evidence

- 親の役割は「実装手数を引き受けても、決定権は子どもに残す」と整理されている
- approval loop は、承認、却下、選択、巻き戻しまでを product の仕組みとして持つ
- UX は、子どもが自分で読めて判断できる説明面を持つことが求められる
- platform は、development と production を比べて採否を決める運用まで含む
- fast feedback loop は、子どもの違和感を次の判断へつなぐ速度条件として扱われる

## Confidence

High. 親の役割、approval loop、UX、platform ops、fast feedback の 5 本が、別々の page で同じ方向を指している。
