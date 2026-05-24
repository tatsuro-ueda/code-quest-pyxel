---
source: raw/tasknotes/steering/done/20260418-cj26-preview-codemaker-download.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月18日 CJ26 開発版 Code Maker zip を index.html から落とせるようにする Summary Draft

## summary

この tasknote は、preview を遊べるだけでなく、そのまま Code Maker に持っていける zip download 導線を `開発版` カードに載せる話を整理した記録です。焦点は、ローカルで手作業なら preview zip を作れても、配布物として再現可能な build flow に乗っていなかったため、人が期待する `開発版カードからそのまま Code Maker に入れられる preview zip` を正面から扱う必要があると定義したことでした。

## key_points

- 現状の `index.html` には preview の play 導線はあるが、Code Maker 用 zip の入口が無かった。
- `tools/build_codemaker.py` も current の `main.py` 固定で、preview 用 artifact 生成責務が無かった。
- 手元で preview zip を作れても、それは再現可能な build flow には乗っていなかった。
- 人が期待するのは `開発版カードからそのまま Code Maker に入れられる preview zip` だと整理した。
- まずは upload / import まで広げず、download 導線だけを閉じる scope に絞った。
- この note は `CJ26` を preview round-trip の入口として扱うための download 側の整理になった。

## important_quotes

- "開発版カードから、そのまま Code Maker に入れられる preview zip"
- "再現可能な build flow"
- "download 導線だけに絞る"

## open_questions

- `開発版を持ち出して編集できる` を満たすには、download 導線のどこまでを一連の流れとして扱うべきか。
- preview zip の生成責務は、build のどの段階で current 向け artifact と分けるべきか。
