---
source: raw/tasknotes/steering/done/20260421-src-method-level-comments.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月21日 src/配下のメソッドに責務コメントを付与 Summary Draft

## summary

この tasknote は、コード理解を助けるために `src/` 配下へ責務コメントを広げつつ、`src/generated/` の SSoT を崩さない範囲を守った記録です。進め方の核は、まず代表 2 ファイルで日本語 1 行 docstring のスタイルを合意し、その後 `__init__` の単純代入や dataclass フィールドを避けながら 28 ファイルへ一気に展開したことでした。

## key_points

- 依頼の主語はコード改変ではなく「責務を読み取りやすくするドキュメンテーション付与」だった。
- `src/generated/` は SSoT 運用に反するため、最初から対象外に固定した。
- 代表ファイル 2 本で、日本語 1 行 docstring と既存英語 docstring の日本語統一方針を先に承認した。
- `audio_system.py` など非自明な private 関数にも責務コメントを入れ、単純な `__init__` や dataclass フィールドには付けなかった。
- 全 30 ファイルのうち 28 ファイルへ展開し、pytest 260 passed と `src/generated/` 差分なしを確認した。

## important_quotes

- "コードを理解したいから"
- "`src/generated/` はSSoT運用（project memory: ssot_policy）に反するので除外必須。"
- "日本語1行docstring・既存英語docstringも日本語に揃える"

## open_questions

- この docstring スタイルを、今後はどの document や rule に昇格するべきか。
- 責務コメントが stale になったとき、どの review で更新漏れを検知するべきか。
