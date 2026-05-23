---
status: open
priority: normal
scheduled: 2026-05-17T22:30:00.000+09:00
dateCreated: 2026-05-17T22:30:00.000+09:00
dateModified: 2026-05-23T04:10:24+00:00
tags:
  - task
---

# 2026年5月17日 アプリ：battle-stale-spell-message

> 状態：① Journey 素案
> 次のゲート：（ユーザー）Journey 素案を修正・承認する

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

（フェーズ2で記入）

---

## 3) Gherkin（完了条件）

（フェーズ3で記入）

---

## 4) Design（どうやるか）

（フェーズ4で記入）

---

## 5) Tasklist

（フェーズ5で記入）

---

## 6) Result（成果物）

（フェーズ6で記入）

---

## 7) Discussion（残課題の起票）

### 残課題メモ

- なし / 残課題を書く
- 別tasknoteにした場合のタイトル or パス：`path/to/tasknote.md`

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：

---

## 8) 参考文献

- 参考画像：`steering/2026年5月17日まだじゅもんをおぼえていない.png`
- 関連コード：`src/scenes/battle/presenter.py:69-101`（menu / spell_select 分岐、`m.text` 設定箇所）
- 関連コード：`src/scenes/battle/view.py:97-123`（メッセージ枠と sub_panel の描画、絶対座標直書き）
- 関連コード：`src/scenes/battle/view_model.py:29,44`（`main_text` / `info_message` の責務コメント）
- 関連コード：`src/scenes/battle/scene.py:48-49,121-220`（`m.text` / `m.text_timer` の他用例）
- 関連 tasknote：`steering/20260517-inn-skip-when-full-hp.md`（同日の戦闘・町メッセージ系タスク、進行中）
- 関連 tasknote：`steering/done/20260507-src-header-functions-battle-view.md`（battle/view モジュール docstring 整備）
