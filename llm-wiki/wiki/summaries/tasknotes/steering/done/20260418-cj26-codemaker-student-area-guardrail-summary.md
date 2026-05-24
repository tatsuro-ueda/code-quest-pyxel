---
source: raw/tasknotes/steering/done/20260418-cj26-codemaker-student-area-guardrail.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月18日 CJ26 Code Maker 教材版で編集可能領域を明示しコア改変時は停止する Summary Draft

## summary

この tasknote は、Code Maker の単一 `main.py` 制約の中で、子どもが触ってよい場所を示し、コアを壊したときは止まる教材 guardrail を入れる話を整理した記録です。要点は、通常の project のようなファイル分離による保護が使えないため、完全ロックではなく `ここを触る` と `ここを壊したら止める` を最小構成で入れて、学びの自由と事故防止の両方を守ろうとしたことでした。

## key_points

- Pyxel Code Maker は単一 `main.py` をその場で編集して実行する環境で、通常の編集可否分離が使えない。
- 現状の `code-maker.zip` には、子どもが触ってよい場所の明示が無かった。
- この問題を `CJ26` の編集体験と `CJ25` の役割交代を支える教材 guardrail として扱った。
- 本物のロックを目指すより、`ここを触る` と `ここを壊したら止める` を最小構成で入れる方が現実的だとした。
- `STUDENT AREA` とコア自己検査の責務を build 生成物側に限定する前提を固定した。
- この note は、編集の自由を残しつつコア改変を止める線引きを決めるための設計メモになった。

## important_quotes

- "単一 `main.py`"
- "ここを触る"
- "ここを壊したら止める"

## open_questions

- 教材 guardrail は、どこまで止めると学びを守りつつ触る自由も残せるのか。
- `STUDENT AREA` とコア領域の境界は、どんな編集を基準に決めるべきか。
