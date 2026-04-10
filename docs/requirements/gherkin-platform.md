# Gherkin: Platform（配信・Code Maker制約・体験設計）

- 対象ジャーニー: J12, J20-J23, J25-J26, J31-J33
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- structure-design の中心: Code Maker制約(C1-C7)、ビルドパイプライン、配信

---

## J12: 歩いたら壁にハマった

```gherkin
Scenario: バグ報告からAI修正→再テストが5分以内で回る
  Given 子どもがテストプレイ中にバグを発見した
  When 親がAIにバグの状況を伝える
  And AIが修正コードを生成する
  And Code Makerでコードを更新してRunする
  Then バグが修正されている
  And 報告から確認まで5分以内で完了する
```

```gherkin
Scenario: AI修正が既存機能を壊さない
  Given AIがバグ修正コードを生成した
  When 修正後のコードでRunする
  Then バグが修正されている
  And 移動・戦闘・セーブなどの既存機能が正常に動作する
```

---

## J20: 演出ON/OFFで違いを体験する

```gherkin
Scenario: 演出をOFFにしてもゲームが正常に動作する
  Given BGM/SFX/VFXがすべて有効な状態
  When 演出を無効にしてRunする
  Then ゲーム本編が正常に動作する
  And 無音・演出なしでプレイできる
```

```gherkin
Scenario: 演出をONに戻すと即座に反映される
  Given 演出が無効な状態でプレイ中
  When 演出を有効に切り替える
  Then BGM/SFX/VFXが即座に有効になる
```

---

## J21: 友達に見せる

```gherkin
Scenario: URLでブラウザからゲームをプレイできる
  Given ゲームがWebビルドされてURLが発行されている
  When 友達がスマホまたはPCのブラウザでURLを開く
  Then ゲームが読み込まれプレイ可能な状態になる
  And インストールやダウンロードが不要である
  And 会員登録やログインが不要である
```

```gherkin
Scenario: スマホで全画面プレイできる
  Given スマホのブラウザでゲームURLを開いた
  When 全画面ボタンをタップする
  Then ゲームが全画面で表示される
  And タッチ操作でプレイできる
```

```gherkin
Scenario: スマホで即プレイできることでフィードバックがもらいやすくなる
  Given 子どもが友達にゲームのURLをLINE等で送った
  When 友達がスマホでURLを開く
  Then 10秒以内にゲームがプレイ可能になる
  And 友達が「ここ難しい」「ここ面白い」等のフィードバックをその場で返せる
  And フィードバックの出し手が親子の外にまで広がる
```

---

## J22: 友達のフィードバックを反映する

```gherkin
Scenario: フィードバック→修正→再共有のサイクルがその場で回る
  Given 友達がスマホでゲームをプレイして「ここ難しい」と言った
  When 親がAIに修正を頼む
  And Code Makerでコードを更新する
  And Webビルドを再実行する
  Then 更新されたURLで修正版がプレイ可能になる
  And 友達がスマホでURLを開き直すだけで修正版を確認できる
  And フィードバックから再確認まで数分で完了する
```

```gherkin
Scenario: スマホ共有によりフィードバックサイクルが複数回転する
  Given 友達がスマホでゲームURLを開いてプレイしている
  When 友達が1つ目のフィードバックを出す
  And 親がAIで修正して再ビルドする
  And 友達がURLを開き直して修正を確認する
  Then 友達がその場で2つ目のフィードバックを出せる
  And 1回の遊びの中でフィードバック→修正のサイクルが複数回転する
```

---

## J23: スプライトを自分で描く

```gherkin
Scenario: Code MakerのSpriteエディタでキャラを編集できる
  Given Code Maker の Sprite タブが開いている
  When 子どもがピクセルを描き替える
  And Run する
  Then ゲーム内のキャラが変更後のスプライトで表示される
```

```gherkin
Scenario: スプライト編集がゲームロジックに影響しない
  Given スプライトの見た目を変更した
  When Run する
  Then キャラの移動速度・当たり判定・ステータスは変わらない
```

---

## J25: 親子で役割を交代する

```gherkin
Scenario: 何を直すかの判断は子どもが行う
  Given 友達がスマホでプレイして複数のフィードバックを出した
  When 親が子どもにフィードバックを伝える
  Then 子どもが「どれを直すか」「どの順で直すか」を決める
  And 親は子どもの判断に基づいてAIに修正を依頼する
```

```gherkin
Scenario: Tilemapエディタは誰でも操作できる
  Given Tilemap タブが開いている
  When 親がタイルを配置する
  And 子どもに操作を渡す
  And 子どもがタイルを配置する
  Then 両者の変更がどちらも正しくマップに反映される
  And 特別な権限や設定の切り替えが不要である
```

```gherkin
Scenario: テストプレイは誰でもすぐにできる
  Given Run してゲームが起動している
  When 子どもがキャラを操作してテストプレイする
  Then 特別な知識なしにゲームを遊べる
  And フィードバック（「ここ変」「ここ面白い」）を口頭で伝えられる
```

