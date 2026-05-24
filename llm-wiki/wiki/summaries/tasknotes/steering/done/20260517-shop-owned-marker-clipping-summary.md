---
source: raw/tasknotes/steering/done/20260517-shop-owned-marker-clipping.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月17日 ぶきや「もっています」表示が画面右端で切れる Summary Draft

## summary

この note は、Shop の「もっています」表示が右端で切れる問題を、行内ラベルを捨てて短期メッセージ表示へ置き換えた記録です。`message_ttl` を Model に持たせ、購入/重複/不足のフィードバックを 2 秒だけ優先表示する形へ整理しました。

## key_points

- `ShopModel.message_ttl` と `MESSAGE_TTL_FRAMES = 60` を追加した。
- `_set_short_message` と `_resolve_display_message` を経由して、短期 message > owned 判定 > none の優先順を作った。
- 行内 `[もっています]` は完全削除し、横幅切れ問題を構造的に消した。

## important_quotes

- "`短期 message > ... > None`"
- "`行内 [もっています] は完全削除`"

## open_questions

- 将来「同種装備所持」のような複雑判定を増やすなら、PlayerModel API をどこまで広げるべきか。
- 短期メッセージ TTL 2 秒を、UX ルールとして他 scene へも使うべきか。
