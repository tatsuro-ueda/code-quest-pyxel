---
source: raw/tasknotes/steering/done/20260420-cj24-codemaker-sfx-roundtrip.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月20日 CJ24 Soundエディタで作ったSFXを本編で鳴らす Summary Draft

## summary

この tasknote は、Sound エディタで作った SFX を selector import から本編再生まで失わず通す `CJ24` の round-trip を復旧した記録です。修正の中心は、`SfxSystem` が `pyxel.load()` 後に固定 `SFX_DEFINITIONS` を書き戻す挙動をやめ、slot に既に入っている imported SFX を truth として優先するようにしたことでした。

## key_points

- image bank 側は解消済みで、残るズレは Sound / Music 側に絞られていた。
- `CJ24` の done は「Sound エディタで作った音がゲーム内で使われる」ことだと定義した。
- 壊れていたのは selector import より runtime overwrite であり、`SfxSystem` が populated slot を潰していた。
- code-side asset 新設ではなく、imported slot を truth とする方針で修正した。
- `test/test_cj24_sound_editor_truth.py` と full pytest 260 passed で round-trip を固定した。

## important_quotes

- "Sound エディタで作った音がゲーム内で使われる"
- "壊れていたのは import 経路より runtime overwrite だった。"
- "`SfxSystem` が Sound editor の結果を潰さないことは今回閉じるべきだった。"

## open_questions

- 同じ truth rule を Music / BGM までどこまで広げるべきか。
- imported SFX が既定音と違うとき、子ども向け説明をどこまで用意するべきか。
