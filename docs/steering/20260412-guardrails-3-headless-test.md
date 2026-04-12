---
status: open
priority: high
scheduled: 2026-04-12
dateCreated: 2026-04-12
dateModified: 2026-04-12
tags:
  - guardrails
  - testing
  - headless
---

# ガードレール(3) ヘッドレステスト基盤

## 深層的目的

壊れた版を子どもに届けない最後の防壁。

## 対象ガードレール

G8, G9

---

## 1. Journey

```mermaid
flowchart TB
  classDef bad fill:#fcc,stroke:#c33
  classDef good fill:#cfc,stroke:#3c3

  subgraph Before
    B1[AIがmain.py編集]
    B2[make buildで構文チェックのみ]
    B3[起動クラッシュが子どもに届く]
    B1 --> B2 --> B3
  end
  class B3 bad

  subgraph After
    A1[AIがmain.py編集]
    A2[make buildでヘッドレス起動+4シナリオ走破]
    A3[壊れた版は承認キューに出ない]
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
