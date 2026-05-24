---
source: raw/tasknotes/steering/2026年5月24日 開発基盤：capture-and-ingest-sourceに要約確認ゲートを追加する.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：capture-and-ingest-sourceに要約確認ゲートを追加する Summary Draft

## summary

この note は、`human feedback -> draft file` が直結していた flow をほどき、summary preview を chat で確認してから file 化する review gate を追加した記録です。fast path があっても review gate を飛ばさず、方向ズレを file 化前に止める方針を置きました。

## key_points

- いまの skill は `human feedback -> key_points 確定 -> summary draft file` が直結している
- 今回はその直結をほどき、preview を chat 上で承認してから final file へ進む形に変える
- fast path があっても review gate は飛ばさない方針にしておくと、方向ズレを file 化前に止めやすい

## important_quotes

- "いまの skill は `human feedback -> key_points 確定 -> summary draft file` が直結している"
- "fast path があっても review gate は飛ばさない方針にしておくと、方向ズレを file 化前に止めやすい"

## open_questions

- なし。
