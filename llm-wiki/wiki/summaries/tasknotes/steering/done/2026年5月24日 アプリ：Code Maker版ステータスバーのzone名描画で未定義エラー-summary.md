---
source: raw/tasknotes/steering/done/2026年5月24日 アプリ：Code Maker版ステータスバーのzone名描画で未定義エラー.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 アプリ：Code Maker版ステータスバーのzone名描画で未定義エラー Summary Draft

## summary

この note は、Code Maker 版ステータスバーで zone 名描画が未定義エラーになる問題を、local module alias の bundler 規則へ揃える形で直した記録です。status bar 個別修正ではなく `import src.<local module> as alias` 全般を `alias = M` に寄せる方針へ広げました。

## key_points

- 今回の修正は `import src.<local module> as alias` 全般を `alias = M` に寄せるので、status bar 以外の同種 alias にも効く
- 既存の `M` alias は special-case のまま据え置き、`M = M` のような無意味な出力は避けた
- #### 残課題1: module import alias 全般の横展開確認

## important_quotes

- "今回の修正は `import src.<local module> as alias` 全般を `alias = M` に寄せるので、status bar 以外の同種 alias にも効く"
- "既存の `M` alias は special-case のまま据え置き、`M = M` のような無意味な出力は避けた"

## open_questions

- なし。
