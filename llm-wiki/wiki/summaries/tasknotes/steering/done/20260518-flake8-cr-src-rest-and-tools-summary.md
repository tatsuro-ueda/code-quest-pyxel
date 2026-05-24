---
source: raw/tasknotes/steering/done/20260518-flake8-cr-src-rest-and-tools.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月18日 src/（scenes 除く）と tools/ に flake8-cr を適用 Summary Draft

## summary

この note は、`src/scenes/` を除く `src/` と `tools/` にまで flake8-cr 0 件を広げた記録です。自動生成ファイルは `.flake8` で除外し、手書きコードだけに Task C と同じ分割パターンを適用しました。

## key_points

- `.flake8` を新設し、`generated/` と `tile_data.py` / `sprite_data.py` を lint 対象外にした。
- E系 -> docstring -> naming -> structure -> condition -> function length の順で repo 全体へ広げた。
- `uv run flake8-cr src/ tools/ --exclude src/scenes` を 0 件にし、pytest / make verify / make build も通した。

## important_quotes

- "`自動生成ファイルは対象外`"
- "`src/ tools/ ... 0 件`"

## open_questions

- YAML/generator 側も flake8-cr 準拠へ寄せるなら、どの単位で別タスク化するべきか。
- wildcard import 許容や tools/test 系の例外を、将来どこまで減らすべきか。