---

## J26: 「自分たちのゲーム」と言えるようになる

```gherkin
Scenario: 改造した内容がセーブされ次回も維持される
  Given Tilemapやコードを変更してRunした
  When Code Makerでプロジェクトを保存する
  And ブラウザを閉じて再度開く
  Then 前回の変更内容が維持されている
```

```gherkin
Scenario: Code Makerからダウンロードしたzipがローカルでも動く
  Given Code Maker でゲームを改造した
  When Save でzipをダウンロードする
  And ローカルのPyxel環境で実行する
  Then Code Makerと同じようにゲームが動作する
```

---

## J31: 子どもが変更を承認する

```gherkin
Scenario: 親の修正が承認されるまで反映されない
  Given 親がAIに「スライムのHPを50→30にして」と頼んだ
  And AIが修正コードを生成した
  When 承認キューに「スライムのHP: 50→30」が表示される
  Then この時点ではゲーム内のスライムのHPは50のまま変わらない
```

```gherkin
Scenario: 子どもが承認すると変更が反映される
  Given 承認キューに「スライムのHP: 50→30」が表示されている
  When 子どもが承認ボタンを押す
  And Run する
  Then スライムのHPが30として動作する
  And 承認キューからその項目が消える
```

```gherkin
Scenario: 承認キューの表示が子どもに理解できる
  Given 親がAIに修正を頼んだ
  When 承認キューに変更内容が表示される
  Then 変更内容がひらがなで「何が」「どう変わるか」表示される
  And コードの差分ではなくゲーム内の変化として説明される
```

---

## J32: 子どもが変更を却下する

```gherkin
Scenario: 子どもが変更を却下すると元のまま維持される
  Given 承認キューに「スライムのHP: 50→30」が表示されている
  When 子どもが却下ボタンを押す
  Then ゲーム内のスライムのHPは50のまま変わらない
  And 承認キューからその項目が消える
  And 却下されたことが親に通知される
```

```gherkin
Scenario: 却下後に別の案を試せる
  Given 子どもが「スライムのHP: 50→30」を却下した
  When 親がAIに別の案を頼む（例: HP 50→40）
  Then 新しい変更案が承認キューに追加される
  And 子どもが改めて承認または却下を選べる
```

---

## J33: 子どもが変更を選んで適用する

```gherkin
Scenario: 複数の変更案から子どもが選んで適用できる
  Given 承認キューに3件の変更が並んでいる
  When 子どもが2番目の変更を選んで承認する
  Then 2番目の変更のみがゲームに反映される
  And 1番目と3番目は承認キューに残る
```

```gherkin
Scenario: 子どもが適用順を決められる
  Given 承認キューに「敵のHP変更」「新しいBGM」「セリフ追加」が並んでいる
  When 子どもが「セリフ追加」を最初に承認してRunする
  And 次に「新しいBGM」を承認してRunする
  Then 各変更が子どもの選んだ順に1つずつ反映される
  And 変更ごとにテストプレイで効果を確認できる
```

```gherkin
Scenario: 不要な変更をまとめて却下できる
  Given 承認キューに複数の変更が並んでいる
  When 子どもが一部の変更を却下する
  Then 却下した変更は破棄される
  And 残りの変更は承認キューに残り個別に判断できる
```

---

## 共通条件（Code Maker制約）

```gherkin
Scenario: 配布物が2ファイルで構成される（C1）
  Given ゲームのすべてのコードとデータ
  Then 配布物は main.py と .pyxres の2ファイルのみで構成される
  And src/ や YAML への参照が存在しない
```

```gherkin
Scenario: アップロード後に何も書き換えなくても遊べる（C3）
  Given Code Maker に main.py と .pyxres をアップロードした
  When 何も編集せずに Run する
  Then ゲームが正常に起動し遊べる
```

```gherkin
Scenario: コードを1行変えると即座に変化が分かる（C4）
  Given Code Maker でゲームが動作している
  When コード内のデータ値（例: HPの数値）を1箇所変更する
  And Run する
  Then 変更した内容がゲーム内に反映されている
```

```gherkin
Scenario: エラーが出ても致命的に壊れない（C5）
  Given Code Maker でコードを編集中
  When 構文エラーを含むコードで Run する
  Then エラーメッセージがブラウザ内に表示される
  And セーブデータが失われない
  And ブラウザを閉じる必要がない
```

```gherkin
Scenario: pip install不要で動作する（A3）
  Given main.py のimport文を確認する
  Then pyxel と Python標準ライブラリ以外のimportが存在しない
```

```gherkin
Scenario: ローカルファイルへの書き込みがない（A4）
  Given main.py のコード全体を確認する
  Then open() による書き込みモードでのファイル操作が存在しない
  And セーブはブラウザのローカルストレージで永続化される
```
