---
source: raw/tasknotes/steering/done/2026年5月23日 開発基盤：llm-wikiをカルパシー最小形まで削減する.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月23日 開発基盤：llm-wikiをカルパシー最小形まで削減する Summary Draft

## summary

この note は、llm-wiki を一度 raw-only の Karpathy 最小形まで削ぎ落とした cleanup 記録です。helper 層や専用 tooling をまとめて外し、「まず raw だけを残す」というリセット判断を実行しました。

## key_points

- `llm-wiki/` から `README.md`、`checklists/`、`wiki/` を削除し、`raw/` だけを残した。
- `tools/gen_wiki.py` と `test/test_gen_wiki.py`、専用 rollout plan/spec/tasknote 群も削除した。
- `rg` と `pytest` で active surface に旧 helper-layer 参照が無いことを確認した。

## important_quotes

- "`raw-only`"
- "`Karpathy の最小発想に戻し`"

## open_questions

- raw-only に戻した後、次の再構築で何を最初の最小器として許すべきか。
- historical snapshot を残しつつ active surface を清潔に保つ境界を、どう維持するべきか。
