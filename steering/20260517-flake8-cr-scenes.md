---
status: open
priority: normal
scheduled: 2026-05-17T00:00:00.000+09:00
dateCreated: 2026-05-17T00:00:00.000+09:00
dateModified: 2026-05-17T00:00:00.000+09:00
tags:
  - task
  - lint
  - scenes
---

# 2026年5月17日 src/scenes に flake8-cr を適用して直す

> 状態：① Journey
> 次のゲート：（ユーザー）Journey を確認して承認するか直しの希望を伝える

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 src/scenes のコードを「上から読めば責務がわかる」状態に揃え、AI/人がすぐ直せる土台を整える
> 補足：やらないこと src/scenes 以外への波及修正、ロジックそのものの再設計、テスト追加までは広げない
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 flake8-cr は `dotfiles/shared/flake8-coding-rules` を経由して動く
   2. 💦 初回スキャンで src/scenes には 508 件の指摘が出ている（CR502 が 179 件で最多）
   3. 💦 src/scenes は MVP（model/view/view_model/presenter/scene）で 11 シーンが並ぶ

2. Before
   1. 💦 シーン間で docstring・命名・関数長の流儀がバラバラ
   2. 💦 update()/draw() に制御フローが直接書かれ、変更コストが高い
   3. ❌ もどかしい

3. After
   1. ✅ 機械修正できる指摘（未使用 import / 行長 / 複文 / 末尾改行）は 0 件
   2. ✅ docstring 系（CR501/CR502/CR601）は src/scenes 全ファイルで整っている
   3. ✅ 構造系（CR201/CR202/CR203/CR301-303/CR100-102）は対応方針が決まり、影響が少ないものから直されている
   4. ❤️ スッキリ

4. 例外
   1. リファクタリングで挙動が変わるリスクが高いものは別 tasknote に切り出す
   2. テストが緑のままを保てない修正は、その場で止めて相談する

5. 境界条件
   1. 修正対象は `src/scenes/**/*.py` のみ
   2. SSoT（YAML→generated）には触れない
   3. 既存テストはすべて通った状態をゴールにする

6. 委任度
   1. 🟡 全体としては一部判断要（どこまで構造を変えるかをユーザーと擦り合わせる必要がある）
   2. 🟢 機械修正系（F401 / E501 / E701 / E702 / W391）は CC のみで可
   3. 🟢 docstring 追加系（CR501 / CR502 / CR601）は雛形があるので CC のみで可
   4. 🔴 関数分割や述語関数化（CR202 / CR203 / CR301 / CR303）は責務設計に踏み込むので人の判断が要る

---

## 2) ユーザーストーリーマップ

> Gherkin の前に、今回の仕事をどの順番で進めるかだけをそろえる。
> 委任度：🔴 まだ Journey 段階。スコープ確定が先
> 残る曖昧さ：今回の範囲を 11 シーン全部にするか、優先順位を付けて段階的にやるか

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

（実行後に記入）

---

## 7) Discussion（残課題の起票）

（実行後に記入）

---

## 8) 参考文献

- 初回スキャン結果: `/tmp/flake8-cr-scenes-initial.txt`（508 件）
- 過去ノート: `steering/done/20260507-src-header-functions-for-all-files.md`（モジュール docstring の方針）
- 過去ノート: `steering/done/20260507-gen-module-docstring-template.md`（docstring 雛形生成スクリプト）
- 既存 memory: `project_module_docstring_policy.md`（src/ 配下の docstring ポリシー）
