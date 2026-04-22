# カスタマージャーニーgherkin: Platform（配信・Code Maker制約・体験設計）

- 対象カスタマージャーニー: CJ12, CJ20-CJ23, CJ25-CJ26, CJ31-CJ34, CJ43
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- 中心テーマ: 配信, Code Maker制約, 承認フロー, 子どもに見える体験
- 読み方: `Feature` は何を約束するか, `Rule` は何を壊してはいけないか, `Scenario` は画面や動作でどう確かめるか
- 実装状況の読み方: `実装済み` は現行コードとテストで確認できる, `部分実装` はコアはあるが文中の約束を全部は満たしていない, `未実装` は目標, `時間目標` は現状の目標値であり自動保証ではない

---

## CJG12: 歩いたら壁にハマった

この `CJG12` では、「バグを見つけても親子の流れが止まらず、すぐ直して安全に試し直せる」を約束する。

実装状況:
- `部分実装`: pytest と Code Maker 用ビルド、開発版ビルドの流れはある
- `時間目標`: `5分以内` は UX 目標であり、自動保証ではない

```gherkin
Feature: CJG12 歩いたら壁にハマった
  子どもがバグを見つけたときも
  親子の流れが止まらず
  すぐ直して安全に試し直せなければならない
```

```gherkin
Rule: 直すまでが長すぎない
  バグを見つけてから試し直すまでが長すぎると、子どもの集中が切れてしまう

  Scenario: バグ報告からAI修正→再テストが5分以内で回る
    Given 子どもがテストプレイ中にバグを発見した
    When 親がAIにバグの状況を伝える
    And AIが修正コードを生成する
    And Code Makerでコードを更新してRunする
    Then バグが修正されている
    And 報告から確認まで5分以内で完了する
```

```gherkin
Rule: 直したつもりで別の場所を壊さない
  1つ直して別の場所が壊れると、子どもは安心して試せない

  Scenario: AI修正が既存機能を壊さない
    Given AIがバグ修正コードを生成した
    When 修正後のコードでRunする
    Then バグが修正されている
    And 移動・戦闘・セーブなどの既存機能が正常に動作する
```

---

## CJG20: 演出ON/OFFで違いを体験する

この `CJG20` では、「演出を切っても遊べるし、戻せば違いがすぐ分かる」を約束する。

実装状況:
- `実装済み`: タイトル画面とゲーム内メニューに `せってい` があり、`ぜんぶ` で BGM/SFX/VFX をまとめて ON/OFF できる
- `実装済み`: BGM/SFX/VFX を個別にも ON/OFF でき、切り替えはその場で反映される

```gherkin
Feature: CJG20 演出ON/OFFで違いを体験する
  子どもが演出の価値を体で感じるには
  演出を切っても遊べて
  戻したときの違いがすぐ伝わらなければならない
```

```gherkin
Rule: 演出を切ってもゲーム本体は止まらない
  演出比較のために遊べなくなってはいけない

  Scenario: 演出をOFFにしてもゲームが正常に動作する
    Given BGM/SFX/VFXがすべて有効な状態
    When 演出を無効にしてRunする
    Then ゲーム本編が正常に動作する
    And 無音・演出なしでプレイできる
```

```gherkin
Rule: 演出を戻したら違いがその場で分かる
  切り替えたのに反映が遅いと比較にならない

  Scenario: 演出をONに戻すと即座に反映される
    Given 演出が無効な状態でプレイ中
    When 演出を有効に切り替える
    Then BGM/SFX/VFXが即座に有効になる
```

---

## CJG21: 友達に見せる

この `CJG21` では、「URLを送ったら友達がすぐ遊べて、すぐ感想を返せる」を約束する。

実装状況:
- `部分実装`: `index.html -> production/play.html -> production/pyxel.html` の共有導線、スマホ全画面ボタン、インストール不要のWeb配信はある
- `時間目標`: `10秒以内` は現状の目標値であり、自動計測はしていない

```gherkin
Feature: CJG21 友達に見せる
  親子の外から感想をもらうには
  URLを開くだけで遊べて
  スマホでもすぐ始められなければならない
```

