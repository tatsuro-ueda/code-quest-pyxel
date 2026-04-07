# Design Scratch: bink導入の再設計（発見事項と方針転換）

`design.md` は「bink（Blade Ink Python）を `pip install` して使う」前提で書かれていた。
しかし実装着手時に調査した結果、**その前提自体が成立しない**ことが判明した。
このスクラッチは、発見した事実と、それを踏まえた **現実的な方針** を残すためのメモ。

- 親設計: `design.md`（理想形。InkWrapperのAPI設計は有効）
- 親要件: `requirements.md`（開発者体験の要件は変わらず有効）
- このスクラッチの位置づけ: **実装前に一度立ち止まって、方針を切り替えるためのスクラッチ**

---

## 1. 発見した事実（悲報）

```mermaid
flowchart TD
    Start[docs/91-external-libraries.md の記述] --> F1[bink Blade Ink Python<br/>優先度・高・1番目]
    F1 --> Try1[pip install bink]
    Try1 --> Fact1[❌ 実物は<br/>RAD Game Tools の<br/>Bink Video codec 拘束]
    Fact1 --> Note1[BINK_OK / BINK_FAIL / LIB / ctypes<br/>が露出する別物]

    Start --> F2[inkpy COUR4G3/inkpy<br/>archived 2024-04]
    F2 --> Try2[pip install inkpy]
    Try2 --> Fact2[❌ PyPI の inkpy は<br/>ODT/テンプレート変換系の別物]

    F2 --> Try3[pip install git+https://github.com/COUR4G3/inkpy]
    Try3 --> Fact3[⚠️ インストール可能だが<br/>Story クラスは<br/>inklecate 事前コンパイル JSON を要求]
    Fact3 --> Need[inklecate C#/mono の<br/>システム導入が必要]
    Need --> Bad[😩 これは楽したい思想に反する]

    Start --> F4[blade-ink / pyInkle / ink-py]
    F4 --> Fact4[❌ いずれも PyPI に存在しない]
```

### 要約

| 候補 | 結果 | 理由 |
|---|---|---|
| `pip install bink` | ❌ | 同名の Bink Video codec bindings であり ink とは無関係 |
| `pip install inkpy` | ❌ | 同名の ODT/テンプレート変換ライブラリであり ink とは無関係 |
| GitHub `COUR4G3/inkpy` | ❌採用不可 | Story が inklecate 事前コンパイル JSON を要求。ビルド工程増 |
| `blade-ink` / `pyInkle` / `ink-py` | ❌ | PyPI に存在しない |

→ **Python エコシステムに、raw `.ink` を読めて保守されている runtime は事実上存在しない。**

---

## 2. 現在のdialogデータの実態（想定より遥かに小さい）

`TOWN_MESSAGES` の現物を確認した結果：

```python
TOWN_MESSAGES = {
    (20, 12): ["はじめの村へようこそ！", "ここではプログラミングの", "基礎を学べます。"],
    (30, 22): ["ロジックタウンだ。", "条件分岐とループを", "マスターしよう！"],
    (18, 34): ["アルゴリズムの街。", "効率的な解法を", "見つけよう！"],
    (25, 6):  ["バグレポート城。", "世界の平和を", "取り戻すのだ！"],
}
```

**たった4エントリ・合計12行のセリフ**。進行度分岐も選択肢もなし。
使用箇所は `main.py:1254` の1箇所のみ：

```python
lines = TOWN_MESSAGES.get(key, ["..."])
self.show_message(lines)
```

つまり **いま inkle ink の本格runtime（変数・分岐・選択肢・VAR）を入れるのは、明らかにオーバーキル**。

```mermaid
flowchart TD
    Reality[現状のdialog規模] --> R1[4シーン 12行 分岐なし]
    R1 --> Q{ink runtime 本格導入は妥当か?}
    Q -->|No| Reason1[ほぼ使わない機能に<br/>外部依存とビルド工程を増やす]
    Q -->|No| Reason2[ビルド工程 inklecate は<br/>楽したい思想に反する]
    Q -->|No| Reason3[将来必要になってから<br/>本物 runtime に差し替えても間に合う]
    Reason1 --> Pivot[🔄 方針転換]
    Reason2 --> Pivot
    Reason3 --> Pivot
```

---

## 3. 方針転換：最小ink風パーサを自前で持つ

**InkWrapper の外部API (`load` / `continue_story` / `choose` / `set_variable`) は design.md のまま据え置く**。
内部実装だけを「外部bink依存」から「自前の最小パーサ」に差し替える。

