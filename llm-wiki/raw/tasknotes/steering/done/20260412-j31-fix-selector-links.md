---
status: done
priority: high
scheduled: 2026-04-12T21:30:00.000+09:00
dateCreated: 2026-04-12T21:30:00.000+09:00
dateModified: 2026-04-12T21:50:00.000+09:00
tags:
  - task
  - j31
  - web
  - selector
  - archived
---

# 2026年4月12日 J31 選択ページのリンク先復旧

> 状態：完了

---

## 1) 改善対象ジャーニー

- **深層的目的**：子どもが2版を遊び比べられるようにする
- **やらないこと**：選択ページのデザイン変更、新機能追加

```mermaid
flowchart TB
    subgraph BEFORE["Before"]
        direction TB
        B1["子どもが選択ページを開く"]
        B1 --> B2["あそんでみる を押す"]
        B2 --> B_END["play.html が存在しない 404"]
    end

    subgraph AFTER["After"]
        direction TB
        A1["子どもが選択ページを開く"]
        A1 --> A2["あそんでみる を押す"]
        A2 --> A_END["ゲームが始まる"]
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

- index.html（選択ページ）は play.html と play-preview.html にリンクしている
- どちらのファイルも存在しない
- pyxel.html（もとのまま版の実体）は存在する
- pyxel-preview.html（おためし版の実体）は存在しない
- 原因: --preview ビルドが途中で止まった、またはラッパーHTML生成ステップがスキップされた

---

## 2) カスタマージャーニーgherkin（完了条件）

### シナリオ1：もとのままばん でゲームが始まる

> {選択ページが表示されている} で {もとのままばんのあそんでみるを押す} と {ゲームが始まる}

```mermaid
flowchart TD
    A1["選択ページ index.html を開く"] --> A2["もとのままばん のあそんでみるを押す"]
    A2 --> A3["play.html が開く"]
    A3 --> AOK["OK: iframe内でゲームが動く"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    class AOK ok;
```

---

### シナリオ2：おためしばん はリンク切れでも許容する

> {選択ページが表示されている} で {おためしばんのあそんでみるを押す} と {ページが開かないが今は許容}

```mermaid
flowchart TD
    B1["おためしばん のあそんでみるを押す"] --> B2{play-preview.html は存在する?}
    B2 -->|No| BFAIL["OK: 404 今は許容"]
    B2 -->|Yes| BOK["OK: ゲームが動く"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    classDef fail fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef gate fill:#e2e3f1,stroke:#3949ab,color:#000000;
    class B2 gate;
    class BOK ok;
    class BFAIL fail;
```

---

### シナリオ3：通常ビルドが選択ページを壊さない

> {play.html を配置済み} で {通常ビルドを実行} すると {index.html が選択ページのまま維持される}

```mermaid
flowchart TD
    C1["通常ビルドを実行"] --> C2{index.html は選択ページのまま?}
    C2 -->|Yes| COK["OK: 影響なし"]
    C2 -->|No| CFAIL["NG: 選択ページが上書きされた"]

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
        I1["templates/wrapper.html"]
        I2["pyxel.html"]
    end

    subgraph PROCESS["処理"]
        P1["generate_wrapper で\nplay.html を生成"]
    end

    subgraph OUTPUT["アウトプット"]
        O1["play.html"]
    end

    INPUT --> PROCESS --> OUTPUT

    classDef io fill:#e2e3f1,stroke:#3949ab,color:#000000;
    classDef proc fill:#fff3cd,stroke:#856404,color:#000000;
    classDef out fill:#d4edda,stroke:#155724,color:#000000;

    class I1,I2 io;
    class P1 proc;
    class O1 out;
```

### 手順

1. generate_wrapper() を呼んで play.html を生成する
2. Playwrightで index.html → play.html → ゲーム表示を検証

---

## 4) Tasklist

- [x] generate_wrapper() で play.html を生成
- [x] Playwright E2E: index.html → play.html → pyxel.html 全て正常

---

## 5) Discussion（記録・反省）

### 2026年4月12日 21:30（調査・起票）

**Observe**：トップページの play.html / play-preview.html が存在せず404。
**Think**：--preview ビルドが未完走。play.html は generate_wrapper() で生成可能。
**Act**：タスクノート起票。

### 2026年4月12日 21:50（実装・検証完了）

**Observe**：generate_wrapper() で play.html (2988 bytes) 生成。Playwright E2E で index.html → play.html → pyxel.html 全通過。
**Think**：play-preview.html は未対応だが今は許容。通常ビルド時の index.html 上書き問題は残存（別タスク）。
**Act**：play.html 生成・検証完了。

### 反省とルール化

- ビルド生成物が git 管理外のため消える可能性あり。存在チェックをビルドスクリプトに入れるべき
- 残課題：通常ビルド時の index.html 上書き問題（シナリオ3は未対処）
