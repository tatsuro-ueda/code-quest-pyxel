---
source: raw/tasknotes/steering/done/20260412-j31-fix-selector-links.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 J31 選択ページのリンク先復旧 Summary Draft

## summary

この tasknote は、子どもが selector page から 2 版を遊び比べられる状態を戻すために、欠けていた `play.html` を wrapper 生成で復旧し、`index.html -> play.html -> pyxel.html` の実リンク導線を E2E で確認した記録です。問題の芯は runtime code ではなく実 artifact の 404 にあり、preview 側の未整備と通常 build 時の `index.html` 上書きは別タスクへ切り分けました。

## key_points

- 深層的目的は、子どもが 2 版を遊び比べられる状態を取り戻すことだった。
- 問題の本体は code の内部挙動ではなく、selector page が指す `play.html` 不在による 404 だった。
- `generate_wrapper()` で `play.html` を生成し、通常版の導線を最短で復旧した。
- Playwright E2E で `index.html -> play.html -> pyxel.html` を通し、実 artifact の導線確認を done 条件にした。
- `play-preview.html` 不在はこの時点では許容し、preview 経路の復旧は別課題に残した。
- 通常 build 実行時に `index.html` が選択ページのまま維持される保証は未解決として切り分けた。

## important_quotes

- "play.html が存在しない 404"
- "子どもが2版を遊び比べられるようにする"
- "play-preview.html は未対応だが今は許容"

## open_questions

- preview 側の wrapper / artifact 導線をいつ同じ厳しさで検証するか。
- `index.html` 上書き問題を build lane の guardrail としてどこまで強化するか。
- selector page の dead link 検知を自動 test に入れるか。