```mermaid
flowchart TD
    subgraph Before["design.md の当初案"]
        M1[main.py] --> W1[InkWrapper]
        W1 --> B1[bink 外部ライブラリ]
        B1 --> I1[town1.ink]
    end

    Before ==>|実現不能と判明| After

    subgraph After["現実解：最小ink風パーサ自前実装"]
        M2[main.py] --> W2[InkWrapper<br/>APIは同一]
        W2 --> MP[MiniInkParser<br/>game/dialog/mini_ink.py 新設]
        MP --> I2[town1.ink<br/>ink風のサブセット]
    end
```

### 対応する ink サブセット（最小）

| ink 機能 | 対応 | 備考 |
|---|---|---|
| プレーンテキスト行 | ✅ | 1行1メッセージ |
| `// コメント` | ✅ | 行頭/行中スキップ |
| `=== knot_name ===` | ✅ | セクション |
| `-> target` divert | ✅ | knot 間ジャンプ |
| `-> END` | ✅ | 会話終了 |
| `{var: case - ... - else}` 条件分岐 | ✅ | set_variable 連動の単純条件のみ |
| `VAR x = "..."` 宣言 | ✅ | 文字列変数のみ |
| `* [choice]` 選択肢 | ⏸ 今回未対応 | code-quest の現状で不要 |
| `~ x = ...` 代入式・計算 | ⏸ 今回未対応 | 不要 |
| include | ⏸ 今回未対応 | 不要 |

→ **「今、本当に必要な範囲だけ」** 実装する。将来不足したら機能追加する（あるいは本物 runtime に差し替える）。

---

## 4. MiniInkParser のデータモデル（縦長）

```mermaid
flowchart TD
    File[town1.ink ソース] --> Parse[parse 行単位で走査]
    Parse --> Model[Story model]

    Model --> M1[variables dict]
    Model --> M2[knots dict]
    M2 --> K1[knot entry]
    M2 --> K2[knot before_boss]
    M2 --> K3[knot after_boss]
    K1 --> Lines1[lines list]
    K1 --> Next1[divert or END]
    K2 --> Lines2[lines list]
    K3 --> Lines3[lines list]

    Model --> State[実行時状態]
    State --> S1[current knot]
    State --> S2[line index]
```

### 実行フロー

```mermaid
sequenceDiagram
    participant Main as main.py
    participant W as InkWrapper
    participant P as MiniInkParser
    participant F as town1.ink

    Main->>W: load("town1")
    W->>F: read UTF-8
    F-->>W: source text
    W->>P: parse(source)
    P-->>W: Story model
    W->>W: current_knot = "entry"
    W->>W: line_index = 0
    W-->>Main: ok

    Main->>W: set_variable("phase", "before_boss")
    W->>W: variables["phase"] = "before_boss"

    loop 会話が続く限り
        Main->>W: continue_story()
        W->>W: 現在のknotから次の行を取り出す
        alt プレーン行
            W-->>Main: "村長: ようこそ"
        else 条件分岐
            W->>W: variables を参照して枝を選ぶ
            W-->>Main: 選ばれた枝の次の行
        else -> divert
            W->>W: current_knot = target
            W->>W: line_index = 0
            W-->>Main: 再帰的に次の行
        else -> END
            W-->>Main: None
        end
    end
```

---

## 5. ファイル構成（方針転換版）

```mermaid
flowchart TD
    Root[/home/exedev/code-quest-pyxel/]
    Root --> MainPy[main.py<br/>TOWN_MESSAGES 削除・参照箇所置換]
    Root --> Game[game/ 新設]
    Root --> Assets[assets/]

    Game --> Dialog[dialog/ 新設]
    Dialog --> Init[__init__.py]
    Dialog --> Runner[ink_runner.py<br/>InkWrapper クラス]
    Dialog --> Parser[mini_ink.py<br/>MiniInkParser/Story/Knot]

    Assets --> Dialogs[dialogs/ 新設]
    Dialogs --> Hello[hello.ink 検証用]
    Dialogs --> Town1[town1.ink]
    Dialogs --> Town2[logic_town.ink]
    Dialogs --> Town3[algo_town.ink]
    Dialogs --> Castle[bug_report_castle.ink]
```

**外部依存ゼロ**。Pyxel と Python 標準ライブラリだけで完結する。

---

## 6. town1.ink の想定内容（最小）

```ink
// はじめの村 入口
=== entry ===
はじめの村へようこそ！
ここではプログラミングの
基礎を学べます。
-> END
```

現状の `TOWN_MESSAGES` の1エントリをそのまま1ファイルに写す。将来、魔王前/後で文言を変えたくなったらこうする：

```ink
VAR phase = "before_boss"

=== entry ===
{ phase:
  - "before_boss": -> before_boss
  - "after_boss":  -> after_boss
}

=== before_boss ===
はじめの村へようこそ！
ここではプログラミングの基礎を学べます。
-> END

=== after_boss ===
英雄よ、ようこそ戻った！
もう学ぶことはあまりないだろう。
-> END
```

