---
source: raw/tasknotes/steering/done/20260509-architecture-rules-label-ja.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 architecture_rules の `label_ja` 追加 Summary Draft

## summary

この note は、`architecture_rules.yml` の主要ブロックへ `label_ja` を追加し、人が YAML 単体で読める度合いを上げた記録です。checker/fixer 互換を崩さずに、日本語の読みやすさを局所改善しています。

## key_points

- `facts.principles`、flows、entry_points、runbooks、contracts、migration notes、validation rules など主要ブロックに `label_ja` を追加した。
- checker/fixer が current YAML に追随し、今回の docs 追加を壊さないことを確認した。
- tree node 全面展開や `repair_*` 集計名の rename は今回は scope 外として切り分けた。

## important_quotes

- "`label_ja`"
- "`主要ブロック`"

## open_questions

- tree node レベルまで日本語ラベルを広げる価値が、維持コストに見合うか。
- 互換性を崩さずに集計名を整理するなら、どの外部依存を先に調べるべきか。
