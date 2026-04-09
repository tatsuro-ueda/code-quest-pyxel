# 詳細設計書: スマホ全画面対応カスタムHTMLラッパー

`structure-design.md` で決定した構造を、実装可能なレベルに落とし込む。

反映済みの構造判断:
- D1: iframe 方式 / D2: document.documentElement 対象 / D3: ontouchstart 判定
- D4: webkitRequestFullscreen フォールバック / D5: ひらがな案内テキスト
- D6: object-fit: contain / D7: build_web_release.py に後処理追加
- D8: CSS transition + setTimeout(5000), iframe外余白タップで再表示
- D9: 画面下部中央・半透明 / D10: index.html + pyxel.html 2ファイル体制
- D11: templates/wrapper.html / D12: iframe に allowfullscreen 付与
- D13: 余白が狭い端末では再表示不可でもOK（初回5秒で十分）
- D14: ボタンフォントは sans-serif（追加フォント読み込み不要）

---

## 1. wrapper.html テンプレート構成

配置先: `templates/wrapper.html`（D11）

### HTML の論理構造

```mermaid
graph TD
    subgraph index.html
        HTML[html lang=ja] --> HEAD[head]
        HTML --> BODY[body]

        HEAD --> META1[meta charset=UTF-8]
        HEAD --> META2[meta viewport<br/>width=device-width<br/>initial-scale=1<br/>maximum-scale=1<br/>viewport-fit=cover]
        HEAD --> STYLE[style<br/>全画面用CSS +<br/>フェードアウト transition]

        BODY --> BTN[button#fullscreen-btn<br/>ぜんがめんであそぶ<br/>画面下部・中央・半透明]
        BODY --> MSG[p#fallback-msg<br/>ホームがめんについかすると<br/>ぜんがめんであそべます<br/>初期状態: 非表示]
        BODY --> IFRAME[iframe#game-frame<br/>src=pyxel.html<br/>allowfullscreen]
        BODY --> SCRIPT[script<br/>Fullscreen API +<br/>フェードアウト制御]
    end

    style BTN fill:#49a,color:#fff
    style MSG fill:#a94,color:#fff
    style IFRAME fill:#4a9,color:#fff
```

### テンプレート変数

| 変数 | 置換内容 | 例 |
|---|---|---|
| `{{PYXEL_HTML_SRC}}` | iframe の src に設定するファイル名 | `pyxel.html` |

---

## 2. CSS 詳細

### レイアウト構造

```mermaid
graph TD
    subgraph 通常表示
        N1[body<br/>margin: 0<br/>background: #000] --> N2[iframe<br/>width: 100vw<br/>height: 100vh<br/>border: none]
        N1 --> N3[button<br/>position: fixed<br/>bottom: 20px<br/>z-index: 1000<br/>opacity: 1]
    end

    subgraph フェードアウト後
        FA1[body] --> FA2[iframe<br/>変化なし]
        FA1 --> FA3[button<br/>opacity: 0<br/>pointer-events: none]
    end

    subgraph 全画面表示
        F1[body<br/>margin: 0<br/>background: #000] --> F2[iframe<br/>width: 100vw<br/>height: 100vh<br/>border: none]
        F1 --> F3[button<br/>display: none]
    end

    N1 -->|5秒経過| FA1
    FA1 -->|余白タップ| N1
    N1 -->|ボタンタップ| F1
```

### 概念コード

```css
/* ベースレイアウト */
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  background: #000;
  width: 100%;
  height: 100%;
}

/* ゲーム iframe */
#game-frame {
  width: 100vw;
  height: 100vh;
  border: none;
  display: block;
}

/* 全画面ボタン — D9: 画面下部中央・半透明 */
#fullscreen-btn {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  padding: 12px 24px;
  font-size: 16px;
  background: rgba(255, 255, 255, 0.85);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-family: sans-serif;
  /* D8: フェードアウト用 transition */
  transition: opacity 0.5s ease;
  opacity: 1;
}

/* フェードアウト状態 */
#fullscreen-btn.faded {
  opacity: 0;
  pointer-events: none;
}

/* フォールバック案内 — D5: ひらがな */
#fallback-msg {
  display: none;
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  color: #aaa;
  font-size: 14px;
  font-family: sans-serif;
  text-align: center;
}
```

---

## 3. JavaScript 詳細

### 処理フロー

```mermaid
graph TD
    A[DOMContentLoaded] --> B[要素取得<br/>btn, fallbackMsg, gameFrame]
    B --> C{タッチデバイス?<br/>D3}

    C -->|いいえ| D[btn を非表示<br/>PC: 何も表示しない]

    C -->|はい| E{Fullscreen API<br/>対応? D4}

    E -->|いいえ| F[btn 非表示<br/>fallbackMsg 表示<br/>ひらがな案内]

    E -->|はい| G[btn 表示<br/>ぜんがめんであそぶ]

    G --> H[btn に click<br/>イベント登録]
    G --> FA[フェードアウト<br/>タイマー開始<br/>setTimeout 5000ms]

    FA --> FB[5秒後<br/>btn.classList.add faded]

    H --> I[クリック時]
    I --> J{requestFullscreen?}
    J -->|はい| K[documentElement<br/>.requestFullscreen]
    J -->|いいえ| L{webkitRequest<br/>Fullscreen?}
    L -->|はい| M[documentElement<br/>.webkitRequestFullscreen]

    K --> N[全画面モード ON]
    M --> N
```