---

## 7. 段階的な実装プラン（縦長）

```mermaid
flowchart TD
    P0[Phase 0: 設計スクラッチをコミット<br/>本ファイル] --> P1

    P1[Phase 1: game/dialog パッケージ新設] --> P1a[__init__.py]
    P1a --> P1b[mini_ink.py<br/>パーサと Story 実装]
    P1b --> P1c[ink_runner.py<br/>InkWrapper 実装]

    P1c --> P2[Phase 2: 単体動作確認]
    P2 --> P2a[assets/dialogs/hello.ink 作成]
    P2a --> P2b[python -c でwrapper単体検証<br/>pyxel無しでも動く前提]

    P2b --> P3[Phase 3: town 4シーンを .ink 化]
    P3 --> P3a[town1.ink 作成]
    P3a --> P3b[logic_town.ink]
    P3b --> P3c[algo_town.ink]
    P3c --> P3d[bug_report_castle.ink]

    P3d --> P4[Phase 4: main.py 参照箇所の置換]
    P4 --> P4a[_check_tile_events の<br/>TOWN_MESSAGES.get を<br/>wrapper 呼び出しに置換]
    P4a --> P4b[座標→シーン名マッピングを追加]

    P4b --> P5[Phase 5: TOWN_MESSAGES 辞書削除]
    P5 --> P5a[main.py から削除]

    P5a --> P6[Phase 6: 検証]
    P6 --> P6a[mini_ink の単体スクリプト検証]
    P6a --> P6b[main.py 構文チェック python -c import]
    P6b --> P6c[grep で TOWN_MESSAGES 残存ゼロ確認]
```

---

## 8. 今回のスコープで意図的に「やらない」こと

```mermaid
flowchart TD
    No[今回のスコープ外] --> N1[❌ 選択肢 star 構文]
    No --> N2[❌ 代入 tilde 構文]
    No --> N3[❌ include]
    No --> N4[❌ 本物 ink runtime への差し替え]
    No --> N5[❌ セーブデータ互換維持]

    N1 --> R1[理由: 現状の<br/>TOWN_MESSAGES に選択肢なし]
    N2 --> R2[理由: 計算は Python 側で十分]
    N3 --> R3[理由: シーン数が少ない]
    N4 --> R4[理由: inklecate 依存は楽したい思想に反する<br/>必要になったときに再判断]
    N5 --> R5[理由: ユーザーが壊れても可と明言]
```

---

## 9. この方針転換で守れること / 守れないこと

### 守れること（design.md から継承）

- ✅ **main.py に会話データ直書きをやめる** — 根本目的は達成
- ✅ **InkWrapper の3メソッド公開API** — シグネチャはそのまま
- ✅ **シーン単位 `.ink` ファイル分割**
- ✅ **ink風の knot/divert 構文** — 将来 inkle ink 本体に差し替える可能性を残す
- ✅ **進行度分岐を Python の if から ink 側へ移す余地**
- ✅ **外部依存ゼロ** — 実はこちらの方が「楽」

### 守れないこと

- ❌ **本物 inkle ink runtime** — パーサはサブセットで、高度な ink 記法は落ちる
- ❌ **ink 互換の .ink ファイル** — inklecate で通らない書き方になる可能性

### トレードオフの総合評価

```mermaid
flowchart TD
    T[方針転換の総合評価] --> Good[👍 得たもの]
    T --> Bad[👎 失ったもの]

    Good --> G1[外部依存ゼロ]
    Good --> G2[ビルド工程なし]
    Good --> G3[即日実装可能]
    Good --> G4[APIは設計通り]

    Bad --> B1[ink 高度機能なし]
    Bad --> B2[inklecate 互換なし]

    G1 --> Verdict[✅ 楽したい目的に合致]
    G2 --> Verdict
    G3 --> Verdict
    G4 --> Verdict
    B1 --> Accept[⏸ 現状不要なので受容]
    B2 --> Accept
```

---

## 10. 決定事項

1. **本スクラッチを採用** し、`design.md` の外部 bink 依存部分はこのスクラッチで上書きされたものとして扱う
2. **`game/dialog/mini_ink.py` と `game/dialog/ink_runner.py` を新設**
3. **`assets/dialogs/` 配下に4つの `.ink` を作成**
4. **main.py の `TOWN_MESSAGES` は削除**、参照箇所は InkWrapper 呼び出しに置換
5. **検証**: mini_ink 単体スクリプトで読める／`main.py` の import が通る／`TOWN_MESSAGES` の grep がゼロ

この順で実装に入る。
