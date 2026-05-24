---
source: raw/tasknotes/steering/done/20260420-cj26-static-codemaker-upload.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月20日 CJ26 static な top page でも Code Maker zip を戻せるようにする Summary Draft

## summary

この tasknote は、runtime server がない static host でも Code Maker zip を戻せるように、upload UI の責務を browser 保存へ切り分け直した記録です。修正の中心は、server import API 前提で disabled になっていたカードをやめ、`templates/codemaker_import_ui.js` で zip を localStorage に保存し、起動前に `my_resource.pyxres` だけを staging する browser-first の経路を成立させたことでした。

## key_points

- top page の upload カードは見えていても、server API がないと動かない偽 affordance になっていた。
- static host で必要なのはまず browser 保存であり、server import API と責務を混ぜない方針へ切り替えた。
- `templates/codemaker_import_ui.js` が zip を localStorage に保存するようになった。
- `main.py` / `main_development.py` は保存済み zip から `my_resource.pyxres` だけを staging する。
- static 配信 + Playwright で、status 表示と localStorage 保存が本当に動くことを確認した。

## important_quotes

- "static host で必要なのはまず browser 保存"
- "できそうに見えて動かない"
- "Code Maker 単一ファイル制約を壊すため、そこだけ inline のまま残すのが妥当だった。"

## open_questions

- browser 保存だけで使える範囲を、親子にどこまで明示するべきか。
- shared な import 経路と local fallback の違いを、どの画面で説明するべきか。
