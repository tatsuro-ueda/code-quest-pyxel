# 受け入れ条件: スマホで全画面にして遊ぶ

## プロダクト判断の合意事項

| # | 論点 | 決定 | 理由 |
|---|---|---|---|
| P1 | 全画面の起動方法 | ユーザーが**全画面ボタンをタップ**する（自動全画面化はしない） | iOS Safari がユーザー操作起点を必須としており、自動化はブロックされる |
| P2 | 全画面の解除方法 | **ブラウザ標準の操作**に委ねる（専用の解除ボタンは置かない） | Chrome はスワイプ、Safari は画面上部タップ等。独自UIを被せると混乱する |
| P3 | PCブラウザでの扱い | 全画面ボタンは**非表示**（タッチデバイスのみ表示） | PCではF11等で全画面にできる。余計なボタンを出さない |
| P4 | iOS 16.3以前の対応 | Fullscreen API は使えないので、**「ホーム画面に追加」を案内する文言**を表示する | PWA化は別ステアリング。最低限の案内だけ行う |
| P5 | アスペクト比 | **維持する**（引き伸ばさない）。余白は黒で埋める | ドット絵が歪むと見た目が崩れる |
| P6 | ラッパー方式 | **iframe 方式**をまず採用する | app.html をそのまま埋め込めるため、ビルドパイプラインの変更が最小 |
| P7 | ボタン位置 | **画面下部・中央**に半透明ボタンを配置 | ゲームパッドの上あたり。目につきやすく、誤タップしにくい |
| P8 | ボタン文言 | **「ぜんがめんであそぶ」**（ひらがな） | 子どもが読めるようにひらがな表記 |
| P9 | ボタン自動非表示 | ページ読み込み後**5秒でフェードアウト**。画面タップで再表示 | 邪魔にならずスッキリ。いつでも再呼び出し可能 |
| P10 | 配信URL | **index.html を新規追加**。pyxel.html も引き続きアクセス可能 | ルートURL（/）でラッパーが開く。既存URLも壊さない |

### プロダクト判断の依存関係

```mermaid
graph TD
    P1[P1: 全画面の起動方法<br/>ボタンタップで起動] --> P3[P3: PCブラウザ<br/>ボタン非表示]
    P1 --> P4[P4: iOS 16.3以前<br/>ホーム画面追加を案内]
    P1 --> P2[P2: 全画面の解除<br/>ブラウザ標準操作]
    P1 --> P7[P7: ボタン位置<br/>画面下部・中央]
    P1 --> P8[P8: ボタン文言<br/>ぜんがめんであそぶ]
    P1 --> P9[P9: 5秒で<br/>フェードアウト]
    P6[P6: iframe 方式] --> P5[P5: アスペクト比維持<br/>余白は黒]
    P6 --> P10[P10: index.html 追加<br/>pyxel.html も維持]

    style P1 fill:#4a9,color:#fff
    style P6 fill:#4a9,color:#fff
```

---

## シナリオ全体マップ

```mermaid
graph TD
    START[ユーザーがページを開く] --> DEV{デバイス判定}

    DEV -->|タッチデバイス| API{Fullscreen API<br/>対応?}
    DEV -->|PC| S3[シナリオ3<br/>ボタン非表示<br/>従来通り動作]

    API -->|対応<br/>iOS 16.4+ / Android| S1[シナリオ1<br/>ぜんがめんであそぶ<br/>ボタン表示]
    API -->|非対応<br/>iOS 16.3以前| S4[シナリオ4<br/>ホーム画面追加を案内]

    S1 --> S6[シナリオ6<br/>5秒後にフェードアウト<br/>余白タップで再表示]
    S6 -->|タップ| S1
    S1 -->|ボタンタップ| S1F[全画面化]
    S1F --> S2[シナリオ2<br/>全画面解除<br/>通常表示に戻る]
    S2 -->|再タップ| S1

    S5[シナリオ5<br/>ビルドスクリプト] -.->|生成| START

    style S1 fill:#49a,color:#fff
    style S1F fill:#49a,color:#fff
    style S2 fill:#49a,color:#fff
    style S3 fill:#888,color:#fff
    style S4 fill:#a94,color:#fff
    style S5 fill:#94a,color:#fff
    style S6 fill:#69a,color:#fff
```

