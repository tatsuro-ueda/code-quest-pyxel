---
status: open
priority: medium
scheduled: 2026-04-12
dateCreated: 2026-04-12
dateModified: 2026-04-12
tags:
  - guardrails
  - pyxres
  - validation
---

# ガードレール(4) pyxres整合チェック

## 深層的目的

pyxresとコード定数の乖離を自動検出する。

## 対象ガードレール

G4, G6

---

## 1. Journey

```mermaid
flowchart TB
  classDef bad fill:#fcc,stroke:#c33
  classDef good fill:#cfc,stroke:#3c3

  subgraph Before
    B1[AIがTILE_DATAにタイル追加]
    B2[起動時に自己修復]
    B3[修復できない場合は見えない壁]
    B1 --> B2 --> B3
  end
  class B3 bad

  subgraph After
    A1[AIがTILE_DATAにタイル追加]
    A2[make buildでvalidate_resources.pyが検証]
    A3[不一致ならビルド失敗+座標差分表示]
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
