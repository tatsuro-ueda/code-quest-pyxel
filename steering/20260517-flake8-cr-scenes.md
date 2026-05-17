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

> 状態：③ Gherkin
> 次のゲート：（CC）Gherkin を書いて approve commit する

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
   1. ✅ src/scenes 全 11 シーンで `flake8-cr` の指摘が 0 件
   2. ✅ `make verify` と `pytest` がどちらも緑のまま
   3. ❤️ スッキリ

4. 例外
   1. 修正で挙動が変わりそうな箇所は事前に相談してから直す
   2. テストが落ちたらその場で止めて原因を共有する

5. 境界条件
   1. 修正対象は `src/scenes/**/*.py` のみ（11 シーン全部を 1 ノートで進める）
   2. SSoT（YAML→generated）には触れない
   3. 構造系（CR202/CR203/CR301/CR303）も今回まとめて直す
   4. 完了判定は `flake8-cr src/scenes/` が 0 件 ＋ `make verify` ＋ `pytest` が緑

6. 委任度
   1. 🟡 全体としては一部判断要（どこまで構造を変えるかをユーザーと擦り合わせる必要がある）
   2. 🟢 機械修正系（F401 / E501 / E701 / E702 / W391）は CC のみで可
   3. 🟢 docstring 追加系（CR501 / CR502 / CR601）は雛形があるので CC のみで可
   4. 🔴 関数分割や述語関数化（CR202 / CR203 / CR301 / CR303）は責務設計に踏み込むので人の判断が要る

---

## 2) ユーザーストーリーマップ

> ユーザー：src/scenes を直したい AI / 大人（自分）
> 委任度：🟢 機械修正と docstring 雛形までは CC が進められる。構造系の関数分割は実装中に都度判断
> 残る曖昧さ：なし

1. 👀 `tasknote確認済み`：`steering/done/20260507-src-header-functions-for-all-files.md` と `steering/done/20260507-gen-module-docstring-template.md` を読み、モジュール docstring の方針と雛形生成 CLI の存在を再確認する
2. 👀 `skill・tool・MCP確認済み`：`flake8-cr`（CLI）、`tools/gen_module_docstring_template.py`、`make verify`、`pytest`、`manage-tasknotes` Skill。MCP は 0件
3. 👀 `flake8-cr src/scenes/` を初めて流し、500 件超の指摘とコード別件数（CR502・CR203・E501・CR601…）が並ぶのを見る
4. 💦 件数の多さに圧倒されるが、種別ごとに難易度が違うことに気付く
5. 📝 ベースライン（コード別件数）を tasknote に控え、ゴールを「0 件」に固定する
6. 🎬 まずは機械修正できる種別（F401・E501・E701・E702・W391）をシーン横断で一気に直し、件数が大きく減る手応えを得る
7. 🎬 次にモジュール docstring（CR601）を雛形 CLI で生成し、Problems: セクションを各ファイルに足す
8. 🎬 続いて関数 docstring（CR501・CR502）を実装に合わせて埋める
9. 🎬 軽い構造系（CR201・CR100・CR101・CR102）を、挙動を変えないリネームだけで片付ける
10. 🎬 重い構造系（CR202・CR203・CR301・CR302・CR303）は、シーンごとに 1 つずつ関数を分割し、その都度 `pytest` で挙動が変わっていないかを確認する
11. 🔁 段落の節目に `flake8-cr src/scenes/` を流し、残り件数が減っていくのを Result に書き残す
12. ❤️ `flake8-cr src/scenes/` が 0 件、`make verify` 緑、`pytest` 緑になり、上から読めるシーンになったところでスッキリと終わる

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
