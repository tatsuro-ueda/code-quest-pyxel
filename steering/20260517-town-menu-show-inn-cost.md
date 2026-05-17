---
status: in-progress
priority: normal
scheduled: 2026-05-17T20:00:00.000+09:00
dateCreated: 2026-05-17T20:00:00.000+09:00
dateModified: 2026-05-17T20:00:00.000+09:00
tags:
  - task
---

# 2026年5月17日 まちメニュー「やどや」に宿代を併記する

> 状態：① Journey
> 次のゲート：（ユーザー）Journey 修正・承認

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 子どもが「いまここで泊まると何G減るか」を選ぶ前に分かり、安心して決められる
> 補足：やらないこと ぶきや / ぼうぐや / どうぐや のラベルには値段を併記しない（複数アイテムで価格が一意でないため）
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 町ごとの宿代は `shops.yaml` の `inn_prices`（フォールバックは `INN_COST=10`）
   2. 💦 まちメニューラベルは `TOWN_MENU_LABELS` の固定タプルで、ラベルは静的に決まっている
   3. 💦 町ごとの宿代は `TownPresenter._get_inn_cost()` で取得済み

2. Before
   1. 💦 「やどや」を選んでも、決定するまで何 G かかるか見えない
   2. 💦 所持金が足りずに `INN_LACK_MSG` が出るまで気づけないことがある
   3. ❌ もどかしい

3. After
   1. 💦 まちメニュー画面で「やどや（5G）」のように費用が見える
   2. ✅ 子どもが所持金と見比べて泊まるか決められる
   3. ❤️ 安心

4. 例外
   1. 日本語フォントが無いとき（英語ラベル）の表示揺れ
   2. 町 index が INN_PRICES の範囲外（フォールバック INN_COST）のとき

5. 境界条件
   1. ラベル文字列幅が広がるとメニューウィンドウのレイアウトに収まるか
   2. 「やどや」以外のラベル（ぶきや等）には値段を出さない

6. 委任度
   1. 🟢 全体としてCC単独で進められる
   2. 🟢 CCのみで可：Presenter で labels を組み立てる際に「やどや」だけ宿代を埋め込む実装
   3. 🟡 一部判断要：英語ラベル `INN` 時の表記（`INN (5G)` か否か）はユーザー確認

---

## 2) ユーザーストーリーマップ

> 委任度：🔴 まだ書かれていない
> 残る曖昧さ：Journey 承認後に組み立てる

---

## 3) Gherkin（完了条件）

> 委任度：🔴 まだ書かれていない
> 残る曖昧さ：USM 承認後に組み立てる

---

## 4) Design（どうやるか）

（USM・Gherkin 承認後に記入）

---

## 5) Tasklist

（Design 承認後に記入）

---

## 6) Result（成果物）

（実行後に記入）

---

## 7) Discussion（残課題の起票）

### 残課題メモ

- なし（実行後に更新）

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：

---

## 8) 参考文献

- `src/scenes/town/presenter.py` `_get_inn_cost` / `_build_menu_vm`
- `src/scenes/town/view_model.py` `TownMenuViewModel`
- `src/shared/constants/game_config.py` `TOWN_MENU_LABELS` / `INN_COST`
- `src/game_data.py` `INN_PRICES`（shops.yaml 由来）
