---
source: raw/tasknotes/steering/done/20260414-j45-noise-guardian-event-only-preview.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月14日 J45 ノイズガーディアンをイベント専用に戻して preview へ載せる Summary Draft

## summary

この tasknote は、イベント専用敵として印付けされていた `ノイズガーディアン` が通常遭遇候補に混ざっていた問題を、既存フラグを正しく使う最小修正で分離した記録です。ポイントは、新しい汎用仕組みを足すのではなく、`is_noise_guardian: true` を見て field encounter からだけ外し、通信塔イベント戦は残したまま preview build で検証したことでした。

## key_points

- `ノイズガーディアン` はイベント敵フラグを持っていたが、通常遭遇候補生成側がそれを見ていなかった。
- 問題の本体は、イベント専用敵が field encounter に混ざりうることだった。
- 通信塔イベント戦は別経路なので、通常遭遇候補からだけ外せば目的を満たせた。
- 最小修正として、`_build_zone_enemies()` の encounter 候補から `is_noise_guardian` を除外した。
- 修正は current 直書きではなく preview 用入力へ閉じ込め、比較導線の意味を保った。
- preview build と全体 pytest で、通常遭遇停止とイベント戦維持の両方を確認した。

## important_quotes

- "通常遭遇候補からだけ外せば目的を満たせる。"
- "既存 `is_noise_guardian` を正しく使う"
- "イベント用の敵が field encounter に混ざりうる"

## open_questions

- イベント用の敵と普通の敵の境界を、今後どう保つべきか。
- preview で試したこの分離ルールを、本番までどこまで広げるべきか。
