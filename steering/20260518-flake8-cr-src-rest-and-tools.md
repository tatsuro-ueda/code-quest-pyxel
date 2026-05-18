---
status: in-progress
priority: normal
scheduled: 2026-05-18T00:00:00.000+09:00
dateCreated: 2026-05-18T00:00:00.000+09:00
dateModified: 2026-05-18T00:00:00.000+09:00
tags:
  - task
  - lint
  - src
  - tools
---

# 2026年5月18日 src/（scenes 除く）と tools/ に flake8-cr を適用

> 状態：① Journey
> 次のゲート：（ユーザー）Journey の補足・境界条件・委任度を確認する

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 src/scenes/ で達成した flake8-cr 0 件を、リポジトリ全体（手書きコード）に広げて、AIコーディングの好循環をプロジェクト全体で享受する
> 補足：やらないこと 自動生成ファイル（`src/shared/constants/tile_data.py`, `src/shared/constants/sprite_data.py`, `src/generated/*`）への直接修正、`tools/architecture_rules/` 等の lint 機械化拡張、scenes/ 再走査
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 Task C 完了で `flake8-cr src/scenes/` は 0 件
   2. 💦 `uv run flake8-cr src/ tools/ --exclude src/scenes` で 10642 件、うち 80% は自動生成ファイル由来
   3. 💦 SSoT ポリシー上、`generated/` と `constants/tile_data.py` / `sprite_data.py` は YAML 由来の自動生成で手書き対象外

2. Before
   1. 💦 src/scenes/ 以外は flake8-cr 未適用で、命名・docstring・契約・関数行数のばらつきが残っている
   2. 💦 tools/ も同様で、手書きスクリプトに CR502（契約欠落）/ CR204（ステップ列違反）/ E501 が散在
   3. ❌ もどかしい

3. After
   1. ✅ `uv run flake8-cr src/ tools/ --exclude <自動生成>` が 0 件
   2. ✅ pytest / make verify / make build がすべて緑
   3. ✅ Task C と同じ「述語 + 早期 return + private 委譲 + docstring 契約」のパターンで全体が揃う
   4. ❤️ スッキリ

4. 例外
   1. 自動生成ファイル（`src/shared/constants/tile_data.py`, `src/shared/constants/sprite_data.py`, `src/generated/*`）は対象外。flake8-cr の除外指定で外す
   2. 偽陽性は flake8-cr の閾値・例外設定で対処し、コード側を歪めない
   3. `tools/test_*.py` の検証スクリプトは「ステップ列」要件を緩める可能性あり（テスト性質上）

5. 境界条件
   1. 対象は src/（scenes/ と generated/ と constants/{tile,sprite}_data.py を除く）+ tools/
   2. 機械修正可能なもの（E系・自動分割）から優先、CR系は Task C の分割パターンを再利用
   3. 挙動を変えない（pytest 緑を維持）
   4. SSoT 由来の自動生成ファイルは YAML 側 or `gen_data.py` 側を直す対象だが、今回はそこまで踏み込まない

6. 委任度
   1. 🟢 機械修正と Task C のパターン適用は CC のみで可
   2. 🟡 自動生成ファイルの扱い（除外 or `gen_data.py` 修正）の最終決定は人と相談
   3. 🟡 `tools/test_*.py` の検証スクリプトを規約対象に含めるかは人と相談

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

## 6) 作業ログ

（Tasklist 実行時に記入）

---

## 7) 評価と成果物

（完了時に記入）

---

## 8) Discussion

### 懸念事項

- （実装後に記入）

### 残課題のルール化

- （実装後に記入）

---

## 9) Closing

（Discussion 完了後に記入）

---

## 10) 参考資料

- 親系譜:
  - `steering/done/20260517-flake8-cr-scenes.md`（src/scenes 全体）
  - `steering/done/20260517-flake8-cr-scenes-cr202.md`（Task A: 大物 3 件）
  - `steering/done/20260518-flake8-cr-rule-extension.md`（Task B: CR204 ルール追加）
  - `steering/done/20260518-flake8-cr-scenes-rest27.md`（Task C: 残 27 件）
- 永続的ドキュメント:
  - `~/.claude/skills/check-python-coding-guide/SKILL.md`
- 関連メモリ:
  - `project_ssot_policy.md`（generated 一方通行）
  - `project_module_docstring_policy.md`（モジュール docstring 規約）
