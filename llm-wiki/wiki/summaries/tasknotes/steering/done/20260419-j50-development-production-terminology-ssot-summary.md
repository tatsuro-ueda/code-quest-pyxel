---
source: raw/tasknotes/steering/done/20260419-j50-development-production-terminology-ssot.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月19日 J50 開発版 / 本番の用語を build 配布物まで統一する Summary Draft

## summary

この tasknote は、docs や UI だけでなく、build 入力・artifact・CLI に残った `preview/current` も `開発版/本番` にそろえる話をまとめた記録です。焦点は、見える言葉と内部ファイル名がずれたままだと利用者が二重の呼び名を覚える必要があり、`開発版を持ち出して編集できる` 体験を支える導線としてまだぶれるため、rename scope を配布物まで広げるべきだと整理したことでした。

## key_points

- docs と selector 表示は `開発版` / `本番` に寄ってきた一方、build flow と runtime 周辺には `preview/current` が広く残っていた。
- このずれのせいで、人は見える言葉と実ファイル名の両方を覚える必要があった。
- 問題を UI 文言だけではなく、build 入力・artifact・CLI にまたがる用語の SSOT 崩れとして扱った。
- rename scope を docs だけでなく build 配布物まで広げる前提を固定した。
- failing test を追加して `development/production` 名を期待させる進め方を置いた。
- この note は、用語統一を人間向け表示と内部運用の両方でそろえるための橋渡しになった。

## important_quotes

- "preview/current が広く残っている"
- "見える言葉と実ファイル名の両方を覚える必要がある"
- "開発版 / 本番"

## open_questions

- 用語の正本は、docs と build 配布物のどこで一致しているべきか。
- `開発版/本番` への rename は、どの artifact まで同じタイミングでそろえるべきか。
