# Gherkin: Battle（戦闘・敵・呪文・バランス）

- 対象ジャーニー: J08, J10, J13, J29
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- structure-design の中心: ENEMIES/SPELLS データ構造、戦闘ロジック、バランス曲線

---

## J08: 敵が強すぎる

```gherkin
Scenario: 敵のHPを変更するとテストプレイで即座に反映される
  Given ENEMIES データに「スライム」が HP=50 で定義されている
  When 親がAIに「スライムのHPを30にして」と頼む
  And AIがコードを修正する
  And Run する
  Then スライムとの戦闘でHPが30として表示される
  And 修正から確認まで5分以内で完了する
```

```gherkin
Scenario: 敵のパラメータ変更が他のゲームシステムを壊さない
  Given 敵のHP/ATK/DEF/EXP/GOLDを変更した
  When Run してその敵と戦闘する
  Then ダメージ計算が正しく動作する
  And 勝利時に正しいEXPとGOLDが得られる
  And レベルアップ判定が正常に動作する
```

---

## J10: 新しい敵を追加したい

```gherkin
Scenario: 新しい敵をENEMIESデータに追加できる
  Given ENEMIESデータの構造（name, hp, atk, def, exp, gold, zone）がある
  When 新しい敵「ドラゴン」を追加する
  Then ENEMIESデータにドラゴンが含まれる
  And 必須フィールドがすべて埋まっている
```

```gherkin
Scenario: 追加した敵が指定ゾーンでエンカウントする
  Given 「ドラゴン」をゾーン3に出現するよう設定した
  When Run してゾーン3を歩く
  Then ドラゴンとのエンカウントが発生する
  And ゾーン0-2ではドラゴンが出現しない
```

```gherkin
Scenario: 追加した敵のスプライトがゲーム内で表示される
  Given 「ドラゴン」のスプライトをスプライトエディタで描いた
  When ドラゴンとの戦闘に入る
  Then 戦闘画面にドラゴンのスプライトが表示される
```

---

## J13: 新しい呪文がほしい

```gherkin
Scenario: 新しい呪文をSPELLSデータに追加できる
  Given SPELLSデータの構造（name, mp_cost, power, target）がある
  When 新しい呪文「ファイアボール」を追加する
  Then SPELLSデータにファイアボールが含まれる
  And 必須フィールドがすべて埋まっている
```

```gherkin
Scenario: 追加した呪文が戦闘中に使用できる
  Given 「ファイアボール」がSPELLSに追加されている
  And プレイヤーが十分なMPを持っている
  When 戦闘中に呪文メニューを開く
  Then 「ファイアボール」が選択肢に表示される
  When ファイアボールを選択する
  Then ダメージが計算され敵に適用される
  And MPが消費される
```

```gherkin
Scenario: MP不足で呪文が使えない場合のフィードバック
  Given プレイヤーのMPがファイアボールのmp_cost未満
  When 戦闘中にファイアボールを選択する
  Then 「MPがたりない」旨のメッセージが表示される
  And MPは消費されない
```

---

## J29: 全体のバランスを調整する

```gherkin
Scenario: 敵パラメータを一括で倍率調整できる
  Given 複数の敵がENEMIESデータに定義されている
  When 親がAIに「ゾーン3以降の敵のHP/ATKを1.5倍にして」と頼む
  And AIがデータを修正する
  Then ゾーン3以降の敵のHP/ATKが元の1.5倍になっている
  And ゾーン0-2の敵は変更されていない
```

```gherkin
Scenario: バランス調整後にゲームが正常に動作する
  Given 敵パラメータとEXPカーブを一括調整した
  When Run して最初から通しプレイする
  Then 各ゾーンで適切な難易度の戦闘が発生する
  And レベルアップのペースが極端に速すぎたり遅すぎたりしない
  And ゲームクリアまで到達可能である
```

```gherkin
Scenario: 友達のフィードバックからバランス調整が回る
  Given 友達がスマホでゲームをプレイして「後半簡単すぎる」と言った
  When 親がAIに「ゾーン3以降の敵を強くして」と頼む
  And 修正後にWebビルドを再実行する
  Then 友達がスマホで修正版を確認できる
  And 「ちょうどいい」か「まだ簡単」のフィードバックがその場で返る
```

---

## 共通条件

```gherkin
Scenario: ENEMIESデータの整合性
  Given ENEMIESデータに定義されたすべての敵
  Then 各敵のHP > 0, ATK > 0, DEF >= 0, EXP > 0, GOLD >= 0 である
  And zone の値が有効なゾーン番号である
```

```gherkin
Scenario: SPELLSデータの整合性
  Given SPELLSデータに定義されたすべての呪文
  Then 各呪文のmp_cost > 0, power > 0 である
  And target が有効な値（single/all）である
```
