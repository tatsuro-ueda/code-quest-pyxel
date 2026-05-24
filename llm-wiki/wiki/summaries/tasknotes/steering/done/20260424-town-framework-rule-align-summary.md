---
source: raw/tasknotes/steering/done/20260424-town-framework-rule-align.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月24日 town/ を framework-rule.md に沿って整える Summary Draft

## summary

この tasknote は、town/shop の買い物エラーを場当たり修正で終わらせず、`framework-rule.md` に合わせて PlayerModel 導入と scene 分解まで進めた記録です。修正の核は、`game.player` dict を全廃して `PlayerModel` を shared state の正本にし、`GameState.current_town` を導入し、最後には `src/scenes/town/scene.py` を削除して runtime dispatcher が Presenter / View を直接呼ぶところまで整えたことでした。

## key_points

- 直接原因は shop が `game._current_town_index()` と `game.town_menu_pos` で town 内部をのぞいていたことだった。
- ユーザー判断で `scene.py` 廃止、PlayerModel 導入、shop→town 受け渡しの `GameState.current_town` 化を今回スコープに含めた。
- `game.player` dict を全 scene / service から廃止し、`PlayerModel` と `PlayerItem` を shared state の正本にした。
- town を model / presenter / view / view_model に分解し、最後に `town/scene.py` を完全削除した。
- 233 tests green と grep 検証で、`player` dict 旧参照と town scene 旧参照が消えたことを確認した。

## important_quotes

- "`scene.py` は **不要**（Presenter が `update` / `draw` 入口を兼ねる）"
- "`game.player` dict を全 scene / service から廃止。"
- "`src/scenes/town/scene.py`（47 行の薄い配線）を削除。"

## open_questions

- browser 手動確認を、今後どの guardrail で置き換えるか。
- battle / explore など他 scene の framework-rule 適合を、どの順で進めるべきか。
