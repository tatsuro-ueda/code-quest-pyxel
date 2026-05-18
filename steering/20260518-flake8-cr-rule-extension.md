---
status: open
priority: normal
scheduled: 2026-05-18T00:00:00.000+09:00
dateCreated: 2026-05-18T00:00:00.000+09:00
dateModified: 2026-05-18T00:00:00.000+09:00
tags:
  - task
  - lint
  - flake8-cr
---

# 2026年5月18日 flake8-cr に構造化リファクタ誘導ルールを追加（タスク B）

> 状態：① Journey
> 次のゲート：（ユーザー）Journey を確認して承認するか直しの希望を伝える

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 制御構造のリファクタ方針を flake8-cr に機械化し、CC が判断で迷わない状態を作る
> 補足：やらないこと SKILL.md（check-python-coding-guide）の改訂、コード本体の修正
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 タスク A（`steering/20260517-flake8-cr-scenes-cr202.md`）が完了済みであること
   2. 💦 A の 3 件で得た「望ましい構造」を機械検出するルールに落とし込む素材があること
   3. 💦 既存 flake8-cr（`~/dotfiles/shared/flake8-coding-rules`）には構造化リファクタを誘導する検出が無い

2. Before
   1. 💦 SKILL.md の述語切り出し指示は AI の解釈でブレる
   2. ❌ 不安

3. After
   1. ✅ flake8-cr が「ステップ列のみの public 関数」「述語切り出し済み」を機械検出できる
   2. ✅ ルール改訂が dotfiles に commit / push 済み
   3. ❤️ 安心

4. 例外
   1. 既存コードに大量の偽陽性が出る場合は閾値で緩和、または段階導入

5. 境界条件
   1. 対象は `~/dotfiles/shared/flake8-coding-rules` のみ
   2. 新ルールは CR204 以降の番号を割り当て
   3. テストケースは `tests/` に追加してから本実装へ進む（TDD）

6. 委任度
   1. 🟡 ルール仕様の決定は CC が原案、ユーザー承認
   2. 🟢 AST 検出ロジックの実装・ユニットテストは CC のみで可
   3. 🔴 dotfiles への commit / push は人の最終承認後

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

### 検討中の論点

- **新ルール候補**
  - CR204: public 関数は「述語呼び出し + private 呼び出し + return」のステップ列のみ許可
  - その他、A で得た構造から逆算
- **採用しない判断軸**
  - dispatch dict / match/case はガイドの主軸にしない（A の経験から早期 return + 述語で 90% カバー可と分かれば）

---

## 7) Discussion（残課題の起票）

（議論完了後に記入）

---

## 8) 参考文献

- 先行タスク A: `steering/20260517-flake8-cr-scenes-cr202.md`
- 後続タスク C: `steering/20260518-flake8-cr-scenes-rest27.md`
- flake8-cr 本体: `~/dotfiles/shared/flake8-coding-rules`
- 参考ガイド: `~/.claude/skills/check-python-coding-guide/SKILL.md`
