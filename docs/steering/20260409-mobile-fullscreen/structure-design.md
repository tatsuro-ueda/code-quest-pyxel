# 構造設計書: スマホ全画面対応カスタムHTMLラッパー

`journey.md` / `gherkin.md` で合意済みのプロダクト判断（iframe方式／ひらがなボタン／5秒フェードアウト／index.html追加）を、アーキテクチャとして定義する。

プロダクト判断はここで覆さない。技術選定・構造方針のみを扱う。

---

## 設計判断の論点

| # | 論点 | 決定 | 理由 | 代替案と却下理由 |
|---|---|---|---|---|
| D1 | ラッパー方式 | **iframe 方式**。`pyxel.html` を iframe で埋め込む `index.html` を新規作成 | app.html をそのまま使えるため、ビルドパイプラインの変更が最小。Pyxel バージョンアップ時にも壊れにくい | スクリプト抽出方式：canvas に直接アクセスできるが、app2html の出力形式に依存し Pyxel バージョンアップ時に壊れる可能性 |
| D2 | Fullscreen API の呼び出し対象 | **`document.documentElement`**（ページ全体） | iframe ごと全画面にするため、親ページの `<html>` 要素を対象にする | iframe 内の canvas：クロスオリジン制約で操作できない場合がある |
| D3 | タッチデバイス判定 | **`'ontouchstart' in window` または `navigator.maxTouchPoints > 0`** | 広く対応されている判定方法。CSS の `@media (hover: none)` よりJSで制御しやすい | User-Agent 判定：不正確で保守性が低い |
| D4 | Safari 対応 | **`webkitRequestFullscreen` をフォールバック**として呼ぶ | iOS Safari 16.4+ は `webkitRequestFullscreen` を使う。標準 `requestFullscreen` → `webkitRequestFullscreen` の順で試行 | webkit のみ：Chrome/Firefox で動かない |
| D5 | Fullscreen API 非対応時 | **ボタンの代わりに案内テキスト（ひらがな）を表示** | iOS 16.3以前やFullscreen API未対応ブラウザへのフォールバック | 何も表示しない：ユーザーが全画面にする手段を知れない |
| D6 | CSS スケーリング | **`object-fit: contain` でアスペクト比維持**、余白は `background: #000` | ドット絵の歪みを防ぐ。黒余白はゲームの雰囲気に合う | `object-fit: cover`：ゲーム画面の端が切れる |
| D7 | ビルドスクリプトへの組み込み | **`tools/build_web_release.py` に後処理を追加**。`pyxel app2html` 出力後に HTMLテンプレートと結合 | 既存のビルドフローに自然に追加できる | 別スクリプト：実行を忘れるリスク |
| D8 | ボタンのフェードアウト | **CSS transition + JS setTimeout(5000)**。**iframe外の黒余白タップ**で再表示し、再び5秒後にフェードアウト | P9 に基づく。CSS transition でスムーズに消えるのが自然。iframe外タップならゲームパッド操作と競合しない | JS アニメーション：CSS だけで十分／画面全体タップ：ゲームパッドと競合する／ダブルタップ：子どもには難しい |
| D9 | ボタンの配置とスタイル | **`position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%)`**。半透明白背景 | P7 に基づく。画面下部中央でゲームパッドの上あたり | absolute：スクロールに追従しない |
| D10 | 配信ファイル構成 | **index.html（ラッパー）+ pyxel.html（Pyxel生成）**の2ファイル体制 | P10 に基づく。ルートURL で index.html が開く。既存 pyxel.html への直リンクも維持 | pyxel.html を置き換え：ラッパーなしでアクセスする手段がなくなる |
| D11 | テンプレート配置 | **`templates/wrapper.html`**（プロジェクトルート直下に templates/ を新設） | ビルド用テンプレート置き場として今後も拡張できる | tools/ 内：ビルドスクリプトとテンプレートの責務が混在／steering 内：実装素材と設計ドキュメントが混在 |
| D12 | iframe の allowfullscreen | **付ける** | 将来 Pyxel 側が Fullscreen API に対応した場合にも問題なく動く。害はない | 付けない：現時点では不要だが、将来の互換性リスク |
| D13 | 余白が狭い端末での再表示 | **再表示できなくてもOK**。初回5秒表示で十分 | スマホ縦画面では黒余白がほぼない場合がある。フォールバックの複雑さに見合わない | iframe下に薄いタップ領域：見た目に影響／ダブルタップ併用：子どもには難しい |
| D14 | ボタンフォント | **sans-serif**（システムデフォルト） | 追加フォントの読み込みが不要で軽量。ボタンはゲーム世界の外なので統一感は不要 | misaki_gothic.ttf：レトロ感は出るがWebフォント読み込みが必要でファイルサイズ増／monospace：レトロ感はあるが日本語の見た目がイマイチ |

### 判断の依存関係

```mermaid
graph TD
    D1[D1: iframe 方式] --> D2[D2: Fullscreen 対象<br/>document.documentElement]
    D1 --> D6[D6: CSS スケーリング<br/>object-fit: contain]
    D1 --> D7[D7: ビルドスクリプト<br/>後処理として追加]
    D1 --> D10[D10: 配信ファイル構成<br/>index.html + pyxel.html]

    D3[D3: タッチデバイス判定<br/>ontouchstart / maxTouchPoints] --> D5[D5: API 非対応時<br/>案内テキスト表示]
    D3 --> D8[D8: フェードアウト<br/>CSS transition + setTimeout<br/>iframe外タップで再表示]
    D3 --> D9[D9: ボタン配置<br/>画面下部・中央・半透明]

    D2 --> D4[D4: Safari 対応<br/>webkitRequestFullscreen]

    D7 --> D11[D11: テンプレート配置<br/>templates/wrapper.html]
    D1 --> D12[D12: iframe に<br/>allowfullscreen 付与]

    style D1 fill:#49a,color:#fff
    style D3 fill:#49a,color:#fff
    style D8 fill:#69a,color:#fff
    style D9 fill:#69a,color:#fff
    style D10 fill:#69a,color:#fff
    style D11 fill:#69a,color:#fff
    style D12 fill:#69a,color:#fff
```

