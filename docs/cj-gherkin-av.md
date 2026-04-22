# カスタマージャーニーgherkin: AV（BGM・SFX・VFX）

- 対象カスタマージャーニー: CJ15-CJ19, CJ24
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- 中心テーマ: BGM, SFX, VFX, 場面転換, Code Maker での音づくり
- 読み方: `Feature` は何を約束するか, `Rule` は何を壊してはいけないか, `Scenario` は画面や動作でどう確かめるか
- 実装状況の読み方: `実装済み` は現行コードとテストで確認できる, `部分実装` はコアはあるが文中の約束を全部は満たしていない, `未実装` は目標, `時間目標` は現状の目標値であり自動保証ではない

---

## CJG15: フィールドBGMをゾーンごとに付ける

この `CJG15` では、「場所が変わると音の雰囲気も変わり、その場所らしさがすぐ伝わる」を約束する。

実装状況:
- `部分実装`: 現行コードの BGM 切り替えは `title / town / overworld / dungeon / battle / boss / victory / ending` の8シーン単位
- `未実装`: ゾーン0-3がそれぞれ別曲を持つ構成にはまだなっていない
- `未実装`: Code Maker の Music エディタで作った曲を selector から戻しても、runtime は `AudioManager` の固定 track を優先してしまう

```gherkin
Feature: CJG15 フィールドBGMをゾーンごとに付ける
  子どもが場所ごとの雰囲気の違いを感じるには
  ゾーンごとに違うBGMがあり
  移動した瞬間に切り替わらなければならない
```

```gherkin
Rule: ゾーンが変わったらその場所のBGMに切り替わる
  場所が変わっても音が同じだと、世界の違いが伝わらない

  Scenario: ゾーンが変わるとBGMが切り替わる
    Given town / overworld / dungeon のBGMシーンが設定されている
    When キャラが町からフィールド、またはフィールドからダンジョンへ移動する
    Then その場面に対応したBGMへ切り替わる
```

```gherkin
Rule: 各ゾーンには固有の音の個性がある
  どこへ行っても同じ曲調だと、場所ごとの印象が弱くなる

  Scenario: 各ゾーンに固有のBGMが設定されている
    Given すべてのゾーン（0-3）にBGMが割り当てられている
    Then 各ゾーンのBGMが異なる曲調である
    And BGMデータがPyxelのMusic形式で定義されている
```

```gherkin
Rule: 曲の原案は人が Code Maker で作り、取り込み後は本編で鳴る
  音の中身まで AI / Codex が代わりに直す前提にすると、子どもの編集面が消える。逆に取り込み後も固定曲で上書きすると、Code Maker で作った意味がなくなる

  Scenario: 人が Musicエディタで編集した曲をその場面で聞ける
    Given 人が Code Maker の Music エディタでBGMを編集した
    When selector から code-maker.zip を取り込み
    And その曲が割り当てられた場面へ移動する
    Then 編集した曲がその場面で再生される
    And `AudioManager` は固定メロディで上書きしない
    And AI / Codex は音の中身を手打ちで置き換えず、import / build を担当する
```

---

## CJG16: 戦闘BGMを付ける

この `CJG16` では、「戦闘に入った瞬間に緊張感が上がり、終わったら元の冒険へ戻る」を約束する。

実装状況:
- `部分実装`: `choose_bgm_scene()` と scene 切り替えはある
- `未実装`: Code Maker で作った戦闘曲 / ボス曲が selector import 後の本編でそのまま鳴る保証はまだない

```gherkin
Feature: CJG16 戦闘BGMを付ける
  子どもが戦闘の始まりと終わりを音で感じるには
  戦闘開始で曲が切り替わり
  終了後は元のフィールドBGMへ戻らなければならない
```

```gherkin
Rule: 戦闘開始で戦闘曲に切り替わる
  戦闘に入っても音が変わらないと、場面の切り替わりが弱い

  Scenario: 戦闘開始時にBGMが戦闘曲に切り替わる
    Given フィールドBGMが再生中であり、戦闘曲が import 済みの audio asset にある
    When エンカウントが発生して戦闘画面に遷移する
    Then BGMが戦闘BGMに切り替わる
```

```gherkin
Rule: 戦闘終了後はその場所の曲へ戻る
  戦闘後も戦闘曲のままだと、元の場所へ戻った感じがなくなる

  Scenario: 戦闘終了後にフィールドBGMに戻る
    Given 戦闘BGMが再生中であり、復帰先のフィールド曲も import 済みの audio asset にある
    When 戦闘に勝利してフィールドに戻る
    Then BGMがフィールドの該当ゾーンBGMに復帰する
```