### フェードアウト・再表示の処理フロー

```mermaid
graph TD
    A[ページ読み込み完了] --> B[btn 表示<br/>opacity: 1]
    B --> C[setTimeout 5000ms<br/>タイマーID保持]
    C --> D[5秒経過]
    D --> E[btn.classList.add faded<br/>opacity: 0 + pointer-events: none]

    E --> F{body の click イベント}
    F --> G{クリック対象は<br/>iframe 外?}
    G -->|はい| H[btn.classList.remove faded<br/>opacity: 1]
    H --> I[タイマーリセット<br/>clearTimeout + 新 setTimeout]
    I --> D

    G -->|いいえ| J[何もしない<br/>ゲーム操作を邪魔しない]

    E -.-> NOTE[D13: 余白が狭い端末では<br/>再表示できなくてもOK<br/>初回5秒で十分]

    style E fill:#69a,color:#fff
    style H fill:#49a,color:#fff
    style J fill:#888,color:#fff
    style NOTE fill:#555,color:#ccc
```

### 全画面切り替え・解除の処理フロー

```mermaid
graph TD
    subgraph 全画面化
        A[btn click] --> B[フェードアウトタイマー停止<br/>clearTimeout]
        B --> C{requestFullscreen?}
        C -->|はい| D[documentElement<br/>.requestFullscreen]
        C -->|いいえ| E[documentElement<br/>.webkitRequestFullscreen]
        D --> F[全画面 ON]
        E --> F
    end

    subgraph fullscreenchange ハンドラ
        F --> G[fullscreenchange 発火]
        G --> H{fullscreenElement<br/>あり?}
        H -->|あり| I[btn.style.display = none<br/>全画面中はボタン不要]
        H -->|なし| K[btn.style.display = block<br/>btn.classList.remove faded<br/>ボタン再表示]
        K --> L[フェードアウトタイマー再開<br/>setTimeout 5000ms]
    end

    style F fill:#4a9,color:#fff
    style I fill:#69a,color:#fff
    style K fill:#49a,color:#fff
```

### 概念コード

```javascript
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('fullscreen-btn');
  const fallbackMsg = document.getElementById('fallback-msg');
  const gameFrame = document.getElementById('game-frame');
  const target = document.documentElement;
  let fadeTimer = null;

  // --- D3: タッチデバイス判定 ---
  const isTouchDevice =
    'ontouchstart' in window || navigator.maxTouchPoints > 0;

  if (!isTouchDevice) {
    btn.style.display = 'none';
    return;
  }

  // --- D4: Fullscreen API 対応判定 ---
  const canFullscreen =
    target.requestFullscreen || target.webkitRequestFullscreen;

  if (!canFullscreen) {
    btn.style.display = 'none';
    fallbackMsg.style.display = 'block';
    return;
  }

  // --- D8: フェードアウトタイマー ---
  function startFadeTimer() {
    clearTimeout(fadeTimer);
    fadeTimer = setTimeout(() => {
      btn.classList.add('faded');
    }, 5000);
  }

  function showButton() {
    btn.classList.remove('faded');
    btn.style.display = 'block';
    startFadeTimer();
  }

  // 初回表示 → 5秒後フェードアウト
  startFadeTimer();

  // --- D8: iframe外の余白タップで再表示 ---
  document.body.addEventListener('click', (e) => {
    // iframe 内のクリックはここに来ない（別ドキュメント）
    // btn 自体のクリックは全画面化で処理するので除外
    if (e.target === btn) return;
    if (btn.classList.contains('faded')) {
      showButton();
    }
  });

  // --- 全画面ボタンのクリックハンドラ ---
  btn.addEventListener('click', () => {
    clearTimeout(fadeTimer);
    if (target.requestFullscreen) {
      target.requestFullscreen();
    } else if (target.webkitRequestFullscreen) {
      target.webkitRequestFullscreen();
    }
  });

  // --- 全画面状態の変更を監視 ---
  const onFullscreenChange = () => {
    const isFullscreen =
      document.fullscreenElement || document.webkitFullscreenElement;
    if (isFullscreen) {
      btn.style.display = 'none';
      clearTimeout(fadeTimer);
    } else {
      showButton();
    }
  };

  document.addEventListener('fullscreenchange', onFullscreenChange);
  document.addEventListener('webkitfullscreenchange', onFullscreenChange);
});
```

### イベントリスナー対応表

```mermaid
graph TD
    subgraph 標準ブラウザ Chrome / Firefox
        E1[fullscreenchange] --> H1[onFullscreenChange]
        E2[document.fullscreenElement] --> H2[全画面状態の判定]
        E3[requestFullscreen] --> H3[全画面化の実行]
    end

    subgraph Safari iOS 16.4+
        W1[webkitfullscreenchange] --> H1
        W2[document.webkitFullscreenElement] --> H2
        W3[webkitRequestFullscreen] --> H3
    end

    H1 --> R[ボタン表示/非表示を切替<br/>+ フェードタイマー制御]
    H2 --> R
    H3 --> F[全画面モード ON]

    style W1 fill:#a94,color:#fff
    style W2 fill:#a94,color:#fff
    style W3 fill:#a94,color:#fff
```