---

## iframe 方式の比較検討

```mermaid
graph TD
    Q{どの方式?} --> A[iframe 方式<br/>★採用]
    Q --> B[スクリプト抽出方式]

    A --> A1[メリット:<br/>app.html をそのまま使える<br/>ビルドパイプラインの変更が最小<br/>Pyxel更新時に壊れにくい]
    A --> A2[デメリット:<br/>iframe 内の canvas に<br/>直接アクセスできない]

    B --> B1[メリット:<br/>canvas に直接アクセスできる<br/>Fullscreen API が確実に動く]
    B --> B2[デメリット:<br/>app2html の出力形式に依存<br/>Pyxel バージョンアップ時に<br/>壊れる可能性]

    A1 --> R[判定: iframe 方式を採用<br/>保守性を優先]
    A2 --> R
    B1 --> R
    B2 --> R

    style A fill:#4a9,color:#fff
    style R fill:#4a9,color:#fff
```

---

## アーキテクチャ

### ファイル構成

```mermaid
graph TD
    subgraph プロジェクトルート
        IDX[index.html<br/>カスタムHTMLラッパー<br/>★新規生成<br/>ルートURLで配信]
        PYX[pyxel.html<br/>Pyxel生成HTML<br/>既存・直リンク維持]
    end

    subgraph templates/
        WRP[wrapper.html<br/>ラッパーテンプレート<br/>★新規作成]
    end

    subgraph tools/
        BLD[build_web_release.py<br/>★既存を拡張]
    end

    BLD -->|pyxel app2html| PYX
    BLD -->|テンプレート読み込み| WRP
    WRP -->|pyxel.html を埋め込み| IDX
    IDX -->|iframe src| PYX

    style IDX fill:#49a,color:#fff
    style WRP fill:#49a,color:#fff
    style BLD fill:#a94,color:#fff
```

### ビルドフロー

```mermaid
graph TD
    A[build_web_release.py 実行] --> B[pyxel package<br/>app.pyxapp 生成]
    B --> C[pyxel app2html<br/>app.html 生成]
    C --> D[app.html を<br/>pyxel.html としてコピー]
    D --> E{★新規追加ステップ}
    E --> F[templates/wrapper.html<br/>読み込み]
    F --> G[テンプレート内の<br/>PYXEL_HTML_SRC を置換]
    G --> H[index.html として出力]
    H --> I[index.html + pyxel.html を<br/>プロジェクトルートにコピー]

    style E fill:#a94,color:#fff
    style F fill:#49a,color:#fff
    style H fill:#4a9,color:#fff
```

### ランタイム動作

```mermaid
graph TD
    subgraph 初期化
        A[ユーザーが index.html を開く] --> B[iframe 内で pyxel.html がロード]
        B --> C{タッチデバイス?}
        C -->|はい| D{Fullscreen API 対応?}
        C -->|いいえ| E[ボタン非表示<br/>通常表示で動作]
        D -->|はい| F[ぜんがめんであそぶ<br/>ボタン表示<br/>画面下部・中央]
        D -->|いいえ| G[ひらがな案内テキスト表示]
    end

    subgraph フェードアウト
        F --> FA[5秒経過]
        FA --> FB[CSS transition で<br/>フェードアウト]
        FB --> FC{iframe外の<br/>黒余白タップ?}
        FC -->|はい| F
    end

    subgraph 全画面切り替え
        F --> H[ボタンをタップ]
        H --> I{ブラウザ種別}
        I -->|標準対応| J[requestFullscreen]
        I -->|Safari| K[webkitRequestFullscreen]
        J --> L[全画面モード ON]
        K --> L
    end

    subgraph 全画面中
        L --> M[ボタン非表示]
        M --> N[canvas が画面いっぱいに拡大<br/>アスペクト比維持・黒余白]
        N --> O[ゲームプレイ]
    end

    subgraph 全画面解除
        O --> P[fullscreenchange イベント検知]
        P --> Q[通常表示に戻る]
        Q --> F
    end
```

---

## 実装ステップ

```mermaid
graph TD
    S1[Step 1<br/>templates/wrapper.html<br/>テンプレート作成] --> S2[Step 2<br/>Fullscreen API +<br/>フェードアウト JS 実装]
    S2 --> S3[Step 3<br/>CSS で iframe 全画面 +<br/>ボタンスタイル]
    S3 --> S4[Step 4<br/>build_web_release.py に<br/>ラッパー生成を追加]
    S4 --> S5[Step 5<br/>iOS Safari /<br/>Android Chrome でテスト]
    S5 --> S6[Step 6<br/>GitHub Pages に<br/>デプロイして確認]

    style S1 fill:#49a,color:#fff
    style S4 fill:#a94,color:#fff
    style S6 fill:#4a9,color:#fff
```

---

## 参照

- [`./journey.md`](./journey.md) — このジャーニーの体験設計
- [`./gherkin.md`](./gherkin.md) — 受け入れ条件
- [`./detailed-design.md`](./detailed-design.md) — 詳細設計（概念コード・API仕様）
