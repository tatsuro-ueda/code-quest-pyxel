---
status: open
priority: high
scheduled: 2026-04-12
dateCreated: 2026-04-12
dateModified: 2026-04-12
tags:
  - guardrails
  - hooks
---

# ガードレール(2) Hooks設計・実装

## 深層的目的

AIが壊せるパスを物理的に封じる。

## やらないこと

- SSoT基盤の構築（タスク1で完了済み）
- ビルドパイプライン（タスク3）

## 対象ガードレール

G1, G2, G3, G5, G7, G14

## 依存

タスク1（完了済み）の後

## 方針

- hook スコープは `.claude/settings.json`（共有）
- デバッグ用バイパス `CLAUDE_GUARD_BYPASS=1`

---

## 1. Journey

```mermaid
flowchart TB
  classDef bad fill:#fcc,stroke:#c33
  classDef good fill:#cfc,stroke:#3c3

  subgraph Before
    B1[AIがsrc/generated/spells.pyを直接編集]
    B2[普通に編集できてしまう]
    B3[SSoTとの乖離]
    B1 --> B2 --> B3
  end
  class B3 bad

  subgraph After
    A1[AIがsrc/generated/spells.pyを編集しようとする]
    A2[PreToolUse hookが拒否]
    A3["「YAMLを編集してください」と誘導"]
    A4[正しいパスに誘導]
    A1 --> A2 --> A3 --> A4
  end
  class A4 good
```

## 2. Gherkin

_(Journey承認後に記入)_

## 3. Design

_(Journey承認後に記入)_

## 4. Tasklist

_(Journey承認後に記入)_

## 5. Discussion

- 2026-04-12 起票
