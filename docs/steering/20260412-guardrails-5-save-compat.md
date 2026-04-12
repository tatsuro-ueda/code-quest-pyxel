---
status: open
priority: medium
scheduled: 2026-04-12
dateCreated: 2026-04-12
dateModified: 2026-04-12
tags:
  - guardrails
  - save
  - compatibility
---

# ガードレール(5) セーブ互換テスト

## 深層的目的

「ぼくのデータなくなった」を防ぐ。

## 対象ガードレール

G10

---

## 1. Journey

```mermaid
flowchart TB
  classDef bad fill:#fcc,stroke:#c33
  classDef good fill:#cfc,stroke:#3c3

  subgraph Before
    B1[AIがPlayerSnapshotのフィールド変更]
    B2[ロードテストなし]
    B3[子どものデータが消える]
    B1 --> B2 --> B3
  end
  class B3 bad

  subgraph After
    A1[AIがPlayerSnapshotのフィールド変更]
    A2[make buildでテスト用セーブデータのロードテスト]
    A3[互換性のない版は承認キューに出ない]
    A1 --> A2 --> A3
  end
  class A3 good
```

## 2. Gherkin

_(Journey承認後に記入)_

## 3. Design

_(Journey承認後に記入)_

## 4. Tasklist

_(Journey承認後に記入)_

## 5. Discussion

- 2026-04-12 起票
