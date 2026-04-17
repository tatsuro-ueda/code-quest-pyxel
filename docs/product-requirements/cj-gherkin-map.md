# カスタマージャーニーgherkin: Map（マップ・タイル操作）

- 対象カスタマージャーニー: CJ01-CJ07
- 根拠: [`customer-journeys.md`](./customer-journeys.md)
- structure-design の中心: タイルバンク、タイル配置、ゾーン生成、derive_world_from_tilemap

---

## CJG01: はじめてのタイル配置

```gherkin
Scenario: 子どもがタイルを1個置いてRunすると変化が見える
  Given Pyxel Code Maker の Tilemap タブが開いている
  And タイルパレットに草・木・水などのタイルが表示されている
  When 子どもがパレットから草タイルを選択する
  And マップ上の任意のマスをクリックする
  Then そのマスが草タイルに変わる
  When Run ボタンを押す
  Then ゲームが起動し、変更したマスにキャラが歩ける
  And 操作開始から確認まで1分以内で完了する
```

```gherkin
Scenario: タイルパレットのタイルがすべてタイルバンクに登録されている
  Given タイルバンクに登録されたタイルIDの一覧がある
  Then パレットに表示されるすべてのタイルがタイルバンクに登録されている
  And 各タイルの16x16ピクセルデータが存在する
```

---

## CJG02: 道を作る

```gherkin
Scenario: 草タイルを並べて通行可能な道ができる
  Given マップ上に通行不可のタイル（山・水など）がある
  When 草タイルを複数マスに連続して配置する
  And Run する
  Then キャラが配置した草タイルの上を連続して歩ける
  And 通行不可タイルの上は歩けない
```

```gherkin
Scenario: 道の配置が1サイクル1-2分で回る
  Given Tilemap タブが開いている
  When 草タイルで5マス程度の道を描く
  And Run して歩いて確認する
  Then 描画から確認まで2分以内で完了する
```

---

## CJG03: 森を作る

```gherkin
Scenario: 木タイルを密集させると通行不可エリアができる
  Given マップ上に草タイルのエリアがある
  When 木タイルを複数マスにまとめて配置する
  And Run する
  Then キャラは木タイルの上を歩けない
  And 木タイルの隙間（草タイル）は歩ける
```

```gherkin
Scenario: 通り道を残さないと閉じ込められる（設計の気づき）
  Given 木タイルでエリアを完全に囲む
  When Run してキャラがそのエリアに入る
  Then キャラはエリアの外に出られない
```

---

## CJG04: 水辺を作る

```gherkin
Scenario: 水タイルは通行不可として機能する
  Given マップ上に草タイルのエリアがある
  When 水タイルを配置する
  And Run する
  Then キャラは水タイルの上を歩けない
```

```gherkin
Scenario: 水タイルと岸タイルを組み合わせて湖を作れる
  Given タイルパレットに水タイルと岸タイルがある
  When 水タイルで内側を、岸タイルで縁を配置する
  And Run する
  Then 湖として視覚的にまとまって見える
  And 岸タイルも通行不可である
```

---

## CJG05: 装飾で世界を彩る

```gherkin
Scenario: 装飾タイル（花・岩・キノコ・サボテン・茂み）は通行可能
  Given マップ上に装飾タイルを配置する
  When Run する
  Then キャラは装飾タイルの上を歩ける
  And エンカウント率は草タイルと同じ（0.06）
```

```gherkin
Scenario: 装飾タイルをゾーンごとに使い分けて個性が出る
  Given ゾーン0（草原）に花タイルを配置する
  And ゾーン1（森）にキノコタイルを配置する
  And ゾーン3（砂漠）にサボテンタイルを配置する
  When Run する
  Then 各ゾーンが異なる見た目になる
```

---

## CJG06: 迷路を作る

```gherkin
Scenario: 壁タイルと道タイルの組み合わせで迷路が作れる
  Given 壁タイル（通行不可）と草タイル（通行可能）がパレットにある
  When 壁と草を交互に配置して迷路パターンを作る
  And Run する
  Then キャラは草タイルの通路のみ移動できる
  And 壁タイルで行き止まりが作れる
```

```gherkin
Scenario: 迷路をテストプレイで自分で解ける
  Given 迷路パターンをTilemapで作成した
  When Run してキャラを操作する
  Then 入口から出口まで到達できるか自分で確認できる
  And 行き止まりに入ったら引き返せる
```

---

## CJG07: ランドマークを配置する

```gherkin
Scenario: マルチタイルランドマーク（2x2）を配置できる
  Given タイルパレットに世界樹・通信塔のランドマークタイルがある
  When ランドマークタイルをマップに配置する
  Then 2x2のタイルが正しい位置に自動配置される
```

```gherkin
Scenario: ランドマークは通行不可で隣接からインタラクションできる
  Given マップにランドマーク（世界樹）が配置されている
  When Run してキャラをランドマークに向かって歩かせる
  Then ランドマークの上には乗れない
  And ランドマークに隣接した状態でインタラクションキーを押すとイベントが発生する
```

```gherkin
Scenario: ランドマーク配置が既存の拠点と重ならない
  Given CASTLE_POS, TOWN_*, CAVE_GLITCH の座標がある
  When ランドマークを配置する
  Then 既存拠点の座標とランドマークのタイルが重ならない
```

---

## 共通条件

```gherkin
Scenario: derive_world_from_tilemap が GUI 編集結果を正しく逆変換する
  Given Tilemap エディタでタイルを変更した
  When Run する
  Then derive_world_from_tilemap が呼ばれ内部の地形データに変換される
  And 変換後のデータでゲームが正常に動作する
  And 既存のセーブデータとの互換性が維持される
```

```gherkin
Scenario: すべてのタイルIDがタイルバンクに登録されている
  Given ゲーム内で定義されたタイルID一覧がある
  Then すべてのタイルIDがタイルバンクに登録されている
  And 各タイルの16x16ピクセルデータがPyxelリソースに描画されている
```
