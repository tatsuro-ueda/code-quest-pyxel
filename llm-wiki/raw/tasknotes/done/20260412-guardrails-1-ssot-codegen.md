---
status: done
priority: high
scheduled: 2026-04-12
dateCreated: 2026-04-12
dateModified: 2026-04-12
tags:
  - guardrails
  - ssot
  - codegen
---

# ガードレール(1) SSoT + Codegen基盤

## 深層的目的

データ散在による不整合を構造的に防ぐ。

## やらないこと

- Hooks実装（別タスク: ガードレール(2)）

## 対象ガードレール

G1, G3, G13

## 完了コミット

df015fa

---

## 1. 改善対象ジャーニー

```mermaid
flowchart TB
  classDef bad fill:#fcc,stroke:#c33
  classDef good fill:#cfc,stroke:#3c3

  subgraph Before
    B1[AIが呪文追加]
    B2[main.py内の複数辞書を手動で全部更新]
    B3[1箇所更新漏れ]
    B4[KeyError]
    B1 --> B2 --> B3 --> B4
  end
  class B4 bad

  subgraph After
    A1[AIが呪文追加]
    A2[assets/spells.yamlを1箇所編集]
    A3[gen_spells.pyが自動生成]
    A4[全参照が自動で一貫更新]
    A1 --> A2 --> A3 --> A4
  end
  class A4 good
```

## 2. カスタマージャーニーgherkin

1. YAML編集 → gen実行 → src/generated/ にPythonファイル生成される
2. make gen で全データ種別を一括生成できる
3. YAML構文エラー時は gen がエラーメッセージを出して失敗する
4. 移行後もゲームの挙動が移行前と同一である
5. 派生データ（ショップ品揃え等）がYAML定義と整合している

## 3. Design

```
assets/*.yaml (6種: spells, items, weapons, armors, enemies, shops)
  ↓
tools/gen_data.py
  ↓
src/generated/*.py
  ↓
src/game_data.py (ローダ)
  ↓
main.py (sync)

Makefile に gen / build ターゲット追加
```

## 4. Tasklist

- [x] assets/ に YAML 6種を配置
- [x] tools/gen_data.py 作成
- [x] src/generated/ ディレクトリ作成
- [x] spells 生成確認
- [x] items / weapons / armors 生成確認
- [x] enemies 生成確認
- [x] shops 生成確認
- [x] src/game_data.py ローダ作成
- [x] Makefile gen / build ターゲット追加

## 5. Discussion

- 2026-04-12 起票: SSoT + Codegen基盤の必要性を整理
- 2026-04-12 改善対象ジャーニー承認 → カスタマージャーニーgherkin記入
- 2026-04-12 実装完了 (df015fa)