```gherkin
Rule: URLだけで遊べる
  インストールや登録が必要だと、その場で見てもらえない

  Scenario: URLでブラウザからゲームをプレイできる
    Given ゲームがWebビルドされてURLが発行されている
    When 友達がスマホまたはPCのブラウザでURLを開く
    Then ゲームが読み込まれプレイ可能な状態になる
    And インストールやダウンロードが不要である
    And 会員登録やログインが不要である
```

```gherkin
Rule: スマホでも見せやすい
  友達がスマホで遊びにくいと共有の広がりが止まる

  Scenario: スマホで全画面プレイできる
    Given スマホのブラウザでゲームURLを開いた
    When 全画面ボタンをタップする
    Then ゲームが全画面で表示される
    And タッチ操作でプレイできる
```

```gherkin
Rule: 開いたあとすぐ感想が返せる
  長く待たせると、その場の会話が止まってしまう

  Scenario: スマホで即プレイできることでフィードバックがもらいやすくなる
    Given 子どもが友達にゲームのURLをLINE等で送った
    When 友達がスマホでURLを開く
    Then 10秒以内にゲームがプレイ可能になる
    And 友達が「ここ難しい」「ここ面白い」等のフィードバックをその場で返せる
    And フィードバックの出し手が親子の外にまで広がる
```

---

## CJG22: 友達のフィードバックを反映する

この `CJG22` では、「感想をもらったら、その場で直して、また見てもらえる」を約束する。

実装状況:
- `部分実装`: 開発版ビルドと再共有の導線はある
- `時間目標`: 「数分で完了」は目標値であり、自動保証ではない

```gherkin
Feature: CJG22 友達のフィードバックを反映する
  友達の感想がその場の会話で終わらないように
  すぐ直して
  すぐもう一度見せられなければならない
```

```gherkin
Rule: 1回の感想をその場で修正版へつなげられる
  感想から修正版までが長いと、会話の熱が消えてしまう

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
Rule: 1回で終わらず何回も回せる
  その場で2回目の感想まで出ると、外部フィードバックが習慣になる

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

この `CJG43` では、「実際に遊ばれたかを親が見て、次の行動につなげられる」を約束する。

実装状況:
- `部分実装`: `production/play.html` / `development/play.html` から `/internal/play-sessions` へ送る仕組みと SQLite 集計はある
- `部分実装`: 実公開で本当に記録されるかは、実際にその公開環境が `tools/web_runtime_server.py` 相当で動いているかに依存する

```gherkin
Feature: CJG43 実公開で遊ばれた記録が見える
  実際に届いているかを親が判断するには
  公開URLで遊ばれた記録が見えて
  もし記録できていないなら見逃さずに気づけなければならない
```

```gherkin
Rule: 実公開のアクセスが見える
  本当に遊ばれたか分からないと、共有の次の動きが決められない

  Scenario: 親が実公開のアクセスログで遊ばれているか確認できる
    Given ゲームURLを友達に共有した
    When 友達が実公開URLからゲームを開く
    And 親がアクセスログを確認する
    Then 日別・ページ別のアクセス数が見える
    And 遊ばれていれば嬉しくてモチベーションが上がる
    And 遊ばれていなければ「やってみた？」と声をかけるきっかけになる
```

```gherkin
Rule: 記録できていない状態を done 扱いしない
  ログ機能があるつもりでも公開環境で動かなければ意味がない

  Scenario: 公開サーバがログAPIを持たないなら見逃さない
    Given 実公開URLが静的ファイルだけを配信している
    When production/play.html または development/play.html が /internal/play-sessions へ送信する
    Then 公開環境の確認で未対応が検知できる
    And 「ログ機能はdoneだが実公開では記録されない」状態を見逃さない
```

---

## CJG23: スプライトを自分で描く

この `CJG23` では、「見た目は自分で変えられて、ゲームの中身は勝手に変わらない」を約束する。

実装状況:
- `部分実装`: `.pyxres` を Code Maker で編集してゲームで読む設計はある
- `部分実装`: 「ロジックに影響しない」は設計意図としてはそうだが、全編集ケースを自動テストしてはいない

```gherkin
Feature: CJG23 スプライトを自分で描く
  子どもが自分のキャラだと感じるには
  見た目を自分で描けて
  見た目の編集でゲームの中身まで勝手に変わってはいけない