---

## シナリオ

### シナリオ1: スマホで全画面にして遊ぶ（正常系）

```gherkin
Given スマホのブラウザで index.html を開いている
And タッチデバイスである
Then 画面下部・中央に「ぜんがめんであそぶ」ボタンが半透明で表示される
And ボタンは5秒後にフェードアウトする
When 「ぜんがめんであそぶ」ボタンをタップする
Then ブラウザのアドレスバーとナビゲーションバーが消える
And ゲーム画面が端末の画面いっぱいに拡大される
And アスペクト比は維持され、余白は黒で埋まる
And バーチャルゲームパッドが表示される
```

```mermaid
graph TD
    A[index.html を開く] --> B[タッチデバイス検知]
    B --> C[ぜんがめんであそぶ<br/>ボタン表示<br/>画面下部・中央]
    C --> D[5秒後に<br/>フェードアウト]
    D --> D2[画面タップで<br/>再表示]
    D2 --> E[ボタンをタップ]
    C --> E
    E --> F[requestFullscreen 呼び出し]
    F --> G[アドレスバー消える]
    G --> H[canvas 拡大<br/>アスペクト比維持]
    H --> I[ゲームパッド表示]
    I --> J[全画面プレイ開始]

    style C fill:#49a,color:#fff
    style D fill:#69a,color:#fff
    style J fill:#4a9,color:#fff
```

### シナリオ2: 全画面を解除する

```gherkin
Given 全画面モードでゲームをプレイしている
When ブラウザ標準の全画面解除操作を行う
Then 通常表示に戻る
And 「ぜんがめんであそぶ」ボタンが再表示される
```

```mermaid
graph TD
    A[全画面でプレイ中] --> B{解除操作}
    B -->|Chrome:<br/>上からスワイプ| C[fullscreenchange<br/>イベント発火]
    B -->|Safari:<br/>画面上部タップ| C
    B -->|Android:<br/>戻るボタン| C
    C --> D[通常表示に戻る]
    D --> E[全画面ボタン再表示]
    E --> F[再タップで<br/>全画面に戻れる]

    style A fill:#49a,color:#fff
    style D fill:#888,color:#fff
```

### シナリオ3: PCブラウザからアクセスする

```gherkin
Given PCのブラウザで index.html を開いている
And タッチデバイスではない
Then 「ぜんがめんであそぶ」ボタンは表示されない
And ゲームは従来通り動作する
```

```mermaid
graph TD
    A[PCブラウザで<br/>index.html を開く] --> B[タッチデバイスではない]
    B --> C[全画面ボタン非表示]
    C --> D[iframe 内で<br/>pyxel.html がロード]
    D --> E[従来通りの<br/>ゲーム表示]

    F[全画面にしたい場合] -.-> G[F11キー等<br/>ブラウザ標準操作]

    style C fill:#888,color:#fff
    style E fill:#4a9,color:#fff
```

### シナリオ4: iOS 16.3以前でアクセスする

```gherkin
Given iOS 16.3以前の Safari で index.html を開いている
And Fullscreen API が利用できない
Then 「ぜんがめんであそぶ」ボタンの代わりに「ホームがめんについかすると ぜんがめんであそべます」という案内が表示される
```

```mermaid
graph TD
    A[iOS 16.3以前の<br/>Safari で開く] --> B[Fullscreen API<br/>非対応を検知]
    B --> C[全画面ボタンを<br/>表示しない]
    C --> D[代わりに案内テキスト表示<br/>ホームがめんについかすると<br/>ぜんがめんであそべます]
    D --> E{ユーザーの行動}
    E -->|ホーム画面に追加| F[PWA的に起動<br/>アドレスバーなし]
    E -->|そのまま遊ぶ| G[通常表示で<br/>ゲームプレイ]

    style D fill:#a94,color:#fff
    style F fill:#4a9,color:#fff
```

### シナリオ5: ビルドスクリプトで全画面対応HTMLが生成される

