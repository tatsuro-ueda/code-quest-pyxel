---
source: raw/tasknotes/steering/done/20260418-cj35-preview-prebattle-scene-sync.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月18日 CJ35 preview の prebattle scene 欠落を子どもに届けない Summary Draft

## summary

この tasknote は、preview でボス前 scene が欠けた不具合を、ゲームロジックではなく preview bundle の同期漏れとして切り分けた記録です。ポイントは、`assets/dialogue.yaml` と generated には scene が存在するのに preview 実物へ入っていなかったことから、問題の本体を runtime ではなく preview 生成経路の stale 同期と見て、scene 欠落を検知する回帰テストまで含めて守ろうとしたことでした。

## key_points

- preview で魔王タイルに乗ると `unknown scene: boss.glitch.prebattle_01` が出ていた。
- `assets/dialogue.yaml` と `src/generated/dialogue.py` には対象 scene が存在していた。
- 一方で `main_preview.py` の inlined dialogue には scene が無く、実物 preview は stale のままだった。
- そのため、問題をゲームロジックではなく preview bundle の生成経路の壊れ方として整理した。
- root cause を dialogue 同期漏れとして固定し、scene 欠落を検知する包括的な回帰テストを追加対象にした。
- この note は、preview にだけ起きる実物差分をどう守るかの guardrail メモになった。

## important_quotes

- "unknown scene: boss.glitch.prebattle_01"
- "ゲームロジックではなく preview bundle の生成経路が壊れている"
- "実物は stale のままになる"

## open_questions

- preview bundle の同期漏れを防ぐには、どの生成経路まで同じ検査で守るべきか。
- dialogue の実物差分は、preview 専用の guardrail としてどこまで独立に扱うべきか。