```

```gherkin
Rule: 人が描いた見た目がそのまま出る
  見た目の中身まで AI / Codex が代わりに触る前提にすると、「自分で描いた」感が消える

  Scenario: Code MakerのSpriteエディタでキャラを編集できる
    Given Code Maker の Sprite タブが開いている
    When 子どもがピクセルを描き替える
    And Run する
    Then ゲーム内のキャラが変更後のスプライトで表示される
    And AI / Codex は `.pyxres` の実体を直接編集しない
```

```gherkin
Rule: 見た目だけを変えて、ルールは変えない
  見た目の編集で性能まで変わると、子どもが何を変えたか分からなくなる

  Scenario: スプライト編集がゲームロジックに影響しない
    Given スプライトの見た目を変更した
    When Run する
    Then キャラの移動速度・当たり判定・ステータスは変わらない
```

---

## CJG25: 親子で役割を交代する

この `CJG25` では、「役割は入れ替わっても、何を決めるかのハンドルは子どもが持ち続ける」を約束する。

実装状況:
- `未実装`: これは主に体験設計の約束であり、現在のコードが強制する仕組みではない

```gherkin
Feature: CJG25 親子で役割を交代する
  親子が対等な仲間でいるには
  役割は交代できても
  何を直すかを決めるハンドルは子どもが持ち続けなければならない
```

```gherkin
Rule: 何を直すかは子どもが決める
  親が全部決めると、子どもはまた見ているだけに戻ってしまう

  Scenario: 何を直すかの判断は子どもが行う
    Given 友達がスマホでプレイして複数のフィードバックを出した
    When 親が子どもにフィードバックを伝える
    Then 子どもが「どれを直すか」「どの順で直すか」を決める
    And 親は子どもの判断に基づいてAIに修正を依頼する
```

```gherkin
Rule: 編集操作は誰に渡しても続けられる
  親だけしか触れないと、役割交代が成立しない

  Scenario: Tilemapエディタは誰でも操作できる
    Given Tilemap タブが開いている
    When 親がタイルを配置する
    And 子どもに操作を渡す
    And 子どもがタイルを配置する
    Then 両者の変更がどちらも正しくマップに反映される
    And 特別な権限や設定の切り替えが不要である
```

```gherkin
Rule: テストプレイも誰でもすぐ始められる
  テスト役に回った子どもがすぐ遊べないと、対等な役割交代にならない

  Scenario: テストプレイは誰でもすぐにできる
    Given Run してゲームが起動している
    When 子どもがキャラを操作してテストプレイする
    Then 特別な知識なしにゲームを遊べる
    And フィードバック（「ここ変」「ここ面白い」）を口頭で伝えられる
```

---

## CJG26: 「自分たちのゲーム」と言えるようになる

この `CJG26` では、`Feature` が全体価値、`Rule` が体験契約、`Scenario` が確認条件を兼ねる。

実装状況:
- `実装済み`: 開発版カードから `development/code-maker.zip` を落とす導線、Code Maker 外部リンク、`STUDENT AREA` ガード付き教材版は現行 build にある
- `実装済み`: selector から Code Maker で保存した `code-maker.zip` を取り込み、その browser で次に開く play に `my_resource.pyxres` を反映できる
- `実装済み`: selector は static host でも `code-maker.zip` をこの browser に保存でき、次に開く play が人の resource を使える
- `部分実装`: 保存と持ち出しの導線はあるが、環境ごとの差は残る
- `部分実装`: `Editor で見えたもの = 実ゲーム` はまだ未達で、特に map / resource の一致は弱い
- `部分実装`: Code Maker 用 zip に入る `my_resource.pyxres` が常に今の開発版と一致する保証はまだ薄い
- `未実装`: `Sound / Music` は selector import 後も `AudioManager` / `SfxSystem` の固定データで上書きされ、Code Maker 側の編集結果が本編の真実になっていない

```gherkin
Feature: CJG26 「自分たちのゲーム」と言えるようになる
  子どもが「自分たちのゲーム」と感じるには
  見えている編集面がそのままゲーム世界の真実であり
  今見ている開発版をそのまま持ち出せて
  見える境界の中で安心して編集できなければならない
```

```gherkin
Rule: 編集した内容が続き、持ち出しても同じゲームとして扱える
  子どもが変えた内容は保存され、別の環境へ持ち出しても同じゲームとして動かなければならない

  Scenario: 改造した内容がセーブされ次回も維持される
    Given Tilemapやコードを変更してRunした
    When Code Makerでプロジェクトを保存する
    And ブラウザを閉じて再度開く
    Then 前回の変更内容が維持されている

  Scenario: Code Makerからダウンロードしたzipがローカルでも動く
    Given Code Maker でゲームを改造した
    When Save でzipをダウンロードする
    And ローカルのPyxel環境で実行する
    Then Code Makerと同じようにゲームが動作する