```gherkin
Given tools/build_web_release.py を実行する
When ビルドが完了する
Then プロジェクトルートに index.html（カスタムHTMLラッパー）が生成される
And index.html 内に pyxel.html が iframe で埋め込まれている
And Fullscreen API の JavaScript が含まれている
```

```mermaid
graph TD
    A[build_web_release.py<br/>実行] --> B[pyxel package<br/>app.pyxapp 生成]
    B --> C[pyxel app2html<br/>app.html 生成]
    C --> D[app.html →<br/>pyxel.html にコピー]
    D --> E[wrapper.html<br/>テンプレート読み込み]
    E --> F[pyxel.html を<br/>iframe src に設定]
    F --> G[Fullscreen API<br/>JavaScript 注入]
    G --> H[index.html<br/>として出力]
    H --> I[プロジェクトルートに<br/>コピー]

    style A fill:#94a,color:#fff
    style I fill:#4a9,color:#fff
```

### シナリオ6: ボタンのフェードアウトと再表示

```gherkin
Given スマホのブラウザで index.html を開いている
And タッチデバイスである
And Fullscreen API が利用できる
When ページ読み込みから5秒が経過する
Then 「ぜんがめんであそぶ」ボタンがフェードアウトして消える
When iframe外の黒余白をタップする
Then 「ぜんがめんであそぶ」ボタンがフェードインして再表示される
And 再び5秒後にフェードアウトする
```

```mermaid
graph TD
    A[ページ読み込み完了] --> B[ぜんがめんであそぶ<br/>ボタン表示]
    B --> C[5秒経過]
    C --> D[フェードアウト<br/>opacity 1→0]
    D --> E[ボタン非表示]
    E --> F{iframe外の<br/>黒余白タップ}
    F --> G[フェードイン<br/>opacity 0→1]
    G --> H[ボタン再表示]
    H --> I[5秒経過]
    I --> D

    H --> J{ボタンをタップ}
    J --> K[全画面化<br/>シナリオ1へ]

    style B fill:#49a,color:#fff
    style D fill:#69a,color:#fff
    style G fill:#69a,color:#fff
    style K fill:#4a9,color:#fff
```

---

## 成功基準

| 基準 | 内容 |
|---|---|
| 動作 | ボタンをタップすると全画面に切り替わる |
| 対応端末 | iOS Safari (16.4+) / Android Chrome |
| 解除 | ブラウザ標準の操作で全画面を解除できる |
| ビルド | `tools/build_web_release.py` の実行だけで全画面対応HTMLが生成される |
| 互換性 | PC ブラウザでも従来通り動作する |
| 保守性 | Pyxel バージョンアップ時にラッパーが壊れにくい構造 |

### 成功基準の検証フロー

```mermaid
graph TD
    V1[ビルド実行] --> V2{index.html<br/>生成された?}
    V2 -->|はい| V3[スマホで開く]
    V2 -->|いいえ| FAIL1[ビルド基準 NG]

    V3 --> V4{全画面ボタン<br/>表示される?}
    V4 -->|はい| V5[ボタンをタップ]
    V4 -->|いいえ| FAIL2[動作基準 NG]

    V5 --> V6{全画面に<br/>なった?}
    V6 -->|はい| V7[ブラウザ操作で解除]
    V6 -->|いいえ| FAIL3[対応端末基準 NG]

    V7 --> V8{通常表示に<br/>戻った?}
    V8 -->|はい| V9[PCで開く]
    V8 -->|いいえ| FAIL4[解除基準 NG]

    V9 --> V10{従来通り<br/>動作する?}
    V10 -->|はい| PASS[全基準 OK]
    V10 -->|いいえ| FAIL5[互換性基準 NG]

    style PASS fill:#4a9,color:#fff
    style FAIL1 fill:#a44,color:#fff
    style FAIL2 fill:#a44,color:#fff
    style FAIL3 fill:#a44,color:#fff
    style FAIL4 fill:#a44,color:#fff
    style FAIL5 fill:#a44,color:#fff
```

---

## 参照

- [`./journey.md`](./journey.md) — このジャーニーの体験設計
- [`./structure-design.md`](./structure-design.md) — 構造設計
- [`./detailed-design.md`](./detailed-design.md) — 詳細設計
