---
source: raw/tasknotes/steering/done/20260506-bgm-pyxres-ssot.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月6日 BGM の責務分担を AI / 人が読める形に整える（CJ37 の BGM 面） Summary Draft

## summary

この note は、BGM の責務を `pyxres` 正本 + scene View 直書きへ寄せ、`AudioManager` や track registry を撤去した記録です。複雑な中央管理より変更速度を優先し、scene ごとの `pyxel.playm` を新しい当たり前として定義しています。

## key_points

- まず pyxres ロード済み slot を上書きしない guard を入れ、BGM 実体を Code Maker / pyxres 側の真実へ戻した。
- `audio_system.py` から `AudioManager`、`CHIPTUNE_TRACKS`、`choose_bgm_scene`、`sync_audio` などを撤去し、各 scene View に `play_bgm()` を置いた。
- 演出 ON/OFF 機構そのものを捨て、`BGM・SFX・VFX は常に ON` という simpler contract を採用した。

## important_quotes

- "`シーンが BGM を持つ`"
- "`View が `pyxel.playm` を直接呼ぶ`"

## open_questions

- scene View ごとの小さな `if` 分岐を、どの時点まで duplication acceptable とみなすべきか。
- この no-toggle 方針を docs/test のどこまで hard guard 化するべきか。
