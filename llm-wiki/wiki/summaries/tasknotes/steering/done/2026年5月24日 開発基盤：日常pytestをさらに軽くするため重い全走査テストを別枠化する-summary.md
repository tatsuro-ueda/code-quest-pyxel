---
source: raw/tasknotes/steering/done/2026年5月24日 開発基盤：日常pytestをさらに軽くするため重い全走査テストを別枠化する.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月24日 開発基盤：日常pytestをさらに軽くするため重い全走査テストを別枠化する Summary Draft

## summary

この note は、repo 全走査系の重い test を daily suite から外し、smoke 側へ分離して日常 pytest を大きく短縮した記録です。file 単位ではなく class / test 単位で切り分け、軽い alias unit test などは daily に残しました。

## key_points

- 現時点の仮説では、まず repo 全走査系から切るのが最も効率がよい
- 高価値 smoke は削るより、daily から分ける設計の方が筋がよい
- 実装後の standalone daily suite は `12.59s -> 4.42s` で `8.17s`、約 `64.9%` 短縮だった。まず repo 全走査系から切るという仮説は妥当だった。

## important_quotes

- "実装後の standalone daily suite は `12.59s -> 4.42s` で `8.17s`、約 `64.9%` 短縮だった。まず repo 全走査系から切るという仮説は妥当だった。"
- "`web_runtime_server` と bundle exec 群を smoke 側へ寄せても、alias unit test のような軽い部分は daily に残せた。file 単位でなく class / test 単位の分離が効いている。"

## open_questions

- なし。
