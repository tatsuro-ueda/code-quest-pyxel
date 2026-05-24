---
source: raw/tasknotes/steering/done/20260507-src-header-functions-for-all-files.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月7日 src/ ファイル先頭に関数一覧コメントを全体へ広げる Summary Draft

## summary

この note は、src header / verify / CJ map / hook integration の読みやすさ改善 backlog を 4 本の実装タスクへ分解し、完走させた umbrella 記録です。単一の大きい note を抱え込まず、実施可能な単位へ割る方が進むという判断を残しています。

## key_points

- 未実装だった 4 シナリオを `verify-scripts-and-makefile`、`gen-module-docstring-template`、`scene-to-cj-map`、`build-hook-ci-integration` の 4 note に切り出した。
- `battle/view.py` への docstring 追加はパターンの実証として位置づけ、その後の横展開や verifier を別 note で扱った。
- 親 note は umbrella として残し、実装の正本は分離した各 subtask note 側へ置く構造になった。

## important_quotes

- "`12 シナリオのうち未実装だった 4 件`"
- "`4 つのサブタスクノート`"

## open_questions

- 4 本へ分けた readability policy を、将来どこで 1 つの stable rule set へ戻すべきか。
- src 全 file に同じ docstring 深さを求めるかどうかを、どの基準で切り分けるべきか。
