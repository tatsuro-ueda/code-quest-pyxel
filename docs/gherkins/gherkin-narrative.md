# Gherkin: Narrative（ダイアログ・ストーリー・ナビ）

- 対象ジャーニー: J09, J14, J27, J30
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- structure-design の中心: dialogue_data, structured_dialog, ストーリー分岐、エンディング

---

## J09: セリフを変えたい

```gherkin
Scenario: NPCのセリフを変更するとテストプレイで即座に反映される
  Given 町のNPCに「ようこそ」というセリフが設定されている
  When 親がAIに「この町人のセリフを冒険者っぽくして」と頼む
  And AIがダイアログデータを修正する
  And Run する
  Then NPCに話しかけると新しいセリフが表示される
  And 修正から確認まで5分以内で完了する
```

```gherkin
Scenario: セリフ変更が他のダイアログを壊さない
  Given 特定のNPCのセリフを変更した
  When Run して他のNPCに話しかける
  Then 変更していないNPCのセリフは元のまま表示される
```

```gherkin
Scenario: ひらがな表記でセリフが表示される
  Given セリフデータにひらがな表記のテキストがある
  When NPCに話しかける
  Then セリフがひらがなで正しく表示される
  And デフォルトフォントで豆腐（文字化け）にならない
```

---

## J14: マップが広すぎて迷う

```gherkin
Scenario: 次の目的地へのガイドが表示できる
  Given ストーリー進行に応じた次の目的地が設定されている
  When 子どもがフィールドを歩いている
  Then 次の目的地の方向が何らかの方法で示される
```

```gherkin
Scenario: ガイドがストーリー進行に連動する
  Given 目的地Aに到達してイベントを完了した
  When フィールドに戻る
  Then ガイドが次の目的地Bを示すように更新される
```

---

## J27: ストーリーの分岐を作る

```gherkin
Scenario: ダイアログに選択肢を追加できる
  Given NPCとの会話データがある
  When 親がAIに「王様の依頼にはい/いいえの選択肢を追加して」と頼む
  And AIがダイアログデータに選択肢を追加する
  Then 会話中に選択肢が表示される
  And 選択肢を選べる
```

```gherkin
Scenario: 選択肢によって会話の続きが変わる
  Given 王様の依頼に「はい」「いいえ」の選択肢がある
  When 「はい」を選ぶ
  Then 依頼を受けた旨のセリフが表示される
  When 「いいえ」を選ぶ
  Then 別のセリフ（断った反応）が表示される
```

```gherkin
Scenario: 選択結果がゲーム状態に反映される
  Given 選択肢による分岐がフラグと紐づいている
  When 「いいえ」を選ぶ
  Then 対応するフラグが設定される
  And 以降のゲーム進行がフラグに応じて変化する
```

---

## J30: エンディングを自分たちで書く

```gherkin
Scenario: エンディングのセリフを変更できる
  Given エンディング画面に表示されるテキストがある
  When 親がAIに「エンディングのセリフを変えて」と頼む
  And AIがエンディングデータを修正する
  And Run してゲームをクリアする
  Then 変更後のセリフがエンディング画面に表示される
```

```gherkin
Scenario: クレジットに名前を入れられる
  Given エンディングにクレジット表示がある
  When クレジットのテキストに子どもの名前を追加する
  And Run してエンディングに到達する
  Then クレジットに子どもの名前が表示される
```

```gherkin
Scenario: エンディング変更がゲーム本編を壊さない
  Given エンディングのデータを変更した
  When Run してゲーム本編をプレイする
  Then エンディング以外のゲーム進行が正常に動作する
```

---

## 共通条件

```gherkin
Scenario: ダイアログデータの整合性
  Given ダイアログデータに定義されたすべての会話
  Then 各会話のテキストが空でない
  And 参照されるNPC/場所のIDが有効である
  And 選択肢がある場合、各選択肢に遷移先が設定されている
```

```gherkin
Scenario: ダイアログ表示がCode Makerで正常に動作する
  Given Code Maker 上でゲームを実行する
  When NPCに話しかける
  Then ダイアログが正常に表示される
  And 外部ファイル参照（open等）を使用していない
```
