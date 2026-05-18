---
status: open
priority: normal
scheduled: 2026-05-18T00:00:00.000+09:00
dateCreated: 2026-05-18T00:00:00.000+09:00
dateModified: 2026-05-18T00:00:00.000+09:00
tags:
  - task
  - lint
  - scenes
---

# 2026年5月18日 src/scenes 残 27 件に flake8-cr 新ルールを適用（タスク C）

> 状態：① Journey
> 次のゲート：（ユーザー）Journey を確認して承認するか直しの希望を伝える

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 タスク B で機械化したルールに沿って残り 27 件を片付け、flake8-cr 0 件を達成する
> 補足：やらないこと ルール仕様の議論（B で完了）、大物 3 件（A で完了）
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 タスク B（`steering/20260518-flake8-cr-rule-extension.md`）が完了済みで、新ルールが有効化されていること
   2. 💦 タスク A の 3 件と合わせ、CR202 違反は残り 27 件のみであること

2. Before
   1. 💦 残 27 件の関数が CR202 違反のまま、新ルールにも該当する状態
   2. ❌ もどかしい

3. After
   1. ✅ `flake8-cr src/scenes/` が 0 件
   2. ✅ pytest / make verify / make build がすべて緑
   3. ❤️ スッキリ

4. 例外
   1. 線形な計算（D 該当：`_run_do_player_attack`, `_run_do_enemy_attack`）で乱数順を変える分割は行わない
   2. 偽陽性は flake8-cr の閾値・例外設定で対処し、コード側を歪めない

5. 境界条件
   1. 対象は残り 27 件（A 3 件・D 2 件以外）
   2. 新ルールの自動修正・誘導を最大限活用、手作業は最小化する
   3. 挙動は変えない（テスト緑を維持）

6. 委任度
   1. 🟢 機械的に直せる範囲は CC のみで可
   2. 🟡 偽陽性・手作業残しの判断は人と相談
   3. 🔴 例外（D 該当）の扱いは人の判断が要る

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

### 残対象（27 件想定 — A の 3 件を除く 27 件）

カテゴリ分け（A の 3 件は除外済）：

| カテゴリ | 件数 | パターン |
|---|---|---|
| A'. 分岐 → 個別処理（タイル・フェーズ判定型） | 約 16 | 述語切り出し + 早期 return + private 切り出し |
| B'. ViewModel 組み立て（純粋関数化） | 約 5 | 行・パネルを `_build_xxx_panel` に分解 |
| C'. 描画関数 | 3 | 領域単位で `_draw_xxx` に切り出し |
| D'. 線形ロジック（例外候補） | 2 | 乱数順を実テストで検証 |

合計 26 件目安（実数はタスク B 完了時の flake8-cr 出力で再確定）。

---

## 7) Discussion（残課題の起票）

（適用完了後に記入）

---

## 8) 参考文献

- 先行タスク A: `steering/20260517-flake8-cr-scenes-cr202.md`
- 先行タスク B: `steering/20260518-flake8-cr-rule-extension.md`
- 親タスクノート（完了済）: `steering/done/20260517-flake8-cr-scenes.md`