```

```gherkin
Rule: 編集面が真実である
  編集画面で見えているものと実際に遊ぶ結果がずれてはいけない

  Scenario: Tilemap / Resource Editor / Sprite / Sound で見えたものがそのままゲームに出る
    Given 子どもが Pyxel Code Maker の編集画面を見ている
    When 子どもが Tilemap / Resource Editor / Sprite / Sound を編集して Run する
    Then 編集画面で見えていた内容がそのままゲームに現れる
    And 子どもは Run 前に結果を自分で予想できる

  Scenario: 実行時だけの見た目補正で別の形に変えない
    Given 編集画面で道や地形の形が見えている
    When ゲームを Run する
    Then 実行時だけで曲がり角や分岐へ描き替えない
    And 編集画面では見えない接続ルールを足さない

  Scenario: Resource Editor で見えるマップは実際に遊ぶマップと一致する
    Given 親が index.html の 開発版カードから Code Maker 用 zip をダウンロードした
    And 親子が公式 Pyxel Code Maker でその zip を開いた
    When 子どもが Resource Editor で道や地形を編集して Run する
    Then Resource Editor で見えた配置とつながりのままゲーム内に現れる
    And 親の通訳なしで「ここをこう変えるとこうなる」と言える

  Scenario: 道が編集画面と実ゲームで別の見え方にならない
    Given Resource Editor 上の道が基底タイルとして見えている
    When ゲームを Run する
    Then 周囲を見て自動で別の道形状へ描き替えない
    And 編集画面では見えない道の意味を実行時だけで足さない
```

```gherkin
Rule: 持ち出した開発版は今見ている開発版そのものである
  選択ページから持ち出す zip とリンクは、その時点の開発版と一致していなければならない

  Scenario: 選択ページの開発版から Code Maker 用 zip を落とせる
    Given 親がAIに変更を頼んで開発版を build した
    When 親が index.html の 開発版カードを見る
    Then 開発版の Code Maker 用 zip ダウンロード導線が表示される
    And その zip には開発版の main.py と .pyxres が入っている

  Scenario: 選択ページの開発版から落とす Code Maker 用 zip は今の開発版と一致する
    Given 親がAIに変更を頼んで開発版を build した
    When 親が index.html の 開発版カードから Code Maker 用 zip をダウンロードする
    Then その zip はその時点の開発版内容を反映している
    And 古い開発版 zip を現在の候補として見せない

  Scenario: 選択ページから落とした開発版 zip を Code Maker で開いてリソースを編集できる
    Given 親が index.html の 開発版カードから Code Maker 用 zip をダウンロードした
    When 親が公式 Pyxel Code Maker でその zip を開く
    Then main.py と .pyxres が読み込まれる
    And 子どもはリソースファイルを編集して Run できる

  Scenario: 選択ページの開発版から公式 Pyxel Code Maker を開ける
    Given 親がAIに変更を頼んで開発版を build した
    When 親が index.html の 開発版カードを見る
    Then 公式 Pyxel Code Maker を開くリンクが表示される
    And 親は zip を落としたあと迷わず Code Maker を開ける

  Scenario: 開発版がない時は開発版の Code Maker zip 導線を出さない
    Given いま有効な main_development.py または開発版配信物がない
    When 親が index.html を開く
    Then 開発版の Code Maker 用 zip ダウンロード導線は表示されない
    And 古い開発版 zip を現在の候補として見せない

  Scenario: 開発版がない時は Pyxel Code Maker 外部リンクも出さない
    Given いま有効な main_development.py または開発版配信物がない
    When 親が index.html を開く
    Then 公式 Pyxel Code Maker を開くリンクは表示されない
    And 開発版がないのに外部リンクだけを孤立して見せない
