---
source: raw/tasknotes/steering/done/20260517-flake8-cr-scenes-cr202.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月17日 src/scenes の CR202 大物 3 件を AI で個別リファクタ（タスク A） Summary Draft

## summary

この note は、Explore 系の CR202 大物 3 関数を AI 判断で分割し、責務パターンを後続ルール化へ渡した実装記録です。`_run_update`、`_run_build_view_model`、`_check_tile_events` を 20 行以下へ分けつつ、副作用順序は変えませんでした。

## key_points

- CR202 対象だった 3 関数を、述語切り出し・private 委譲・早期 return で分割した。
- `pytest` / `make verify` / `make build` を green に保ったまま終えた。
- 後続の CR204 ルール化へ向けて、望ましい分割パターンを Discussion に抽出した。

## important_quotes

- "`述語呼び出し + private 呼び出し + return のステップ列`"
- "`副作用順序の保存原則`"

## open_questions

- 画面遷移や描画回帰を含む変更では、headless screenshot check をどこまで標準化するべきか。
- ExploreViewModel 側の大きな field 数を、次はどこまで設計から薄くするべきか。
