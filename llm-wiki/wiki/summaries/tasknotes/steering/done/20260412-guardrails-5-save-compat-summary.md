---
source: raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# ガードレール(5) セーブ互換テスト Summary Draft

## summary

この tasknote は、AI が save schema を変えても子どもの既存データを壊さないために、固定 fixture を使う load compatibility test を build gate に入れた記録です。中心は `restore_snapshot()` が旧 save data を例外なく読めること、`SAVED_PLAYER_KEYS` の追加削除で既存データを壊さないこと、そして失敗した版を approval queue に出さないことでした。

## key_points

- 深層的目的は「ぼくのデータなくなった」を防ぐことだった。
- guardrail の主対象は save compatibility で、G10 を具体的な fixture test に落とした。
- `tests/fixtures/save_v1.json` を固定の回帰データとして持ち、`restore_snapshot()` を継続的に検証する方針を置いた。
- `SAVED_PLAYER_KEYS` から field を削除しても、残る必須キーが正常復元されることを確認対象にした。
- `SAVED_PLAYER_KEYS` に field を追加しても、旧 save data が例外なく読めることを確認対象にした。
- load test に失敗した版は approval queue に出さない、という build gate を done 条件に含めた。

## important_quotes

- "「ぼくのデータなくなった」を防ぐ。"
- "ロードテスト失敗時は承認キューに出さない"
- "フィールドの追加は安全"

## open_questions

- save compatibility test を現在の build / approval flow のどこで必須 gate にするか。
- fixture save data の更新規律を別 note として固定するか。
- `SAVE_VERSION` を上げる変更が来たとき、旧 fixture 群をどう増やすか。
