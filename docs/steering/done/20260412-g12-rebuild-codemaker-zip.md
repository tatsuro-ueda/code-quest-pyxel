---
status: done
priority: high
scheduled: 2026-04-12T22:00:00.000+09:00
dateCreated: 2026-04-12T22:00:00.000+09:00
dateModified: 2026-04-12T22:00:00.000+09:00
tags:
  - task
  - g12
  - codemaker
  - web
---

# 2026年4月12日 G12 code-maker.zip 再ビルド

> 状態：完了

---

## 1) Journey（どこへ行くか）

- **深層的目的**：Code Makerで遊ぶゲームをWeb版と同じ最新版にする
- **やらないこと**：build_codemaker.pyのインライン処理（main.pyは既にインライン済み）

```mermaid
flowchart TB
    subgraph BEFORE["Before"]
        direction TB
        B1["code-maker.zip を Code Maker にアップロード"]
        B1 --> B2["古い版（6,343行）が動く"]
        B2 --> B_END["Web版（6,823行）と内容が違う"]
    end

    subgraph AFTER["After"]
        direction TB
        A1["code-maker.zip を Code Maker にアップロード"]
        A1 --> A2["最新版が動く"]
        A2 --> A_END["Web版と同じゲームが遊べる"]
    end

    BEFORE ~~~ AFTER

    classDef oldStyle fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef newStyle fill:#d4edda,stroke:#155724,color:#000000;
    classDef endOld fill:#f5c6cb,stroke:#721c24,color:#000000,font-weight:bold;
    classDef endNew fill:#c3e6cb,stroke:#155724,color:#000000,font-weight:bold;

    class B1,B2 oldStyle;
    class A1,A2 newStyle;
    class B_END endOld;
    class A_END endNew;
```

### 調査結果

- code-maker.zip はコミット 8870c0b 時点で止まっている
- 現在のmain.pyは既にsrc/*.pyがインライン済みの単一ファイル（6,823行）
- pyxresは名前が違う（zip内: my_resource.pyxres、プロジェクト: blockquest.pyxres）が、main.pyは両方を探す設計
- tools/build_codemaker.py は存在しない

### やること

1. tools/build_codemaker.py を作る（main.py + pyxres を zipにまとめるだけ）
2. code-maker.zip を最新版で再ビルド
3. ヘッドレステストで起動確認

---

## 2) Gherkin（完了条件）

### シナリオ1：zip内のmain.pyがプロジェクトのmain.pyと同一

> {build_codemaker.py を実行} すると {zip内main.pyとプロジェクトのmain.pyが同一}

```mermaid
flowchart TD
    A1["build_codemaker.py 実行"] --> A2["code-maker.zip を展開"]
    A2 --> A3{main.py が同一?}
    A3 -->|Yes| AOK["OK: 同じバージョン"]
    A3 -->|No| AFAIL["NG: バージョン不一���"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    classDef fail fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef gate fill:#e2e3f1,stroke:#3949ab,color:#000000;
    class A3 gate;
    class AOK ok;
    class AFAIL fail;
```

---

### シナリオ2：zip内のpyxresが最新

> {build_codemaker.py を実行} すると {zip内のmy_resource.pyxresがblockquest.pyxresと同一}

```mermaid
flowchart TD
    B1["zip展開"] --> B2{my_resource.pyxres == blockquest.pyxres?}
    B2 -->|Yes| BOK["OK: 同じリソース"]
    B2 -->|No| BFAIL["NG: リソース不一致"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    classDef fail fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef gate fill:#e2e3f1,stroke:#3949ab,color:#000000;
    class B2 gate;
    class BOK ok;
    class BFAIL fail;
```

---

### シナリオ3：ヘッドレステストでzip版が起動する

> {zip内のmain.pyとmy_resource.pyxresで} ヘッドレス起動テストが通過する

```mermaid
flowchart TD
    C1["zip展開先でヘッドレス起動"] --> C2{1フレーム描画完走?}
    C2 -->|Yes| COK["OK: Code Makerで動く"]
    C2 -->|No| CFAIL["NG: 起動失敗"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    classDef fail fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef gate fill:#e2e3f1,stroke:#3949ab,color:#000000;
    class C2 gate;
    class COK ok;
    class CFAIL fail;
```

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：なし

```mermaid
flowchart LR
    subgraph INPUT["インプット"]
        I1["main.py"]
        I2["assets/blockquest.pyxres"]
    end

    subgraph PROCESS["処理"]
        P1["build_codemaker.py:\nblock-quest/main.py にコピー\nblockquest.pyxres を my_resource.pyxres にリネームコピー\nzip圧縮"]
    end

    subgraph OUTPUT["アウトプット"]
        O1["code-maker.zip"]
    end

    INPUT --> PROCESS --> OUTPUT

    classDef io fill:#e2e3f1,stroke:#3949ab,color:#000000;
    classDef proc fill:#fff3cd,stroke:#856404,color:#000000;
    classDef out fill:#d4edda,stroke:#155724,color:#000000;

    class I1,I2 io;
    class P1 proc;
    class O1 out;
```

### zip構造

```
code-maker.zip
  block-quest/
    main.py              <- プロジェクトのmain.pyそのまま
    my_resource.pyxres   <- blockquest.pyxresをリネーム
```

---

## 4) Tasklist

- [x] tools/build_codemaker.py 作成
- [x] code-maker.zip 再ビルド
- [x] シナリオ1: main.py同一チェック — OK
- [x] シナリオ2: pyxres同一チェック — OK
- [x] シナリオ3: ヘッドレス起動テスト — OK

---

## 5) Discussion（記録・反省）

### 2026年4月12日 22:00（調査・起票）

**Observe**：code-maker.zip内のmain.py(6,343行)と現在のmain.py(6,823行)が別バージョン。pyxresも異なる。build_codemaker.pyは存在しない。
**Think**：main.pyは既にインライン済みなので、zipに詰めるだけのシンプルなスクリプトで十分。pyxresはmy_resource.pyxresの名前でzipに入れる（Code Maker互換）。
**Act**：タスクノート起票。