---

## CJG17: 効果音をイベントに紐づける

この `CJG17` では、「行動ごとに音が鳴って、何が起きたか耳でも分かる」を約束する。

実装状況:
- `実装済み`: 攻撃、回復、レベルアップなどの主要 SFX は現行コードにある
- `未実装`: 方針文から SFX データを自動生成する体験は製品機能としてはない
- `未実装`: Code Maker の Sound エディタで作った SFX を selector import 後の本編へ戻す流れはまだ弱い

```gherkin
Feature: CJG17 効果音をイベントに紐づける
  子どもが行動の結果を耳でも感じるには
  攻撃、回復、成長などの出来事に
  それぞれ対応した効果音が結びついていなければならない
```

```gherkin
Rule: バトルや成長の大事な瞬間で音が鳴る
  行動しても無音だと、手応えが弱くなる

  Scenario: 攻撃時にSFXが再生される
    Given 攻撃アクションにSFXが設定されている
    When 戦闘中に攻撃コマンドを選択する
    Then 攻撃SFXが再生される

  Scenario: 回復時にSFXが再生される
    Given 回復アクションにSFXが設定されている
    When 戦闘中に回復呪文を使用する
    Then 回復SFXが再生される

  Scenario: レベルアップ時にSFXが再生される
    Given レベルアップイベントにSFXが設定されている
    When 戦闘勝利後にレベルアップ条件を満たす
    Then レベルアップSFXが再生される
```

```gherkin
Rule: 効果音の原案は人が Soundエディタで作り、取り込み後はイベントで鳴る
  AI / Codex が中身を直接直す前提にせず、人が聞きながら育てられなければならない

  Scenario: 人が作ったSFXを行動イベントに結びつけられる
    Given 人が Code Maker の Sound エディタで攻撃用SFXを編集した
    When selector から code-maker.zip を取り込み
    And ゲーム内で攻撃する
    Then 編集したSFXが攻撃イベントで再生される
    And `SfxSystem` は固定 SFX 定義で上書きしない
    And AI / Codex は音の中身を直接書き換えず、import / build を担当する
```

---

## CJG24: 効果音を自分で作る

この `CJG24` では、「子どもが音を自分で作って、そのままゲームの中で鳴らせる」を約束する。

実装状況:
- `部分実装`: `.pyxres` を Code Maker で編集し、zip として戻す導線はある
- `未実装`: runtime は `SfxSystem` の固定定義で Sound エディタの結果を上書きしてしまう
- `未実装`: Code Maker 用 zip の audio import と本編一致を固定する E2E がまだない

```gherkin
Feature: CJG24 効果音を自分で作る
  子どもが音も自分の作品だと感じるには
  Soundエディタで試しながら作れて
  作った音がそのままゲームで鳴らなければならない
```

```gherkin
Rule: 作った音をその場で試せる
  聞きながら直せないと、子どもが音づくりを楽しめない

  Scenario: Code MakerのSoundエディタでSFXを編集できる
    Given Code Maker の Sound タブが開いている
    When 子どもがマウスで音程を描く
    And 再生ボタンで試聴する
    Then 編集した音が即座に聞ける
```

```gherkin
Rule: エディタで作った音がゲーム本編で鳴る
  エディタで聞いた音とゲームで鳴る音が違ってはいけない

  Scenario: Soundエディタで編集したSFXがゲーム内で使われる
    Given Sound エディタで攻撃用SFXを編集した
    When selector から code-maker.zip を取り込み
    And ゲーム内で攻撃する
    Then 編集したSFXが戦闘中に再生される
    And 固定のコード定義で別音へ戻らない
```

---

## CJG18: ダメージ演出を付ける

この `CJG18` では、「攻撃した時も、攻撃された時も、画面の光で手応えが伝わる」を約束する。

実装状況:
- `実装済み`: 白フラッシュと赤フラッシュは `VFX_FLASH` とテストで確認できる
- `部分実装`: パフォーマンス目標はまだ自動計測していない

```gherkin
Feature: CJG18 ダメージ演出を付ける
  子どもがダメージの重みを感じるには
  与えた時と受けた時の違いが光で伝わり
  しかもゲームが重くなりすぎてはいけない
```

