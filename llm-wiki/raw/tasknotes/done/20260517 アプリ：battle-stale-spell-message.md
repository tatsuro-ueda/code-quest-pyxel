---
status: done
priority: normal
scheduled: 2026-05-17T22:30:00.000+09:00
dateCreated: 2026-05-17T22:30:00.000+09:00
dateModified: 2026-05-23T09:40:00+00:00
tags:
  - task
---

# 2026年5月17日 アプリ：battle-stale-spell-message

> 状態：⑧ Closing
> 次のゲート：（CC）なし

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 子どもが直前に出たメッセージと、いま選んでいるメニューを混同せず、戦闘を落ち着いて進められる
> 補足：やらないこと Window 抽象化（枠＋中身を束ねるクラス）や XY 座標廃止リファクタには今回踏み込まない。CJ44「便利だけど複雑な仕組みは変える速さを奪う」に従い、配置責務の見直しは別 Could tasknote として切り出すだけにする
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 じゅもん未習得時、`BattlePresenter.update` は `m.text = "まだ じゅもんを おぼえていない"` を立てるが `m.phase` を変えずに `"menu"` のまま残す（`src/scenes/battle/presenter.py:80-85`）
   2. 💦 メニューから「どうぐ」を選ぶと `m.phase = "item_select"` へ進むが、`m.text` をクリアする処理が無い（`src/scenes/battle/presenter.py:86-88`）
   3. 💦 `BattleView.draw` は `vm.main_text` が None でない限りメッセージ枠を描き、同時に `vm.sub_panel`（アイテム一覧）も別座標で描くため重なる（`src/scenes/battle/view.py:97-123`）

2. Before
   1. 💦 戦闘でじゅもんを選び「まだじゅもんをおぼえていない」が出たあと、どうぐを選ぶと前のメッセージが消えずに重なって読めない
   2. 💦 子どもが「いま何が起きてるの？」と混乱し、戦闘の入口で詰まる
   3. ❌ もどかしい

3. After
   1. 💦 メニュー遷移時に前回メッセージは自然に消え、いま選んでいる操作だけが見える
   2. ✅ 今日中に tasknote を done に閉じられ、「ひとつ完了した」感覚で次の「こうしたい」へ進める
   3. ❤️ スッキリ

4. 例外
   1. メッセージを「あえて残しておきたい」フェーズ（攻撃結果表示中など `m.text_timer > 0` の間）はクリアしない
   2. メニュー戻り操作（B/Esc）でクリアすべきかは、修正後の挙動を見て後追い判断する

5. 境界条件
   1. 修正は presenter 側（`m.phase` 遷移時に `m.text = ""`）か view 側（`vm.sub_panel is not None` のとき `vm.main_text` を抑制）のどちらかを選ぶ。最小差分で済む方を採る
   2. 配置責務見直し（Window 抽象化）は **このノートの射程外**。同じパターンの重なりバグが 3 回再発したら、別 Could tasknote を昇格させる条件付き

6. 委任度
   1. 🟢 全体として CC 単独で実行可能：スコープがバグ修正のみに絞られたため、Gherkin・Design・Tasklist・実装まで自走できる
   2. 🟢 CCのみで可：presenter / view どちらで直すかの判断と、最小差分での実装＋テスト追加
   3. 🟡 一部確認したい：英語フォント時の文言扱い（既存の他バグ修正と揃えるか）だけは念のため聞く可能性あり

---

## 2) ユーザーストーリーマップ

> 委任度：🟢 bugfix と検証まで CC が進められる
> 残る曖昧さ：なし

### 話題1：再現条件を presenter 遷移へ閉じ込める

##### ユーザー：私

1. 当初計画
    1. 👀 じゅもん未習得メッセージの発火条件を固定する
    2. 👀 item menu へ入る瞬間に stale text が残ることを再現する
    3. ✂️ submenu 遷移時だけ text をクリアする最小差分を選ぶ

### 話題2：wiki/checklist の試運転に使う

##### ユーザー：私

1. 当初計画
    1. 📚 `ux-policy` と `ux-checklist` から「今の操作だけを見せる」を確認する
    2. 📚 `framework-checklist` から presenter 側で閉じる方針を確認する
    3. ✅ bugfix 後に battle task を wiki の試運転記録へ流用する

