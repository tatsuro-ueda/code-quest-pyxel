---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/product-requirements-narrative-summary.md
  - ../summaries/knowledge/story-concepts-summary.md
  - ../summaries/knowledge/ux-policy-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j36-dialogue-ssot-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j37-dialogue-page-advance-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j38-dungeon-boss-trigger-summary.md
  - ../../raw/knowledge/docs/product-requirements-narrative.md
  - ../../raw/knowledge/docs/story-concepts.md
  - ../../raw/knowledge/docs/ux-policy.md
  - ../../raw/tasknotes/steering/done/20260412-j36-dialogue-ssot.md
  - ../../raw/tasknotes/steering/done/20260413-j37-dialogue-page-advance.md
  - ../../raw/tasknotes/steering/done/20260413-j38-dungeon-boss-trigger.md
---

# Narrative Branching And Player Guidance

## 核心

`product-requirements-narrative` は、物語を `読める` `迷わない` `選んだ結果が残る` という体験契約で捉える。`story-concepts` はその中身に philosophical spine を与え、`ux-policy` は子どもがその言葉を無理なく受け取るための表示条件を与える。

## 物語を支える条件

- セリフ変更は対象 NPC にだけ届く
- dialogue data の正本を YAML + generated に寄せても、会話変更が実ゲームへ確実に届く経路を保つ
- 複数フレーズ会話では `今の1ページだけを表示する` 責務を崩さない
- guidance は答えを言いすぎず、方向だけは失わせない
- branching は会話の変化だけでなく state に残る
- ending は ownership を完成させる
- ダンジョン最奥のような終点イベントは、silent dead end でなく
  明示トリガーと見た目の手がかりで物語へ接続する

## この repo への含意

- narrative 変更では text quality、state effect、readability を同時に見る
- battle log や landmark も story の一部として扱い、純粋な flavor text に落とさない
- guide UI を作る場合も、 exploration を奪わない最小限の示し方を優先する
- `src.dialogue_data.py` の互換を残しつつ `main.py` 同期まで通すことで、会話の正本変更が runtime 実体から外れないようにする
- 世界樹や通信塔のページ送り修正と、ダンジョン終点のボストリガー復旧は、
  narrative guidance を code path と map event の両側で支える例になった

## 関連ページ

- [Story Theme And Landmark Symbolism](./story-theme-and-landmark-symbolism.md)
- [Child Readable UX And Parent Assist](./child-readable-ux-and-parent-assist.md)
