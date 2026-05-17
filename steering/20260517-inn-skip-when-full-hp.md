---
status: in-progress
priority: normal
scheduled: 2026-05-17T22:00:00.000+09:00
dateCreated: 2026-05-17T22:00:00.000+09:00
dateModified: 2026-05-17T22:00:00.000+09:00
tags:
  - task
---

# 2026年5月17日 やどやでHP満タンなら泊まらずメッセージだけ出す

> 状態：① Journey 素案
> 次のゲート：（ユーザー）Journey 素案を修正・承認する

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 子どもが「いま泊まる必要が無い」ことを払う前に知り、無駄遣いで損した気持ちにならないで済む
> 補足：やらないこと 「げんきまんたん」以外の親切判定（コイン残量警告・自動でひとこと等）まで広げない
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 `PlayerModel.stay_at_inn(cost)` は所持金チェックだけ見て、満タン判定をせずに HP/MP 全回復＋gold減算をする（`src/shared/state/player_model.py:210-218`）
   2. 💦 `TownPresenter._stay_at_inn` は 2 値（成功＝INN_OK_MSG / 失敗＝INN_LACK_MSG）でしか分岐していない（`src/scenes/town/presenter.py:280-292`）
   3. 💦 やどやのメッセージ文言は `src/shared/constants/game_config.py` の `INN_OK_MSG` / `INN_LACK_MSG` に SSoT がある

2. Before
   1. 💦 HP/MP が満タンでもやどやを選ぶと、宿代だけ引かれてしまう
   2. 💦 子どもがあとから所持金を見て「あれ、減ってる」と気づき損した気分になる
   3. ❌ もどかしい

3. After
   1. 💦 満タンでやどやを選ぶと「すでに げんきまんたんだ！」と表示される
   2. ✅ 所持金は減らず、HP/MP もそのまま、まちメニューへ戻れる
   3. ❤️ 安心

4. 例外
   1. HPは満タンだが MP が減っている場合に、回復させたいかスキップしたいか
   2. HP/MP 満タンでも毒状態が残っているケース（宿で毒解除されるため、スキップすると治せなくなる）
   3. 英語フォント表示時の文言（`ALREADY FULL HP!` 等）も併せて足すか

5. 境界条件
   1. 「げんきまんたん」の定義を `hp == max_hp` だけにするか、`mp == max_mp` と `not poisoned` まで含めるか
   2. メッセージ表示後の遷移は既存の `_enter_message` 経路に乗せ、まちメニューへの戻り方は INN_OK_MSG と揃える

6. 委任度
   1. 🟡 全体としては一部判断要：満タン判定の条件と英語文言の扱いをユーザー確認したい
   2. 🟢 CCのみで可：判定条件と文言が決まれば、Presenter / PlayerModel / テスト追加までは自走できる
   3. 🔴 人の判断：満タン判定の範囲（HPのみ／HP+MP／HP+MP+毒）と、英語フォント時の表示

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

- 関連 tasknote：`steering/done/20260517-town-menu-show-inn-cost.md`（やどや宿代併記、同テーマの直前タスク）
- 関連 tasknote：`steering/20260517-shop-owned-marker-clipping.md`（下部メッセージ枠の流用パターン参考）
- 関連コード：`src/scenes/town/presenter.py` `_stay_at_inn`（行 280-292）
- 関連コード：`src/shared/state/player_model.py` `stay_at_inn`（行 210-218）
- 関連コード：`src/shared/constants/game_config.py` `INN_OK_MSG` / `INN_LACK_MSG`（行 69-70）
