---
source: raw/tasknotes/steering/done/20260425-menu-shim-crash-fix.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月25日 メニューの せってい / AIでしゅうせい 選択で AttributeError（さかのぼり） Summary Draft

## summary

この tasknote は、menu から `せってい` と `AIでしゅうせい` を選ぶと、存在しない Game shim を呼んで落ちていた問題を修復したさかのぼり記録です。修正の中心は、`game._open_settings` / `game._enter_ai_help` を scene 実体の `settings_scene.open("menu")` と `ai_help_scene.enter()` へ差し替え、fake が実体を裏切らないよう regression test も実 API 準拠へ合わせたことでした。

## key_points

- menu scene は存在しない Game shim を経由して settings / AI help を開こうとしていた。
- 呼び出し先を `settings_scene.open("menu")` と `ai_help_scene.enter()` に直し、scene の実 API へ寄せた。
- `test_cjg_menu_navigation.py` の fake も本物の API 署名へ合わせ、nonexistent shim を呼ばない回帰テストを追加した。
- unit test fake が実体を追認してしまうパターンは、静的 grep guard も必要だと分かった。
- `game._*(` 呼び出し全体の棚卸しと M5 系 grep guard 追加を次タスク候補へ残した。

## important_quotes

- "fake が実体を裏切るパターンは grep 静的ガードで補完するしかない"
- "Game にメソッドが無いのに scene から `game._method(` を呼ぶ"
- "random sampling が効いた"

## open_questions

- scene からの `game._*(` 呼び出しを、どの静的 guard で網羅的に止めるべきか。
- fake object の API 署名同期を、どの test convention として固定するべきか。
