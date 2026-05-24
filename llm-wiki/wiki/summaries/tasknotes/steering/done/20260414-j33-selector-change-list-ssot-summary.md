---
source: raw/tasknotes/steering/done/20260414-j33-selector-change-list-ssot.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月14日 J33 選択ページの変更説明が実変更とずれる Summary Draft

## summary

この tasknote は、selector の変更説明が実際の build 内容とずれていた問題を、表示ミスではなく Source of Truth の破綻として扱い直した記録です。中心は、`top_changes.json` のような説明 metadata が実ソースより古くても build が通ってしまう状態をやめ、子どもが比較や承認に使う change list を stale なまま出せない guardrail へ寄せたことでした。

## key_points

- `index.html` の説明は更新されていても、実変更を表していないことがあった。
- 問題は build failure ではなく、selector 説明の SoT failure と整理された。
- 根本原因は、normal build が stale な `top_changes.json` をそのまま信用していたことだった。
- 手動更新を前提に残すとしても、古い説明のまま build/push できない guardrail が必要だと判断した。
- stale metadata を build/test で検知する方針を固定した。
- この修正は `CJ31/CJ33` の「子どもが説明を信じて比較できる」導線を守るためのものだった。

## important_quotes

- "build failure ではなく SoT failure"
- "対応するソースより古ければ失敗する"
- "今回何が変わったか"

## open_questions

- 変更説明は、どのファイルを正本として作るのがいちばんぶれにくいか。
- selector の説明を build がどこまで自動で持つべきか。