```

```gherkin
Rule: Code Maker から戻す時は code を巻き戻さず必要な asset を取り込む
  Code Maker の zip から code まで戻すと、子どもが見ていた今の候補と AI 修正の境界が崩れる。逆に音を取り込まず固定データで上書きすると、Code Maker で触った意味が消える

  Scenario: selector から Code Maker の zip を取り込める
    Given 親子が Code Maker で見た目や音を編集して Save した
    When 親が selector から code-maker.zip を取り込む
    Then 画像系は `my_resource.pyxres` としてその browser の次回 play へ反映される
    And `Sound / Music` は development 候補の code 側 audio asset として反映される
    And 次に開く `production/play.html` または `development/play.html` は取り込み後 asset を使う

  Scenario: static な selector でも Code Maker の zip を取り込める
    Given 親が static host の index.html を開いている
    When 親が selector から code-maker.zip を取り込む
    Then その browser に zip が保存される
    And 次に開く `production/play.html` または `development/play.html` は取り込み後 asset を使う

  Scenario: Code Maker zip に入っている main.py は取り込まない
    Given Code Maker が `main.py` と `my_resource.pyxres` を含む zip を保存した
    When 親がその zip を selector から取り込む
    Then 現在の `main.py` または `main_development.py` はそのまま維持される
    And zip 内の `main.py` は development 候補の code source として採用されない

```

```gherkin
Rule: 見た目や音の原案は人が Code Maker で修正する
  見た目や音まで AI / Codex が代わりに直す前提にすると、子どもの編集面が消えてしまう

  Scenario: 見た目や音の authoring の主体は人である
    Given 子どもが Code Maker の Sprite / Sound / Music / Tilemap / Resource Editor を使っている
    When 親子が見た目や音を編集する
    Then 原案の変更は人の手で行われる
    And AI / Codex は `.pyxres` を手で編集する代わりに import / build / verify を担当する

  Scenario: 見た目や音の変更をAIに頼んだら Code Maker へ案内する
    Given 親がAIに「敵の絵を変えて」「SEを変えて」と頼む
    When AIが返答する
    Then AIは Code Maker の該当エディタを案内する
    And 音の中身を自分で手打ちしようとせず、必要なら import 手順を案内する
```

```gherkin
Rule: 子どもに見える境界がある
  子どもが触る場所とコア領域の境界は見えていなければならない

  Scenario: Code Maker 教材版では編集可能領域が明示される
    Given 親が Code Maker 用 zip を build した
    When production/code-maker.zip 内の main.py を開く
    Then STUDENT AREA が表示される
    And 子どもが触る場所とゲーム本体の境界が分かる

  Scenario: 危ない場所を毎回親が口で説明しなくてもよい
    Given 子どもが教材版の main.py を見ている
    When 子どもがどこを触ればよいか確認する
    Then 子どもは自力で触ってよい範囲を指させる
    And 親が毎回コア領域の危なさを通訳しなくてよい
```

```gherkin
Rule: 親の通訳を前提にしない
  親は相談相手であって、見えない内部仕様の通訳係ではない

  Scenario: 子どもは見えない内部ルールを知らなくても編集結果を理解できる
    Given 子どもが編集画面を見ている
    When 子どもが変更前に「こうなるはず」と話す
    And Run して結果を見る
    Then 子どもは「思った通りだった」と言える

  Scenario: この画面は見た目だけで本当の挙動は別と言わなくてよい
    Given 子どもが Resource Editor や Tilemap を使っている
    When 親が説明なしで見守る
    Then 編集画面だけで結果を理解できる
    And 親が「実はゲーム中だけ別のルールがある」と補足しなくてよい
```

```gherkin
Rule: 失敗しても全部は壊しにくい
  子どもが許された範囲で試した失敗が、全部崩壊する事故になってはいけない

  Scenario: Code Maker 教材版で STUDENT AREA だけを編集しても起動できる
    Given Code Maker 用教材版の main.py に STUDENT AREA がある
    When 子どもが STUDENT AREA だけを編集して Run する
    Then コア自己検査は通る
    And 既存ゲームの起動フローは壊れない

  Scenario: コア領域を壊したときは起動前に案内して止まる
    Given 子どもが誤ってコア領域を壊した
    When ゲームを起動しようとする
    Then 起動前に案内して止まる
    And 何が危ないかが子どもにも分かる

  Scenario: 小さな編集ミスで理由も分からず全部が壊れない
    Given 子どもが小さな編集ミスをした
    When ゲームを起動する
    Then 理由も分からず全部が壊れる状態にしない
    And 親がエラーログ通訳だけで復旧する前提にしない
