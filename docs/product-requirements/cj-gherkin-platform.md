# カスタマージャーニーgherkin: Platform（配信・Code Maker制約・体験設計）

- 対象カスタマージャーニー: CJ12, CJ20-CJ23, CJ25-CJ26, CJ31-CJ34
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- structure-design の中心: Code Maker制約(C1-C7)、ビルドパイプライン、配信

---

## CJG12: 歩いたら壁にハマった

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

## CJG20: 演出ON/OFFで違いを体験する

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

## CJG21: 友達に見せる

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

## CJG22: 友達のフィードバックを反映する

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

## CJG43: 実公開で遊ばれた記録が見える

```gherkin
Scenario: 親が実公開のアクセスログで遊ばれているか確認できる
  Given ゲームURLを友達に共有した
  When 友達が実公開URLからゲームを開く
  And 親がアクセスログを確認する
  Then 日別・ページ別のアクセス数が見える
  And 遊ばれていれば嬉しくてモチベーションが上がる
  And 遊ばれていなければ「やってみた？」と声をかけるきっかけになる
```

```gherkin
Scenario: 公開サーバがログAPIを持たないなら見逃さない
  Given 実公開URLが静的ファイルだけを配信している
  When play.html が /internal/play-sessions へ送信する
  Then 公開環境の確認で未対応が検知できる
  And 「ログ機能はdoneだが実公開では記録されない」状態を見逃さない
```

---

## CJG23: スプライトを自分で描く

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

## CJG25: 親子で役割を交代する

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

## CJG26: 「自分たちのゲーム」と言えるようになる

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

## CJG31: 子どもが変更を承認する

```gherkin
Scenario: 親がAIに頼んだ変更はまずおためし版に入る
  Given 親がAIに変更を頼んだ
  When おためし版（pyxel-preview.html）をビルドする
  Then 新しい変更はおためし版に反映される
  And もとのまま版（pyxel.html）は直前までに通った内容を保つ
```

```gherkin
Scenario: 前の依頼の preview を今の依頼のおためし版として見せない
  Given 前の依頼で作った preview artifact が残っている
  And 今の依頼に対応する preview source がない
  When 選択ページを生成する
  Then 前の preview をそのまま今の依頼の「おためしばん」として表示しない
  And 今の依頼に対応する preview をまだ作っていないなら「おためしばん」カード自体を出さない
```

```gherkin
Scenario: 「おためしばん」で変更後を体験できる
  Given 選択ページに「おためしばん」と「もとのままばん」が表示されている
  When 子どもが「おためしばん」の「あそんでみる」を押す
  Then 変更が反映されたゲームが始まる
```

```gherkin
Scenario: 「もとのままばん」で変更前を体験できる
  Given 選択ページに「おためしばん」と「もとのままばん」が表示されている
  When 子どもが「もとのままばん」の「あそんでみる」を押す
  Then 変更前のゲームが始まる
```

```gherkin
Scenario: 親が昇格コマンドを実行したときだけ current が更新される
  Given 親がAIに変更を頼んでおためし版を build した
  And 子どもが遊び比べて「おためしばんがいい」と決めた
  When 親が `python tools/build_web_release.py --approve-preview` を実行する
  Then main.py はおためし版の内容へ更新される
  And おためし版は取り下げられる
  And もとのまま版には承認後の内容が配信される
```

```gherkin
Scenario: 変更内容が子どもに理解できる
  Given 親がAIに変更を頼んだ
  When 選択ページに変更説明が表示される
  Then 変更内容がひらがなで「何が変わったか」表示される
  And コードの差分ではなくゲーム内の変化として説明される
  And 説明はおためし版に入った変更から自動生成される
```

```gherkin
Scenario: 選択ページの変更説明が実際の配信内容と一致する
  Given 親がAIに変更を頼んでおためし版を build した
  When 子どもが選択ページの変更説明を読む
  Then 説明は実際におためし版へ build された内容と一致している
  And 親が手で書いた古い説明が残ったまま比較させない
```

