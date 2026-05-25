---
source: docs/product-requirements-narrative.md
source_type: doc
status: active
origin:
  - docs/product-requirements-narrative.md
last_synced: 2026-05-23
last_ingested: 2026-05-23
size_class: large
---

# Product Requirements Narrative Summary

## TL;DR

この source は、セリフ、目的地ガイド、会話分岐、エンディングを `子どもが読めて、自分で選んだと感じられる形` へ保つ。中心は `dialogue.yaml 由来の会話変更` `迷わせすぎない導線` `選択が会話と state の両方を変える分岐` `最後の言葉まで自分たちの作品にする ending ownership` である。

## 主要トピック

- NPC のセリフを変えたら、その NPC にだけすぐ反映される
- 子どもが迷わないよう、次の目的地は示しつつ答えの言いすぎは避ける
- 選択肢は表示され、会話の続きを変え、ゲーム state に残る
- エンディングとクレジットは「自分たちのゲーム」感を強める
- ひらがな中心で読みやすく、文字化けしない表示を守る

## 深い洞察

- narrative の価値は物語量より `読めること` と `選択が効くこと` にある
- guidance は攻略の答えではなく、探索が止まらない最小限の方向づけとして設計される
- ending 編集は cosmetic ではなく ownership の証明になる

## キーワード

- product-requirements-narrative
- dialogue
- guidance
- branching
- ending
- child-readable text

## 注意点

- 汎用の目的地ガイド UI はまだ未実装で、現状は一部の導線や会話が支えている
- branching は構造上可能でも、本編全体で強く使われている範囲は限定的である