---

## 4. build_web_release.py への追加処理

### 追加する関数

```mermaid
graph TD
    A[既存: stage_release_files] --> B[既存: run pyxel package]
    B --> C[既存: run pyxel app2html]
    C --> D[既存: copy app.html → pyxel.html]
    D --> E[★追加: generate_wrapper]
    E --> F[既存: copy to project root<br/>★ index.html も追加]

    subgraph generate_wrapper の内部処理
        E --> G[templates/wrapper.html を読み込む<br/>D11]
        G --> H[PYXEL_HTML_SRC を<br/>pyxel.html に置換]
        H --> I[index.html として書き出す]
    end

    style E fill:#a94,color:#fff
    style I fill:#4a9,color:#fff
```

### copy to project root の変更

```mermaid
graph TD
    subgraph 既存のコピー対象
        A1[pyxel.html]
        A2[pyxel.pyxapp]
    end

    subgraph ★追加のコピー対象
        B1[index.html<br/>カスタムHTMLラッパー]
    end

    A1 --> C[プロジェクトルート]
    A2 --> C
    B1 --> C

    style B1 fill:#49a,color:#fff
```

### 概念コード

```python
def generate_wrapper(build_dir: Path, project_root: Path):
    """カスタムHTMLラッパーを生成する（D7, D11）"""
    template_path = project_root / "templates" / "wrapper.html"
    template = template_path.read_text(encoding="utf-8")

    # iframe の src を設定
    wrapper_html = template.replace("{{PYXEL_HTML_SRC}}", "pyxel.html")

    # index.html として出力
    output_path = build_dir / "index.html"
    output_path.write_text(wrapper_html, encoding="utf-8")
```

---

## 5. テスト方針

### テスト対象と手段

```mermaid
graph TD
    subgraph 自動テスト Playwright
        T1[タッチデバイス<br/>エミュレーション] --> T1A[ボタン表示確認<br/>ぜんがめんであそぶ]
        T1 --> T1B[Fullscreen API<br/>呼び出し確認]
        T1 --> T1C[5秒後に<br/>フェードアウト確認]
        T1 --> T1D[余白クリックで<br/>再表示確認]
        T2[デスクトップ<br/>エミュレーション] --> T2A[ボタン非表示確認]
        T3[ビルドスクリプト<br/>実行テスト] --> T3A[index.html<br/>生成確認]
        T3 --> T3B[iframe src=pyxel.html<br/>確認]
        T3 --> T3C[allowfullscreen<br/>属性確認 D12]
    end

    subgraph 手動テスト 実機
        M1[iPhone<br/>Safari 16.4+] --> M1A[全画面化の動作確認]
        M1 --> M1B[フェードアウト<br/>+ 余白タップ再表示]
        M2[Android<br/>Chrome] --> M2A[全画面化の動作確認]
        M2 --> M2B[フェードアウト<br/>+ 余白タップ再表示]
        M3[iPhone<br/>Safari 16.3以前] --> M3A[ひらがな案内テキスト<br/>表示確認]
    end

    style T1 fill:#49a,color:#fff
    style T1C fill:#69a,color:#fff
    style T1D fill:#69a,color:#fff
    style M1 fill:#4a9,color:#fff
    style M2 fill:#4a9,color:#fff
```

### テストシナリオと検証項目の対応

```mermaid
graph TD
    G1[gherkin シナリオ1<br/>全画面化] --> T1A[Playwright: ボタン表示]
    G1 --> T1B[Playwright: API呼び出し]
    G1 --> M1A[実機: 全画面動作]

    G2[gherkin シナリオ2<br/>全画面解除] --> M1A
    G2 --> M2A[実機: Android 全画面動作]

    G3[gherkin シナリオ3<br/>PC] --> T2A[Playwright: ボタン非表示]

    G4[gherkin シナリオ4<br/>iOS旧版] --> M3A[実機: 案内テキスト]

    G5[gherkin シナリオ5<br/>ビルド] --> T3A[ビルド: index.html生成]
    G5 --> T3B[ビルド: iframe src]
    G5 --> T3C[ビルド: allowfullscreen]

    G6[gherkin シナリオ6<br/>フェードアウト] --> T1C[Playwright: フェードアウト]
    G6 --> T1D[Playwright: 余白タップ再表示]
    G6 --> M1B[実機: フェードアウト]
    G6 --> M2B[実機: フェードアウト]

    style G1 fill:#49a,color:#fff
    style G6 fill:#69a,color:#fff
```

---

## 参照

- [`./structure-design.md`](./structure-design.md) — 構造設計（判断論点・アーキテクチャ）
- [`./journey.md`](./journey.md) — このジャーニーの体験設計
- [`./gherkin.md`](./gherkin.md) — 受け入れ条件
