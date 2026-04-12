---
status: open
priority: high
scheduled: 2026-04-12T23:57:09.000+0900
dateCreated: 2026-04-12T23:57:09.000+0900
dateModified: 2026-04-12T23:57:09.000+0900
tags:
  - task
  - j38
  - preview
  - build
---

# 2026年4月12日 J38 preview build を current に混ぜない

> 状態：(1) Journey
> 次のゲート：（ユーザー）Gherkin へ進むか確認

---

## 1) Journey（どこへ行くか）

- **深層的目的**：比較導線を守る
- **やらないこと**：今日中に承認UI全体を作り直すこと、配信方式まで広げて直すこと

```mermaid
flowchart TB
    subgraph BEFORE["Before（現状）"]
        direction TB
        B1["親が変更をビルドする"]
        B1 --> B2["通常 build が pyxel.html を更新する"]
        B2 --> B_END["もとのままばんに変更が混ざり、J31 の遊び比べが崩れる"]
    end

    subgraph AFTER["After（達成状態）"]
        direction TB
        A1["親が変更をビルドする"]
        A1 --> A2["変更は pyxel-preview.html 側にだけ出る"]
        A2 --> A_END["子どもが current / preview を遊び比べてから承認できる"]
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

### 現状

- `docs/gherkins/gherkin-platform.md` の J31/J32 では、変更確認は `pyxel-preview.html` 側で行う前提になっている
- しかし現在の通常 build は `pyxel.html` / `pyxel.pyxapp` を直接更新するので、変更が current 側へ混ざる
- 今回は応急処置として preview 側へファイルを退避したが、次に `make build` を実行するとまた current 側へ出る

### 今回の方針

- preview build と current build の役割をコード上ではっきり分ける
- AI に変更を頼んだときは preview 側にだけ成果物が出る流れを先に守る
- 承認後にだけ current 側へ昇格する流れを、J31/J32 の仕様どおりに整理する

### 委任度

- 🟡 CC主導で実装は進められるが、最終判断として「通常 build を current 用に残すか」「preview build を別入口にするか」の整理が必要

---

## 2) Gherkin（完了条件）

### シナリオ1：正常系（〜が成功する）

> {前提条件} で {操作} すると {期待結果}

```mermaid
flowchart TD
    A1[操作] --> A2[処理]
    A2 --> AOK["✓ 期待結果"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    class AOK ok;
```

---

### シナリオ2：異常系（〜が失敗するケース）

> {前提条件} で {異常な操作} すると {エラーが返り副作用がない}

```mermaid
flowchart TD
    B1[操作] --> B2{判定}
    B2 -->|OK| BOK["✓ 正常"]
    B2 -->|NG| BFAIL["✓ エラーが返る"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    classDef fail fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef gate fill:#e2e3f1,stroke:#3949ab,color:#000000;
    class B2 gate;
    class BOK ok;
    class BFAIL fail;
```

---

### シナリオ3：リスク確認（〜に悪影響がない）

> {変更適用済み} で {影響範囲を確認} すると {既存の動作が維持されている}

```mermaid
flowchart TD
    C1[影響範囲を確認] --> C2{既存動作が維持?}
    C2 -->|Yes| COK["✓ 影響なし"]
    C2 -->|No| CFAIL["⚠ 悪影響あり"]

    classDef ok fill:#d4edda,stroke:#155724,color:#000000;
    classDef fail fill:#f8d7da,stroke:#721c24,color:#000000;
    classDef gate fill:#e2e3f1,stroke:#3949ab,color:#000000;
    class C2 gate;
    class COK ok;
    class CFAIL fail;
```

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：（余計なものをロードしない）

```mermaid
flowchart LR
    subgraph INPUT["インプット"]
        I1[〜]
        I2[〜]
    end

    subgraph PROCESS["処理・変換"]
        P1[〜]
        P2[〜]
    end

    subgraph OUTPUT["アウトプット"]
        O1[〜]
    end

    INPUT --> PROCESS --> OUTPUT

    classDef io fill:#e2e3f1,stroke:#3949ab,color:#000000;
    classDef proc fill:#fff3cd,stroke:#856404,color:#000000;
    classDef out fill:#d4edda,stroke:#155724,color:#000000;

    class I1,I2 io;
    class P1,P2 proc;
    class O1 out;
```

```mermaid
flowchart TD
    D1[① Journey確認] --> D2[② Gherkin承認]
    D2 -->|ゲート1: ユーザー| D3[③ Design・計画]
    D3 --> D4[④ Tasklist実行]
    D4 -->|ゲート2: ユーザー| D5[⑤ 検証]
    D5 -->|ゲート3: ユーザー| D6[反省・ルール化]
    D5 -->|Gherkinに不足| D4

    classDef gate fill:#e2e3f1,stroke:#3949ab;
    classDef done fill:#d4edda,stroke:#155724;

    class D2,D4,D5 gate;
    class D6 done;
```

---

## 4) Tasklist

```mermaid
flowchart TD
    T2["（CC）計画立案\n/superpowers:writing-plans"]
    T2 --> T2C{"CoVe:\nGherkinを全て満たせるか?"}
    T2C -->|NG| T2
    T2C -->|OK| T4["（CC）1ステップ実行\n→ Discussion記録 → Gherkinチェック"]
    T4 --> T4C{"CoVe:\n期待通りか?"}
    T4C -->|NG| T4
    T4C -->|OK| T5{全ステップ完了?}
    T5 -->|No| T4
    T5 -->|Yes| T7["（CC）まとめ"]
    T7 --> T7C{"CoVe:\n全Gherkin満たされているか?"}
    T7C -->|NG| T4
    T7C -->|OK| DONE[✓ 完了]

    classDef done fill:#d4edda,stroke:#155724,color:#000000;
    classDef cove fill:#fff3cd,stroke:#856404,color:#000000;

    class DONE done;
    class T2C,T4C,T7C cove;
```

> 必ず上から順に実施。CCがCoVeで自力検証しながら進める。

- [ ] （CC）`/superpowers:writing-plans` で計画を立てる（このセクションに記入）
- [ ] （CC）作業を1ステップ実行 → **5) Discussion に記録** → Gherkinチェック → 次へ
- [ ] （CC）作業結果をまとめ、全Gherkinを満たしているかCoVeで検証

---

## 5) Discussion（記録・反省）

> Observe → Think → Act を刻む。未来の自分が復元できることが目的。

### 2026年4月12日 23:57（起票）

**Observe**：通常 build を実行すると変更済み成果物が `pyxel.html` 側へ出てしまい、J31 の「おためしばんで確認してから承認する」流れとずれていた。今回は時間優先で preview 側へファイルを退避して応急対応した。
**Think**：問題は「ファイル名」より「build の責務分離」にある。preview build の入口と current build の入口を整理し、承認前の変更が current 側へ混ざらないようにする必要がある。
**Act**：preview build 導線の根本修正タスクとして J38 を起票した。

### 2026年4月13日 00:02（close-session 中断メモ）

**Observe**：セッション終了前の時点で、preview 側への応急退避は完了しているが、根本の build 導線修正は未着手。`index.html` のおためし版説明文は当面の文言に差し替え済み。
**Think**：次回は J38 の `Gherkin` から再開し、`make build` / `--preview` / `--promote` の責務分離を仕様に沿って整理するのが最短。
**Act**：再開ポイントをノートに追記した。

---

### 反省とルール化

- 記入先：observe-situation / manage-tasknotes / CLAUDE.md
- 次にやること：