```

---

## CJG31: 子どもが変更を承認する

この `CJG31` では、「変更はまず開発版で比べ、子どもがよいと言ったときだけ本番へ入る」を約束する。

実装状況:
- `実装済み`: `--development` と `--approve-development` による開発版 / 本番フローはある
- `部分実装`: 子どもに説明が十分やさしいか、変更説明が十分自動化されているかはまだ改善余地がある

```gherkin
Feature: CJG31 子どもが変更を承認する
  子どもが自分で採否を決めるには
  変更はまず開発版に入り
  比べてよいと思ったときだけ本番へ上がらなければならない
```

```gherkin
Rule: 新しい変更はまず開発版に入る
  本番が先に変わると、子どもが比べて決める前に結果が確定してしまう

  Scenario: 親がAIに頼んだ変更はまず開発版に入る
    Given 親がAIに変更を頼んだ
    When 開発版（development/pyxel.html）をビルドする
    Then 新しい変更は開発版に反映される
    And 本番（production/pyxel.html）は直前までに通った内容を保つ

  Scenario: 前の依頼の開発版を今の依頼の開発版として見せない
    Given 前の依頼で作った開発版配信物が残っている
    And 今の依頼に対応する main_development.py がない
    When 選択ページを生成する
    Then 前の開発版をそのまま今の依頼の「開発版」として表示しない
    And 今の依頼に対応する開発版をまだ作っていないなら「開発版」カード自体を出さない
```

```gherkin
Rule: 子どもが遊び比べて決められる
  比べる前に決まってしまうと、承認フローが形だけになる

  Scenario: 「開発版」で変更後を体験できる
    Given 選択ページに「開発版」と「本番」が表示されている
    When 子どもが「開発版」の「あそんでみる」を押す
    Then 変更が反映されたゲームが始まる

  Scenario: 「本番」で変更前を体験できる
    Given 選択ページに「開発版」と「本番」が表示されている
    When 子どもが「本番」の「あそんでみる」を押す
    Then 変更前のゲームが始まる
```

```gherkin
Rule: 昇格は親の明示操作と子どもの承認がそろったときだけ起きる
  自動で本番に上がると、子どもの決定権が消えてしまう

  Scenario: 親が昇格コマンドを実行したときだけ本番が更新される
    Given 親がAIに変更を頼んで開発版を build した
    And 子どもが遊び比べて「開発版がいい」と決めた
    When 親が `python tools/build_web_release.py --approve-development` を実行する
    Then main.py は開発版の内容へ更新される
    And 開発版は取り下げられる
    And 本番には承認後の内容が配信される
```

```gherkin
Rule: 比べる前に変更内容が子どもに分かる
  説明が難しかったり古かったりすると、自分の判断で選べない

  Scenario: 変更内容が子どもに理解できる
    Given 親がAIに変更を頼んだ
    When 選択ページに変更説明が表示される
    Then 変更内容がひらがなで「何が変わったか」表示される
    And コードの差分ではなくゲーム内の変化として説明される
    And 説明は開発版に入った変更から自動生成される

  Scenario: 選択ページの変更説明が実際の配信内容と一致する
    Given 親がAIに変更を頼んで開発版を build した
    When 子どもが選択ページの変更説明を読む
    Then 説明は実際に開発版へ build された内容と一致している
    And 親が手で書いた古い説明が残ったまま比較させない
```

---

## CJG32: 子どもが変更を却下する

この `CJG32` では、「気に入らなければ止められて、別案をまた試せる」を約束する。

実装状況:
- `実装済み`: `--reject-development` により本番を保ったまま開発版を取り下げられる

```gherkin
Feature: CJG32 子どもが変更を却下する
  子どもが自分の体感でノーと言うには
  却下したとき本番が守られ
  そのあとも別案を試せなければならない
```

```gherkin
Rule: 却下したら本番はそのまま残る
  却下したのに本番が変わると、ノーと言う意味がなくなる

  Scenario: 遊び比べた後に却下すると本番が維持される
    Given 子どもが両方のバージョンで遊んだ
    When 子どもが「本番がいい！」と親に伝える
    And 親が `python tools/build_web_release.py --reject-development` を実行する
    Then main.py は変わらない
    And 開発版が削除され、変更前の状態が維持される