---

## 3) Gherkin（完了条件）

> 委任度：🟢 実装とテスト追加まで CC が完走できる
> 残る曖昧さ：なし

- [x] シナリオ1：未習得 spell メッセージは item menu へ持ち越さない

1. 🧱 じゅもん未習得の状態で spell を選ぶと `まだ じゅもんを おぼえていない` が menu 上に出る
2. 🎬 その直後に item menu を開く
3. ✅ `item_select` に遷移し、前のメッセージは空になる

- [x] シナリオ2：timed result message の経路は変えない

1. 🧱 run fail や item use success は `text_timer` 付きで結果表示を行う
2. 🎬 submenu 遷移の stale text だけを修正する
3. ✅ run / item / spell の timed result 経路は既存テストのまま通る

---

## 4) Design（どうやるか）

- **関連スキル・MCP**：`manage-tasknotes`, `test-driven-development`

### 【参照】

- Steering: `steering/2026年5月22日 開発基盤：LLM Wiki shared packageを導入して自律実行ルートを固定する.md`
- Architecture: `wiki/checklists/framework-checklist.md`
- UXPolicy: `docs/ux-policy.md`

### 変更範囲

- やること:
  - `BattlePresenter` の submenu 遷移で stale text をクリアする
  - regression test を追加する
- やらないこと:
  - window 抽象化
  - 座標系の整理
  - timed result message の表示仕様変更

### 検証

- 検証コマンド:
  - `python -m pytest test/test_cjg_battle_stale_spell_message.py -q`
  - `python -m pytest test/test_battle_run_logic.py test/test_cjg_battle_spell_effects.py -q`
- 成功条件:
  - stale spell message regression が防がれる
  - run / spell effect の既存テストが壊れない
- 未実施時の扱い:
  - 画面 overlap の再現確認ができないので done にしない

---

## 5) Tasklist

- [x] battle task を wiki/checklist の試運転候補に選んだ
- [x] `wiki/wiki/indexes/tasknotes.md` から open task として引けることを確認した
- [x] `docs/ux-policy.md` / `wiki/checklists/ux-checklist.md` から「今の操作だけを見せる」を確認した
- [x] `wiki/checklists/framework-checklist.md` から presenter 側の最小差分を選んだ
- [x] failing test `test/test_cjg_battle_stale_spell_message.py` を追加した
- [x] `BattlePresenter` に submenu 遷移時の text clear を実装した
- [x] targeted pytest を通した

---

## 6) Result（成果物）

- `src/scenes/battle/presenter.py` で spell / item submenu を開く瞬間に `model.text = ""` を行うようにした
- `test/test_cjg_battle_stale_spell_message.py` を追加し、未習得 spell メッセージが item menu に持ち越されないことを固定した
- 試運転では `areas/current-state` を使わず、`indexes/tasknotes.md` と checklist docs だけでも前進できることを確認した

---

## 7) Discussion（残課題の起票）

### 残課題メモ

- 今回の bug は presenter 側で閉じたため、window 抽象化は不要のまま保留にした
- 同種の重なりが 3 回再発したら別 note で window 責務整理を切る
- 別tasknoteにした場合のタイトル or パス：`steering/2026年5月23日 アプリ：battle-window-overlap-policy.md`

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：glitch-lord prebattle 会話の open task へ戻る

---

## 8) 参考文献

- 参考画像：`steering/2026年5月17日まだじゅもんをおぼえていない.png`
- 関連コード：`src/scenes/battle/presenter.py:69-101`（menu / spell_select 分岐、`m.text` 設定箇所）
- 関連コード：`src/scenes/battle/view.py:97-123`（メッセージ枠と sub_panel の描画、絶対座標直書き）
- 関連コード：`src/scenes/battle/view_model.py:29,44`（`main_text` / `info_message` の責務コメント）
- 関連コード：`src/scenes/battle/scene.py:48-49,121-220`（`m.text` / `m.text_timer` の他用例）
- 関連 tasknote：`steering/20260517-inn-skip-when-full-hp.md`（同日の戦闘・町メッセージ系タスク、進行中）
- 関連 tasknote：`steering/done/20260507-src-header-functions-battle-view.md`（battle/view モジュール docstring 整備）
