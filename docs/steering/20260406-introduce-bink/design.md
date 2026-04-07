# Design: Pyxel版code-questへのbink導入設計

`requirements.md` で定義した要件を、**どう実装するか**の設計ドキュメント。
方針は一言で言うと **「bink依存を1ファイルに閉じ込め、main.pyには薄いAPIだけを見せる」**。

---

## 1. 設計の大方針

```mermaid
flowchart TD
    P1[原則1: bink依存を1ファイルに閉じる] --> Why1[いつか別の道具<br/>inkpy等 に乗り換える可能性を残す]
    P2[原則2: main.pyからはAPI 3つだけ] --> Why2[会話呼び出しコードを単純化し<br/>main.py の複雑さを増やさない]
    P3[原則3: .ink ファイルはシーン単位で分割] --> Why3[1ファイルが肥大化せず<br/>並行編集でも衝突しにくい]
    P4[原則4: 既存の TOWN_MESSAGES は<br/>段階的に削除する] --> Why4[一括置換は不具合の温床<br/>町単位で動作確認しながら進める]
    P5[原則5: 進行度フラグは Python 側が持ち続ける] --> Why5[セーブデータ互換を壊さない<br/>ink は表示差分だけを担当]
```

---

## 2. レイヤー構成（縦長）

```mermaid
flowchart TD
    subgraph Top["🎮 ゲーム本体"]
        Main[main.py<br/>戦闘・マップ・入力ループ]
    end

    subgraph Mid["📝 会話レイヤー 新設"]
        Wrapper[game/dialog/ink_runner.py<br/>InkWrapper クラス]
    end

    subgraph Lib["📦 外部ライブラリ"]
        Bink[bink<br/>Blade Ink Python]
    end

    subgraph Data["📂 データ"]
        Ink1[assets/dialogs/town1.ink]
        Ink2[assets/dialogs/castle.ink]
        Ink3[assets/dialogs/cave_b1.ink]
        InkN[assets/dialogs/...ink]
    end

    Main -->|load/continue_story/choose の3つだけ| Wrapper
    Wrapper -->|bink API を呼ぶ| Bink
    Bink -->|.ink をパースして実行| Ink1
    Bink --> Ink2
    Bink --> Ink3
    Bink --> InkN
```

**ポイント**: main.py は Bink の存在を知らない。InkWrapper の3つのメソッドだけが見えている。

---

## 3. InkWrapper の公開API（最小3つ）

```mermaid
flowchart TD
    API[InkWrapper 公開API] --> M1[load scene_name]
    API --> M2[continue_story]
    API --> M3[choose index]

    M1 --> D1[assets/dialogs/ 配下から<br/>scene_name.ink を読み込む<br/>→ Story オブジェクト生成]
    M2 --> D2[次の1行を返す<br/>返り値は str または None<br/>None なら会話終了]
    M3 --> D3[プレイヤーが選択肢を選んだ時に呼ぶ<br/>引数は 0始まりのインデックス]
```

### メソッドシグネチャ（案）

```python
class InkWrapper:
    def load(self, scene_name: str) -> None: ...
    def continue_story(self) -> str | None: ...
    def choose(self, index: int) -> None: ...

    # 補助（内部参照用）
    def current_choices(self) -> list[str]: ...
    def set_variable(self, name: str, value) -> None: ...
    def get_variable(self, name: str): ...
```

`set_variable` / `get_variable` は ink 側の `VAR` を Python から出し入れするための窓口。これも **ink_runner.py の中に閉じる**。

---

## 4. 会話呼び出しのシーケンス（縦長）

```mermaid
sequenceDiagram
    participant Player as プレイヤー
    participant Main as main.py
    participant W as InkWrapper
    participant Bink as bink
    participant File as town1.ink

    Player->>Main: NPCに話しかける (Z/決定キー)
    Main->>W: load("town1")
    W->>Bink: Story(file_contents)
    Bink->>File: パース
    File-->>Bink: AST
    Bink-->>W: story オブジェクト
    W-->>Main: OK

    loop 会話が続く限り
        Main->>W: continue_story()
        W->>Bink: story.Continue()
        Bink-->>W: 次の1行
        W-->>Main: "村長: ようこそ勇者よ"
        Main->>Player: 画面に1行表示
        Player->>Main: 決定キー
    end

    alt 選択肢あり
        Main->>W: current_choices()
        W-->>Main: ["はい", "いいえ"]
        Main->>Player: 選択肢UI表示
        Player->>Main: 「はい」を選ぶ
        Main->>W: choose(0)
        W->>Bink: story.ChooseChoiceIndex(0)
    end

    Main->>W: continue_story()
    W-->>Main: None  (会話終了)
    Main->>Player: メッセージウィンドウを閉じる
```

---

## 5. ファイル構成（新設ファイル）

```mermaid
flowchart TD
    Root[/home/exedev/code-quest-pyxel/]
    Root --> MainPy[main.py<br/>修正のみ TOWN_MESSAGES削除]
    Root --> Assets[assets/]
    Root --> Game[game/ 新設]

    Assets --> Dialogs[dialogs/ 新設]
    Dialogs --> D1[town1.ink 新設]
    Dialogs --> D2[castle.ink 新設]
    Dialogs --> D3[cave_b1.ink 新設]
    Dialogs --> DHello[hello.ink 検証用]

    Game --> Dialog[dialog/ 新設]
    Dialog --> Runner[ink_runner.py 新設]
    Dialog --> Init[__init__.py 新設]
```