```

```gherkin
Rule: 却下しても次の案は試せる
  1回ノーと言ったら止まるのではなく、次の候補へ進めなければならない

  Scenario: 却下後に別の案を試せる
    Given 子どもが開発版を却下した
    When 親がAIに別の案を頼む
    And 新しいmain_development.pyでビルドする
    Then 選択ページに新しい開発版が表示される
    And 子どもが改めて遊び比べて判断できる
```

```gherkin
Rule: 却下した版はあとから勝手に本番へ上がらない
  前に断った版が勝手に戻ると、子どもの判断が壊れる

  Scenario: 却下した開発版は自動で本番にしない
    Given 子どもが前の開発版を却下した
    And main.py は却下前の本番のままである
    When 親が次の変更を頼んで新しい開発版を build する
    Then 却下した開発版を本番へ繰り上げない
    And 次の依頼はその本番から新しい開発版を作る
```

---

## CJG33: 子どもが変更を選んで適用する

この `CJG33` では、「何が変わるかを見て、どれを入れるかを子どもが選べる」を約束する。

実装状況:
- `部分実装`: 変更一覧は `development_meta.json` や `top_changes.json` を通じて表示される
- `未実装`: 実際の差分から完全自動で子ども向け説明文を生成する仕組みにはまだなっていない

```gherkin
Feature: CJG33 子どもが変更を選んで適用する
  子どもが何を入れるか選ぶには
  開発版の変更一覧が分かりやすく見えて
  その一覧が今の候補とずれていてはいけない
```

```gherkin
Rule: 開発版に何が入っているかが見える
  何を比べているか分からないと、順番も採否も決められない

  Scenario: 開発版に含まれる変更一覧が表示される
    Given 親がAIに複数の変更を頼んで開発版を build した
    When 選択ページが表示される
    Then 開発版カードに開発版へ入った変更リストがひらがなで列挙される
    And 子どもが「ここを変えたから、遊んでみて」と一覧で理解できる

  Scenario: 変更一覧は開発版から自動生成される
    Given 親がAIに複数の変更を頼んだ
    When 開発版を build する
    Then 選択ページの変更一覧は開発版に入った変更から自動生成される
    And 親が別に change list を手で書かなくてもよい
```

```gherkin
Rule: 一覧は今の候補だけを説明する
  古い候補の説明が混ざると、子どもは今どれを選んでいるのか分からなくなる

  Scenario: 変更一覧は今の依頼に対応する開発版だけを説明する
    Given 古い開発版配信物が残っている
    And いま有効な main_development.py または development_meta.json がない
    When 選択ページを表示する
    Then 古い開発版の変更一覧を現在の説明として表示しない
    And いま有効な開発版がないなら一覧も出さない

  Scenario: 新しい開発版を作り直したら一覧もその候補だけを説明する
    Given 以前の開発版とは別の変更で新しい main_development.py を作った
    When 親が新しい開発版を build する
    Then 変更一覧は現在の main_development.py の差分だけを説明する
    And 子どもが「今回どこを変えたか」だけを読める
```

```gherkin
Rule: 一覧が実物とずれていたら止める
  説明と実物がずれていたままでは、正しい選び方ができない

  Scenario: 変更一覧が実際の開発版とずれるなら build で検知できる
    Given 選択ページの説明と実際の開発版の内容がずれている
    When 親が開発版を build する
    Then build または関連テストで不整合が検知される
    And 実際とずれた説明のまま子どもに届けない
```

```gherkin
Rule: 変更は1つずつ入れて比べられる
  まとめて入れすぎると、どれが良かったのか子どもが決められない

  Scenario: 変更を段階的に入れたい場合は複数回のビルドで対応する
    Given 親がAIに3つの変更を頼みたい
    When 親が1つ目の変更だけで開発版をビルドする
    And 子どもが承認したあと親が `python tools/build_web_release.py --approve-development` を実行する
    And 次に2つ目の変更で開発版をビルドする
    Then 各変更が1つずつ遊び比べて判断される
```

---

## CJG34: 承認したあとに「やっぱり」となる

この `CJG34` では、「いったんOKしたあとでも、また比べて戻せる」を約束する。

実装状況:
- `部分実装`: 以前の本番内容を元に新しい開発版を作ることはできる
- `未実装`: 「もとにもどす版」という専用ラベルや巻き戻し専用 UI はない

```gherkin
Feature: CJG34 承認したあとに「やっぱり」となる
  子どもがあとから考え直せるように
  承認後でも巻き戻し候補を作れて
  いつもと同じ比べ方で選び直せなければならない
