---
source: raw/tasknotes/steering/done/20260507-gen-module-docstring-template.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月7日 docstring 雛形生成スクリプト（B3） Summary Draft

## summary

この note は、AST から module docstring の雛形を生成するスクリプトを足し、readability 整備の初速を上げた記録です。手で関数一覧を数える前工程を削り、docstring drift を減らすための補助具として位置づけています。

## key_points

- `tools/gen_module_docstring_template.py` が AST からトップレベル箇条書きとネスト箇条書きの雛形を stdout 出力する。
- `--force` を付けると既存 docstring を持つ file でも再生成でき、元識別子コメントを手がかりとして残す。
- `@property` getter / setter が同名で重複列挙される既知の粗さを Discussion に明示した。

## important_quotes

- "`AST → docstring 雛形`"
- "`@property` のセッター/ゲッター"

## open_questions

- `@property` 重複を generator 側でどこまで吸収するべきか。
- module docstring 以外の readability scaffold まで自動生成対象を広げるべきか。