```gherkin
Rule: 与えたダメージと受けたダメージで見分けられる
  どちらも同じ見え方だと、何が起きたか伝わりにくい

  Scenario: 敵にダメージを与えたとき画面フラッシュが発生する
    Given ダメージVFXが実装されている
    When 戦闘中に敵にダメージを与える
    Then 画面が一瞬白くフラッシュする

  Scenario: プレイヤーがダメージを受けたとき画面が赤く光る
    Given 被ダメージVFXが実装されている
    When 戦闘中にプレイヤーがダメージを受ける
    Then 画面が一瞬赤くフラッシュする
```

```gherkin
Rule: 演出は気持ちよさを足しても、操作を壊さない
  派手でも重すぎる演出は、遊びやすさを壊してしまう

  Scenario: VFXがゲームの動作を妨げない
    Given VFXが有効な状態でゲームを実行する
    When 戦闘中にダメージを与える/受ける
    Then VFX表示後にゲームが正常に続行する
    And フレームレートが著しく低下しない
```

---

## CJG19: 場面転換の演出

この `CJG19` では、「町に入る時や戦闘に入る時に、画面の切り替わりがなめらかに伝わる」を約束する。

実装状況:
- `未実装`: 現在のゲーム本編には町突入や戦闘開始のフェード演出はない
- `未実装`: フェード中の入力ロックもまだない

```gherkin
Feature: CJG19 場面転換の演出
  子どもが場面の切り替わりを自然に感じるには
  画面がなめらかに切り替わり
  切り替え中は操作が暴れないように止まらなければならない
```

```gherkin
Rule: 画面遷移はフェードでつながる
  いきなり切り替わるだけだと、場面転換の気持ちよさが弱くなる

  Scenario: 町に入るときフェードアウト/フェードインする
    Given フェード演出が実装されている
    When キャラが町のタイルに乗る
    Then 画面がフェードアウトする
    And 町の画面が表示される
    And 画面がフェードインする

  Scenario: 戦闘開始時にフェード演出が入る
    Given フェード演出が実装されている
    When エンカウントが発生する
    Then フィールド画面がフェードアウトする
    And 戦闘画面がフェードインする
```

```gherkin
Rule: フェード中は操作を止める
  切り替え中に動けると、画面遷移の途中で状態が乱れる

  Scenario: フェード演出中に操作を受け付けない
    Given フェード演出中である
    When プレイヤーがキー入力する
    Then 操作は無視される
    And フェード完了後に操作が有効になる
```

---

## 共通条件

この共通条件では、「音や光の演出があっても、音の実体は人が Code Maker で扱い、演出を切ってもゲームは壊れない」を約束する。

実装状況:
- `部分実装`: BGM/SFX のフォールバックデータはコードにある
- `未実装`: Code Maker で作った `Sound / Music` を code 側 audio asset へ取り込み、runtime truth にする流れはまだない
- `実装済み`: タイトル画面とゲーム内メニューの `せってい` から `ぜんぶ` で BGM/SFX/VFX をまとめて ON/OFF できる
- `実装済み`: BGM/SFX/VFX を個別にも ON/OFF できる
- `未実装`: `AudioManager` / `SfxSystem` が imported audio を上書きしないことを build / E2E で固定する仕組みはまだ薄い

```gherkin
Feature: 共通条件 AV
  音と光の演出を子どもが安心して触るには
  データの置き場所が単純で
  演出がなくてもゲーム本体が止まってはいけない
```

```gherkin
Rule: 音の原案は人が Code Maker で作り、runtime は取り込み済み audio asset を使う
  音の中身を AI / Codex が直接いじる前提にすると、子どもの編集面がぼやける。逆に runtime が固定音へ戻すと、Code Maker 側の編集面が真実でなくなる

  Scenario: BGM / SFX は Code Maker で編集し、取り込み後は本編の audio asset になる
    Given Code Maker 用 zip を開く
    And 人が Sound / Music エディタで編集する
    When selector から code-maker.zip を取り込む
    Then BGM / SFX の内容は code 側の audio asset として本編へ反映される
    And AI / Codex はその音の中身を手編集しない
```

```gherkin
Rule: 演出がなくても本編は遊べる
  音や光は気持ちよさを足す役目であり、ないだけで壊れてはいけない

  Scenario: 演出が無効でもゲームが正常に動作する
    Given BGM/SFX/VFXのいずれかが未設定または無効な状態
    When Run する
    Then ゲーム本編（移動・戦闘・セーブ等）が正常に動作する
    And エラーが発生しない
```