```

```gherkin
Rule: 承認後でも巻き戻し候補を作れる
  一度OKしたら永遠に固定だと、子どもは安心して選べない

  Scenario: 承認済みの変更を巻き戻せる
    Given 子どもが開発版を承認してしばらく遊んだ
    When 子どもが「やっぱり前のほうがよかった」と親に伝える
    And 親がAIに「元に戻して」と頼み、新しい開発版をビルドする
    Then 選択ページに「もとにもどす版」と「いまの版」が表示される
    And 子どもが遊び比べて判断できる
```

```gherkin
Rule: 巻き戻しも特別扱いせず、いつもの比べ方で選べる
  巻き戻しだけ難しい別フローだと、子どもが自分で選び直せない

  Scenario: 巻き戻しも通常の遊び比べフローを通る
    Given 選択ページに巻き戻し版が表示されている
    When 子どもが両方のバージョンで遊ぶ
    Then 通常の承認と同じように遊び比べて判断できる
```

---

## 共通条件（Code Maker制約）

この共通条件では、「どの `CJG` でも Code Maker で無理なく扱える」を約束する。

実装状況:
- `実装済み`: Code Maker 配布物は `main.py + my_resource.pyxres` の2ファイルにまとまる
- `部分実装`: Code Maker 上の構文エラー時 UX は Pyxel / ブラウザ側の挙動にも依存する
- `部分実装`: resource の中身そのものは人が Code Maker で編集する前提だが、その境界を E2E で完全固定はできていない

```gherkin
Feature: 共通条件 Code Maker制約
  どの体験も Code Maker で回せるように
  配布物が単純で
  アップロードしてすぐ動いて
  危ない依存やファイル書き込みを持ち込んではならない
```

```gherkin
Rule: 配布物は子どもにも扱いやすい最小構成である
  ファイルが増えすぎると、どれを触ればよいか分からなくなる

  Scenario: 配布物が2ファイルで構成される（C1）
    Given ゲームのすべてのコードとデータ
    Then 配布物は main.py と .pyxres の2ファイルのみで構成される
    And src/ や YAML への参照が存在しない
```

```gherkin
Rule: 見た目や音の原案は人が Code Maker で触る
  Codex がその境界を越えると、子ども向けの編集面が壊れる

  Scenario: `.pyxres` と audio import の元データ修正は人の作業として扱う
    Given Code Maker 用配布物に `.pyxres` が含まれている
    When 見た目や音の実体を変えたい
    Then 人が Code Maker で修正する
    And Codex は build / packaging / verify と import を担当する
```

```gherkin
Rule: アップロードしたらすぐ遊べる
  余計な準備が必要だと、子どもの編集体験が止まる

  Scenario: アップロード後に何も書き換えなくても遊べる（C3）
    Given Code Maker に main.py と .pyxres をアップロードした
    When 何も編集せずに Run する
    Then ゲームが正常に起動し遊べる

  Scenario: コードを1行変えると即座に変化が分かる（C4）
    Given Code Maker でゲームが動作している
    When コード内のデータ値（例: HPの数値）を1箇所変更する
    And Run する
    Then 変更した内容がゲーム内に反映されている
```

```gherkin
Rule: 失敗しても作業が続けられる
  小さな失敗で全部閉じるようでは、安心して試せない

  Scenario: エラーが出ても致命的に壊れない（C5）
    Given Code Maker でコードを編集中
    When 構文エラーを含むコードで Run する
    Then エラーメッセージがブラウザ内に表示される
    And セーブデータが失われない
    And ブラウザを閉じる必要がない
```

```gherkin
Rule: 余計な依存や危ない保存先を持ち込まない
  Code Maker でそのまま動かない作りは、子ども向けの体験を壊す

  Scenario: pip install不要で動作する（A3）
    Given main.py のimport文を確認する
    Then pyxel と Python標準ライブラリ以外のimportが存在しない

  Scenario: Code Maker / Web 実行ではローカルファイル書き込みに依存しない（A4）
    Given main.py のコード全体を確認する
    Then Code Maker / Web 実行時のセーブはブラウザのローカルストレージで永続化される
    And desktop 実行時のみ save.json への保存を使う
```
