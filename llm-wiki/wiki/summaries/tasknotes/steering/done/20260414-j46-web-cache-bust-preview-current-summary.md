---
source: raw/tasknotes/steering/done/20260414-j46-web-cache-bust-preview-current.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月14日 J46 preview/current の古い配信物をブラウザに使わせない Summary Draft

## summary

この tasknote は、preview/current の HTML が毎回同じ URL で配られていたため、ブラウザが古い artifact を握り続けられる問題を、build token 付き URL で直した記録です。修正の要点は、通常の静的配信を捨てずに、`play*.html` と `pyxel*.html` の参照先へ versioned query string を流し、build 内容に応じて cache bust できるようにしたことでした。

## key_points

- preview 用 `main.py` は直っていても、ブラウザが古い HTML を使う余地があった。
- `selector -> play-preview.html -> pyxel-preview.html` が固定 URL だったことが原因だった。
- まず versioned URL の failing test を書いて Red を固定した。
- `tools/build_web_release.py` に build token と versioned asset URL を追加した。
- current / preview の両方で `?v=...` 付き URL を生成するようにした。
- build test、全体 pytest、web compat、live runtime で token 付き URL を確認した。

## important_quotes

- "静的配信のまま cache bust ができる。"
- "build token"
- "ブラウザが古い html を掴む余地がある。"

## open_questions

- このキャッシュ対策は、どの配布物まで広げるのがちょうどよいか。
- build token の決め方は、今の依存ファイル基準でどこまで十分か。
