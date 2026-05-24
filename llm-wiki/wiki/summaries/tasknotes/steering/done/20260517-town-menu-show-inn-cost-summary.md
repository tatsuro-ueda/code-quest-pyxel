---
source: raw/tasknotes/steering/done/20260517-town-menu-show-inn-cost.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月17日 まちメニュー「やどや」に宿代を併記する Summary Draft

## summary

この note は、Town メニューの `やどや` ラベルへ宿代を併記した小さな UX 修正記録です。定数の正を変えず、Presenter の整形段だけで `やどや（5G）` / `INN (5G)` を生成する方式で既存判定を壊さずに済ませました。

## key_points

- `_build_menu_vm` が `_get_inn_cost()` と `_format_inn_label` を通してラベルを動的整形するようになった。
- TownMenuViewModel の label test を 4 ケース追加し、既存 7 テストも非破壊で維持した。
- `TOWN_MENU_LABELS` 定数は触らず、`_dispatch_confirm` の既存判定互換を守った。

## important_quotes

- "`やどや（{cost}G）`"
- "`整形段で動的に宿代を埋め込む方式`"

## open_questions

- shop 系メニューでも価格要約を出すなら、どの粒度と見せ方が child-readable か。
- 日英ラベル整形ルールを、他の動的 menu label まで共通化する必要があるか。
