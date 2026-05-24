---
source: raw/tasknotes/steering/done/20260505-detach-index-html-from-build.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月5日 トップページの「あたらしくなったこと」を commit log から自動更新する（build からは切り離す） Summary Draft

## summary

この note は、トップページの「あたらしくなったこと」更新を build から切り離し、render script + hook + static guard へ移した記録です。`make build` が `index.html` を上書きする regression を dead code 削除ごと構造的に塞いでいます。

## key_points

- `tools/render_top_changes.py` を新設し、`top_changes.json` からの pure render を build とは独立させた。
- `build_web_release.py` と `render_release_selector.py` から top page 生成責務を外し、`index.html` への build 書き込みを止めた。
- post-commit hook による `top_changes.json` 自動更新と、G1/G2/G3 static guard を導入した。

## important_quotes

- "`build からは切り離す`"
- "`make build` が `index.html` を上書きする regression`"

## open_questions

- Anthropic API key がある実環境で hook の change-summary 品質をどう観測するべきか。
- G1 guard を `dist` rename や将来の変数名変更にどう追従させるべきか。
