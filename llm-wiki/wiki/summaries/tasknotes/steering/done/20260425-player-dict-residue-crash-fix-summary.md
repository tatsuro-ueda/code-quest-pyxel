---
source: raw/tasknotes/steering/done/20260425-player-dict-residue-crash-fix.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月25日 game.player dict 参照の取りこぼしで落ちる現象の修復（さかのぼり） Summary Draft

## summary

この tasknote は、PlayerModel 移行後に残っていた `game.player` 系の参照漏れが status bar や ending など常時描画経路で crash を起こしていた問題を潰した記録です。修正の中心は、残存箇所を `game.player_model` 属性参照へ置き換え、`production/*` を再ビルドしたうえで、dict→dataclass リファクタでは grep を 2 段で回すべきだとルール化したことでした。

## key_points

- `game.player[` だけでなく `game.player` や変数経由の `p["key"]` が残っていると crash することが分かった。
- `status_bar.py`、`ending/scene.py`、`professor/scene.py`、`battle/scene.py` の残り参照を `player_model` 経由へ直した。
- 常時描画層の crash は unit test だけでは見落としやすく、status bar smoke の薄さも露出した。
- dict→dataclass リファクタでは、old field 名の grep と変数経由 bracket access の grep を両方残す運用を決めた。
- pre-commit / CI に grep ガードを入れる候補として M5 系ルールへ返した。

## important_quotes

- "grep パターンが甘かった。"
- "常時描画層（status_bar）のテストカバレッジが薄い。"
- "pytest だけで満足せずブラウザ検証を通す手順を必須化すべき"

## open_questions

- player dict residue を防ぐ grep ガードを、どの commit/CI 段で必須化するべきか。
- status bar のような常時描画層を、どの smoke test で安定して守るべきか。
