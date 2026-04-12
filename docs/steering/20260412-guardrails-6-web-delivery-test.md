---
status: open
priority: medium
scheduled: 2026-04-12
dateCreated: 2026-04-12
dateModified: 2026-04-12
tags:
  - guardrails
  - web
  - delivery
---

# ガードレール(6) Web配信テスト

## 深層的目的

ローカルで動いてもWeb版で動かない問題を防ぐ。

## 対象ガードレール

G11, G12

---

## 1. Journey

```mermaid
flowchart TB
  classDef bad fill:#fcc,stroke:#c33
  classDef good fill:#cfc,stroke:#3c3

  subgraph Before
    B1[AIがセーブ/ロード変更]
    B2[ローカルPythonでは動く]
    B3[Web版でセーブできない]
    B1 --> B2 --> B3
  end
  class B3 bad

  subgraph After
    A1[AIがセーブ/ロード変更]
    A2[make buildでemscripten環境テスト]
    A3[Web版で動かない版は承認キューに出ない]
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
