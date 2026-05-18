---
status: open
priority: normal
scheduled: 2026-05-17T00:00:00.000+09:00
dateCreated: 2026-05-17T00:00:00.000+09:00
dateModified: 2026-05-18T00:00:00.000+09:00
tags:
  - task
  - lint
  - scenes
---

# 2026年5月17日 src/scenes の CR202 大物 3 件を AI で個別リファクタ（タスク A）

> 状態：② ユーザーストーリーマップ
> 次のゲート：（ユーザー）USM を確認して承認するか直しの希望を伝える

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 機械的に直しにくい大物 3 関数を、責務が読み取れる単位まで AI 判断で分割する
> 補足：やらないこと 残り 27 件のリファクタ、SKILL.md 改訂、flake8-cr ルール改訂
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 親 `steering/done/20260517-flake8-cr-scenes.md` で CR202 以外の警告は解消済み
   2. 💦 残 30 件のうち 3 件は大物（92/89/79 行）で構造判断が要り、機械化前に AI で先行処理する

2. Before
   1. 💦 `_check_tile_events`(92), `_run_build_view_model`(89), `_run_update`(79) が責務混在で読みにくい
   2. ❌ もどかしい

3. After
   1. ✅ 大物 3 関数が全て 20 行以下に分割される
   2. ✅ pytest / make verify / make build がすべて緑
   3. ❤️ スッキリ

4. 例外
   1. 線形な計算（プレイヤー攻撃など）で乱数・副作用順を変える分割は行わない（対象 3 件は該当なし想定）

5. 境界条件
   1. 対象は上記 3 関数のみ。残り 27 件はタスク C で処理する
   2. 挙動は変えない（テスト緑を維持）
   3. リファクタ方針は SKILL.md ではなく flake8-cr ルール改訂を優先（B で対応、当タスクは個別判断）

6. 委任度
   1. 🟡 分割境界の最終判断は人と擦り合わせる -> OK
   2. 🟢 述語切り出し・private 切り出しの実装は CC のみで可
   3. 🔴 ロジックの本質を変える分割は人の判断が要る -> 聞いて下さい

---

## 2) ユーザーストーリーマップ

（Journey 承認後に記入）

---

## 3) Gherkin（完了条件）

（USM 承認後に記入）

---

## 4) Design（どうやるか）

（Gherkin 承認後に記入）

---

## 5) Tasklist

（Design 承認後に記入）

---

## 6) Result（成果物）

### 対象 3 件

| ファイル | 関数 | 行数 |
|---|---|---|
| `src/scenes/explore/presenter.py` | `_check_tile_events` | 92 |
| `src/scenes/explore/presenter.py` | `_run_build_view_model` | 89 |
| `src/scenes/explore/presenter.py` | `_run_update` | 79 |

---

## 7) Discussion（残課題の起票）

> Close 前に、残課題があるなら別 tasknote 化し、そのタイトルやパスをここに残す。

### 残課題メモ

- 残り 27 件は別タスク：`steering/20260518-flake8-cr-scenes-rest27.md`（前提条件にタスク B 完了を持つ）
- flake8-cr ルール改訂は別タスク：`steering/20260518-flake8-cr-rule-extension.md`（前提条件にタスク A 完了を持つ）

---

## 8) 参考文献

- 親タスクノート（完了済）: `steering/done/20260517-flake8-cr-scenes.md`
- 後続タスク B（flake8-cr ルール改訂）: `steering/20260518-flake8-cr-rule-extension.md`
- 後続タスク C（残り 27 件適用）: `steering/20260518-flake8-cr-scenes-rest27.md`
- 初回スキャン: `/tmp/flake8-cr-scenes-initial.txt`