---

## CJG32: 子どもが変更を却下する

```gherkin
Scenario: 遊び比べた後に却下するともとのまま版が維持される
  Given 子どもが両方のバージョンで遊んだ
  When 子どもが「もとのままがいい！」と親に伝える
  And 親が `python tools/build_web_release.py --reject-preview` を実行する
  Then main.py は変わらない
  And おためし版が削除され、変更前の状態が維持される
```

```gherkin
Scenario: 却下後に別の案を試せる
  Given 子どもがおためし版を却下した
  When 親がAIに別の案を頼む
  And 新しいmain_preview.pyでビルドする
  Then 選択ページに新しいおためし版が表示される
  And 子どもが改めて遊び比べて判断できる
```

```gherkin
Scenario: 却下したおためし版は自動で current にしない
  Given 子どもが前のおためし版を却下した
  And main.py は却下前の current のままである
  When 親が次の変更を頼んで新しいおためし版を build する
  Then 却下した preview を current へ繰り上げない
  And 次の依頼はその current から新しいおためし版を作る
```

---

## CJG33: 子どもが変更を選んで適用する

```gherkin
Scenario: おためし版に含まれる変更一覧が表示される
  Given 親がAIに複数の変更を頼んでおためし版を build した
  When 選択ページが表示される
  Then おためしばんカードにおためし版へ入った変更リストがひらがなで列挙される
  And 子どもが「ここを変えたから、遊んでみて」と一覧で理解できる
```

```gherkin
Scenario: 変更一覧はおためし版から自動生成される
  Given 親がAIに複数の変更を頼んだ
  When おためし版を build する
  Then 選択ページの変更一覧はおためし版に入った変更から自動生成される
  And 親が別に change list を手で書かなくてもよい
```

```gherkin
Scenario: 変更一覧は今の依頼に対応するおためし版だけを説明する
  Given 古い preview artifact が残っている
  And いま有効な main_preview.py または preview_meta.json がない
  When 選択ページを表示する
  Then 古い preview の変更一覧を現在の説明として表示しない
  And いま有効なおためし版がないなら一覧も出さない
```

```gherkin
Scenario: 新しいおためし版を作り直したら一覧もその候補だけを説明する
  Given 以前のおためし版とは別の変更で新しい main_preview.py を作った
  When 親が新しいおためし版を build する
  Then 変更一覧は現在の main_preview.py の差分だけを説明する
  And 子どもが「今回どこを変えたか」だけを読める
```

```gherkin
Scenario: 変更一覧が実際のおためし版とずれるなら build で検知できる
  Given 選択ページの説明と実際のおためし版の内容がずれている
  When 親がおためし版を build する
  Then build または関連テストで不整合が検知される
  And 実際とずれた説明のまま子どもに届けない
```

```gherkin
Scenario: 変更を段階的に入れたい場合は複数回のビルドで対応する
  Given 親がAIに3つの変更を頼みたい
  When 親が1つ目の変更だけでおためし版をビルドする
  And 子どもが承認したあと親が `python tools/build_web_release.py --approve-preview` を実行する
  And 次に2つ目の変更でおためし版をビルドする
  Then 各変更が1つずつ遊び比べて判断される
```

---

## CJG34: 承認したあとに「やっぱり」となる

```gherkin
Scenario: 承認済みの変更を巻き戻せる
  Given 子どもがおためし版を承認してしばらく遊んだ
  When 子どもが「やっぱり前のほうがよかった」と親に伝える
  And 親がAIに「元に戻して」と頼み、新しいおためし版をビルドする
  Then 選択ページに「もとにもどす版」と「いまの版」が表示される
  And 子どもが遊び比べて判断できる
```

```gherkin
Scenario: 巻き戻しも通常の遊び比べフローを通る
  Given 選択ページに巻き戻し版が表示されている
  When 子どもが両方のバージョンで遊ぶ
  Then 通常の承認と同じように遊び比べて判断できる
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
