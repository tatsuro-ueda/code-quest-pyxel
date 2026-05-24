---
source: raw/tasknotes/steering/done/20260507-bundle-rebuild-after-bgm-ssot.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月7日 bundle 再ビルド（BGM pyxres SSoT 反映） Summary Draft

## summary

この note は、BGM pyxres SSoT 変更後に `dist` artifact を再ビルドし、bundle の中身まで旧 audio 設計が残っていないことを確認した記録です。コード変更だけで終わらず、配布物の実体を見に行く運用をそのまま残しています。

## key_points

- `dist/code-maker.zip`、`dist/pyxel.html`、`dist/pyxel.pyxapp`、`dist/play.html`、`dist/index.html` を再生成した。
- bundle 内 `main.py` で `AudioManager` / `SettingsScene` 0 件、`pyxel.playm(` 5 件を確認した。
- BGM SSoT 後の build 手順と `PYTHONPATH` の注意点も docs 化の必要として残した。

## important_quotes

- "`bundle 再ビルド`"
- "`pyxel.playm(`: 5 件"

## open_questions

- bundle 内自己検査を、どこまで `make verify` の自動 gate に上げるべきか。
- release build の検収項目を docs と scripts のどちらへ重心置きすべきか。
