---
source: raw/tasknotes/steering/done/20260412-guardrails-6-web-delivery-test.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# ガードレール(6) Web配信テスト Summary Draft

## summary

この tasknote は、ローカル Python では動いても Web 版で壊れる変更を承認キューへ流さないために、Playwright + Chromium Headless で `pyxel.html` を実際に開く web delivery gate を足した記録です。中心は `tools/test_web_compat.py` で 10 秒間の console error を収集し、環境依存ノイズを除いた致命的エラーだけを fail にすることでした。

## key_points

- 深層的目的は「ローカルで動いても Web 版で動かない問題を防ぐ」ことだった。
- G11 / G12 の guardrail を、emscripten 実行確認と Code Maker 互換確認の方向へ具体化した。
- `tools/test_web_compat.py` は、ローカル HTTP サーバで `pyxel.html` を配信し、Playwright で実ブラウザ起動まで通す構成を採った。
- 判定では ALSA、`favicon.ico` 404、`SharedArrayBuffer` / COOP のようなローカル環境ノイズを除外した。
- ねらいは「ローカルでは動くが Web 共有物では落ちる版」を approval queue の手前で止めることだった。
- `build_web_release.py` の file inclusion check と `code-maker.zip` の構文チェックは後続課題として残した。

## important_quotes

- "ローカルで動いてもWeb版で動かない問題を防ぐ。"
- "Web版で動かない版は承認キューに出ない"
- "Playwright + Chromium Headless で実行テスト可能と判明。"

## open_questions

- `build_web_release.py` に新規ファイル包含チェックをどこまで入れるか。
- `code-maker.zip` の構文チェックを web delivery gate と同じ段で回すか。
- `tools/test_web_compat.py` を current build の必須 gate にする運用をどこで固定するか。
