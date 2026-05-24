---
source: raw/tasknotes/steering/done/20260420-cj26-codemaker-audio-code-import.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月20日 CJ26 Code Maker の Sound / Music を code asset として取り込む Summary Draft

## summary

この tasknote は、Code Maker で作った Sound / Music が本編に残らない問題を、audio import の責務分離として切り出した設計記録です。中心となる判断は、音の authoring は人が持ち、scene / event がどの音を鳴らすかは code が持つと分け、`AudioManager` / `SfxSystem` の固定再初期化と import/build 経路を別責務として扱うことでした。

## key_points

- `pyxel.load()` の後に `sounds` / `musics` を固定データで再初期化していたため、Code Maker で作った音が本編に残らなかった。
- 問題は audio asset の authoring と runtime playback selection が混ざっていることだった。
- image bank 系は scope から外し、Sound / Music だけを code asset import へ寄せる方針にした。
- `CJ15/CJ16/CJ17/CJ24/CJ26` と関連 gherkin を、authoring / import / playback / build の責務で切り分ける設計を始めた。

## important_quotes

- "Code Maker で作った `Sound / Music` が本編に残らない。"
- "音の authoring は人、scene / event の選択は code"
- "`Sound / Music` だけを code asset import へ寄せる"

## open_questions

- Sound と Music を、同じ import 経路で扱うべきか分けて扱うべきか。
- Code Maker authorship を壊さずに、audio を code asset とどう接続するべきか。