- 既存ファイルは `main.py` の修正のみ
- `game/` パッケージは新設（将来の分割のための入れ物も兼ねる）
- `assets/dialogs/` 配下の `.ink` はテキストエディタで直接編集

---

## 6. .ink ファイルの内部構造（進行度分岐の設計）

```mermaid
flowchart TD
    Start[town1.ink] --> Entry[=== entry ===]
    Entry --> Q{現在のフラグは?}
    Q -->|before_boss| K1[-> before_boss]
    Q -->|defeated_boss| K2[-> after_boss]

    K1 --> B1[=== before_boss ===<br/>村長: 魔王を倒してくれ]
    B1 --> End1[-> END]

    K2 --> A1[=== after_boss ===<br/>村長: よくぞ戻った！]
    A1 --> End2[-> END]
```

### ink側のサンプル（イメージ）

```ink
VAR phase = "before_boss"

=== entry ===
{ phase:
    - "before_boss": -> before_boss
    - "after_boss":  -> after_boss
}

=== before_boss ===
村長: 魔王を倒してくれ、勇者よ。
-> END

=== after_boss ===
村長: よくぞ戻った！ 英雄よ！
-> END
```

### Python側の呼び出しイメージ

```python
wrapper.load("town1")
wrapper.set_variable("phase",
    "after_boss" if self.flags.get("defeated_boss") else "before_boss")
while line := wrapper.continue_story():
    self.message_queue.append(line)
```

**進行度フラグ自体は Python 側の `self.flags` が持ち続ける**。inkは表示差分だけを担当。セーブデータ互換を壊さないための妥協点。

---

## 7. 移植順序（町単位で段階的に）

```mermaid
flowchart TD
    Phase0[Phase 0: 準備] --> P0a[pip install bink]
    P0a --> P0b[assets/dialogs/ 作成]
    P0b --> P0c[hello.ink で最小動作確認]

    P0c --> Phase1[Phase 1: ラッパー構築]
    Phase1 --> P1a[ink_runner.py 新設]
    P1a --> P1b[load/continue_story/choose の<br/>3メソッド実装]
    P1b --> P1c[単体で hello.ink を読めることを確認]

    P1c --> Phase2[Phase 2: town1 パイロット]
    Phase2 --> P2a[town1 の既存セリフを<br/>town1.ink に書き写す]
    P2a --> P2b[main.py の town1 表示箇所を<br/>wrapper 呼び出しに置換]
    P2b --> P2c{動作一致?}
    P2c -->|No| P2a
    P2c -->|Yes| Phase3

    Phase3[Phase 3: 横展開] --> P3a[castle.ink 移植]
    P3a --> P3b[cave_b1.ink 移植]
    P3b --> P3c[残りのシーン順次移植]
    P3c --> Phase4

    Phase4[Phase 4: 進行度分岐の ink 化] --> P4a[if 分岐を knot に置換]
    P4a --> P4b[set_variable で phase を渡す形に統一]

    P4b --> Phase5[Phase 5: 大掃除]
    Phase5 --> P5a[main.py から TOWN_MESSAGES 辞書削除]
    P5a --> P5b[関連する if 分岐残骸も削除]
    P5b --> Goal[🎉 main.py に会話データなし]
```

---

## 8. リスクと対策

```mermaid
flowchart TD
    R1[リスク1: bink の改行処理が<br/>Pyxel のフォント描画と合わない] --> C1[対策: InkWrapper 内で<br/>改行を吸収・再整形する]

    R2[リスク2: 日本語文字コード問題] --> C2[対策: .ink ファイルは UTF-8 で統一<br/>読み込み時に明示 encoding 指定]

    R3[リスク3: .ink パースが重くて<br/>ゲーム起動が遅くなる] --> C3[対策: シーン単位で遅延ロード<br/>必要になった時だけ load]

    R4[リスク4: セーブデータ互換性] --> C4[対策: 進行度フラグは Python 側が保持<br/>ink 側は状態を持たない設計]

    R5[リスク5: 既存の選択肢UIが<br/>ink の選択肢と噛み合わない] --> C5[対策: current_choices で文字列配列を返し<br/>UI 側は従来通りの描画で済ませる]
```

---

## 9. 設計の「やらない」こと

```mermaid
flowchart TD
    No[今回の設計で踏み込まないこと] --> N1[❌ ink 側で所持金や装備を管理]
    No --> N2[❌ ink 側でセーブ/ロード]
    No --> N3[❌ ink 側から pyxel API を直接叩く外部関数]
    No --> N4[❌ 複数 .ink ファイルの include]
    No --> N5[❌ 戦闘シーケンスの ink 化]

    N1 --> R[理由: Python 側のデータ構造と<br/>二重管理になり整合性が崩れる]
    N2 --> R
    N3 --> R2[理由: 抽象境界を壊し<br/>乗り換え困難になる]
    N4 --> R3[理由: まずシンプルな構造で<br/>軌道に乗せる]
    N5 --> R4[理由: リアルタイム描画は<br/>Pyxel の仕事]
```

---

## 10. 完了の定義（Definition of Done）

```mermaid
flowchart TD
    DoD[✅ Definition of Done] --> D1[main.py に TOWN_MESSAGES が存在しない]
    DoD --> D2[main.py から bink を import していない]
    DoD --> D3[ink_runner.py が単独で単体テスト可能である]
    DoD --> D4[各シーンの表示が移植前と同一である]
    DoD --> D5[新規 NPC のセリフ追加が ink ファイル編集のみで完結する]
    DoD --> D6[進行度別セリフが if なしで ink の knot で表現されている]
```
