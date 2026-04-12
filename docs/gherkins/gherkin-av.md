# Gherkin: AV（BGM・SFX・VFX）

- 対象ジャーニー: J11, J15-J19, J24
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- structure-design の中心: audio_system, chiptune_tracks, SFXトリガー, VFX描画

---

## J15: フィールドBGMをゾーンごとに付ける

```gherkin
Scenario: ゾーンが変わるとBGMが切り替わる
  Given ゾーン0に草原BGM、ゾーン1に森BGMが設定されている
  When キャラがゾーン0からゾーン1に移動する
  Then BGMが草原BGMから森BGMに切り替わる
```

```gherkin
Scenario: 各ゾーンに固有のBGMが設定されている
  Given すべてのゾーン（0-3）にBGMが割り当てられている
  Then 各ゾーンのBGMが異なる曲調である
  And BGMデータがPyxelのMusic形式で定義されている
```

```gherkin
Scenario: AIが方針からBGMデータを生成できる
  Given 親が「草原は明るく冒険っぽく」と方針を伝える
  When AIがPyxelのMusic/Soundデータを生成する
  Then 生成されたデータがPyxel APIで再生可能である
  And main.py内にデータとして埋め込まれている（外部ファイル不使用）
```

---

## J16: 戦闘BGMを付ける

```gherkin
Scenario: 戦闘開始時にBGMが戦闘曲に切り替わる
  Given フィールドBGMが再生中である
  When エンカウントが発生して戦闘画面に遷移する
  Then BGMが戦闘BGMに切り替わる
```

```gherkin
Scenario: 戦闘終了後にフィールドBGMに戻る
  Given 戦闘BGMが再生中である
  When 戦闘に勝利してフィールドに戻る
  Then BGMがフィールドの該当ゾーンBGMに復帰する
```

---

## J11: BGMの雰囲気を変えたい

```gherkin
Scenario: 既存BGMの曲調を変更できる
  Given ゾーン1のBGMが暗い曲調である
  When 親がAIに「もっと明るい感じにして」と頼む
  And AIがMusicデータを修正する
  And Run する
  Then ゾーン1のBGMが明るい曲調に変わっている
```

```gherkin
Scenario: BGM変更が他のゾーンに影響しない
  Given ゾーン1のBGMを変更した
  When ゾーン0に移動する
  Then ゾーン0のBGMは変更前のまま再生される
```

---

## J17: 効果音をイベントに紐づける

```gherkin
Scenario: 攻撃時にSFXが再生される
  Given 攻撃アクションにSFXが設定されている
  When 戦闘中に攻撃コマンドを選択する
  Then 攻撃SFXが再生される
```

```gherkin
Scenario: 回復時にSFXが再生される
  Given 回復アクションにSFXが設定されている
  When 戦闘中に回復呪文を使用する
  Then 回復SFXが再生される
```

```gherkin
Scenario: レベルアップ時にSFXが再生される
  Given レベルアップイベントにSFXが設定されている
  When 戦闘勝利後にレベルアップ条件を満たす
  Then レベルアップSFXが再生される
```

```gherkin
Scenario: AIが方針からSFXデータを生成できる
  Given 親が「攻撃音はシュッと短く、回復はキラキラ」と方針を伝える
  When AIがPyxelのSoundデータを生成する
  Then 生成されたデータがPyxel APIで再生可能である
  And main.py内にデータとして埋め込まれている
```

---

## J24: 効果音を自分で作る

```gherkin
Scenario: Code MakerのSoundエディタでSFXを編集できる
  Given Code Maker の Sound タブが開いている
  When 子どもがマウスで音程を描く
  And 再生ボタンで試聴する
  Then 編集した音が即座に聞ける
```

```gherkin
Scenario: Soundエディタで編集したSFXがゲーム内で使われる
  Given Sound エディタで攻撃用SFXを編集した
  When Run してゲーム内で攻撃する
  Then 編集したSFXが戦闘中に再生される
```

---

## J18: ダメージ演出を付ける

```gherkin
Scenario: 敵にダメージを与えたとき画面フラッシュが発生する
  Given ダメージVFXが実装されている
  When 戦闘中に敵にダメージを与える
  Then 画面が一瞬白くフラッシュする
```

```gherkin
Scenario: プレイヤーがダメージを受けたとき画面が赤く光る
  Given 被ダメージVFXが実装されている
  When 戦闘中にプレイヤーがダメージを受ける
  Then 画面が一瞬赤くフラッシュする
```

```gherkin
Scenario: VFXがゲームの動作を妨げない
  Given VFXが有効な状態でゲームを実行する
  When 戦闘中にダメージを与える/受ける
  Then VFX表示後にゲームが正常に続行する
  And フレームレートが著しく低下しない
```

---

## J19: 場面転換の演出

```gherkin
Scenario: 町に入るときフェードアウト/フェードインする
  Given フェード演出が実装されている
  When キャラが町のタイルに乗る
  Then 画面がフェードアウトする
  And 町の画面が表示される
  And 画面がフェードインする
```

```gherkin
Scenario: 戦闘開始時にフェード演出が入る
  Given フェード演出が実装されている
  When エンカウントが発生する
  Then フィールド画面がフェードアウトする
  And 戦闘画面がフェードインする
```

```gherkin
Scenario: フェード演出中に操作を受け付けない
  Given フェード演出中である
  When プレイヤーがキー入力する
  Then 操作は無視される
  And フェード完了後に操作が有効になる
```

---

## 共通条件

```gherkin
Scenario: すべての音データがmain.py内に埋め込まれている
  Given BGM/SFXのデータが定義されている
  Then すべての音データがmain.py内のPythonリテラルまたは.pyxres内に格納されている
  And 外部ファイル参照（open等）を使用していない
  And Code Maker上で正常に再生される
```

```gherkin
Scenario: 演出が無効でもゲームが正常に動作する
  Given BGM/SFX/VFXのいずれかが未設定または無効な状態
  When Run する
  Then ゲーム本編（移動・戦闘・セーブ等）が正常に動作する
  And エラーが発生しない
```
