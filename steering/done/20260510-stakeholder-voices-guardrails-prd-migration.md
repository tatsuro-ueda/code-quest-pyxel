---
status: done
priority: normal
scheduled: 2026-05-10T00:00:00.000+09:00
dateCreated: 2026-05-10T00:00:00.000+09:00
dateModified: 2026-05-10T00:00:00.000+09:00
tags:
  - task
  - docs
  - yaml
  - stakeholder
  - guardrails
  - migration
requirement_ids:
  - req_safe_architecture_boundaries
  - req_no_silent_failure
  - req_dist_is_not_source
acceptance_ids:
  - acc_safe_architecture_boundaries_guard
  - acc_no_silent_failure_gates
  - acc_dist_is_not_source_build_path
stakeholder_ids:
  - st_child_user
  - st_parent_customer
  - st_repo_developer
  - st_coding_ai
  - st_product_executive
affected_paths:
  - docs/product-requirements-guardrails.md
  - docs/stakeholder_voices.yml
  - docs/superpowers/plans/2026-05-10-stakeholder-voices-guardrails-prd-migration.md
  - test/test_source_trace_coverage_report.py
  - test/test_stakeholder_voices_checker.py
  - test/test_fix_stakeholder_voices.py
  - test/test_repair_stakeholder_voices.py
  - tools/check_stakeholder_voices.py
  - tools/report_source_trace_coverage.py
  - steering/
verification_refs:
  - python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q
  - python tools/report_source_trace_coverage.py
  - python tools/check_stakeholder_voices.py
done_checks:
  - python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q
  - python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q
  - python tools/report_source_trace_coverage.py
  - python tools/check_stakeholder_voices.py
---

# 2026年5月10日 stakeholder_voices guardrails PRD migration

> 状態：⑤ Result（実装完了）
> 実装 plan: [2026-05-10-stakeholder-voices-guardrails-prd-migration.md](/home/exedev/code-quest-pyxel/docs/superpowers/plans/2026-05-10-stakeholder-voices-guardrails-prd-migration.md)

---

## 1) Journey（どこへ行くか）

- **深層的目的**：guardrails PRD の未移植領域を stakeholder voices に取り込む
- **やらないこと**：残り journeys 全体まで同じ note で抱え込むこと

**Before（現状）**：
- 💦 coverage report で `product_requirements_guardrails` は `CJG36/CJG38/CJG39/CJG40/CJG44` が missing のまま残っている
- 💦 データ SSoT、イベント追加安全性、システム変更安全性、セーブ互換、大きすぎる複雑さの抑制は docs にあるが、task note 起票や checker の根拠として機械参照しづらい
- 💦 `CJ35/CJG35`, `CJ37/CJG37`, `CJ41/CJG41` だけ先に stakeholder voices 化されているため、guardrails の coverage が途中で止まっている

**After（達成状態）**：
- ❤️ `CJG36/CJG38/CJG39/CJG40/CJG44` が stakeholder voices の requirement / acceptance へ移植される
- ❤️ coverage report で `product_requirements_guardrails` の missing refs が 0 になる
- ❤️ guardrails 系 task note が `doc_id:stable_ref` ベースで起票できる

---

## 2) Gherkin（完了条件）

### シナリオ1：guardrails PRD の残り 5 項目を stakeholder voices から辿れる

🧱 Given：AI や開発者が guardrails 系 task note を起票したい  
🎬 When：`stakeholder_voices.yml` と coverage report を見る  
✅ Then：`CJG36/CJG38/CJG39/CJG40/CJG44` に対応する requirement / acceptance を機械的に辿れる

---

### シナリオ2：SSoT と safety gate の体験が acceptance に落ちている

🧱 Given：guardrails PRD には SSoT、イベント追加安全性、システム変更安全性、セーブ互換、複雑さ削減の約束がある  
🎬 When：stakeholder voices に移植する  
✅ Then：親と AI が何を変え、どこで止まり、子どもに何を見せないかが acceptance で表現される

---

### シナリオ3：coverage report が guardrails docs の進捗改善を示す

🧱 Given：移植前は `product_requirements_guardrails` に 5 件の missing がある  
🎬 When：移植後に coverage report を実行する  
✅ Then：`product_requirements_guardrails` の referenced refs が 8 件すべてそろい、missing refs が空になる

---

### シナリオ4：checker と task note contract を壊さない

🧱 Given：`stakeholder_voices.yml` と task note frontmatter は deterministic checker で検査される  
🎬 When：guardrails 系 requirement / acceptance を追加する  
✅ Then：`python tools/check_stakeholder_voices.py` は warning 0 のまま通る

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：`writing-plans`, `test-driven-development`, `verification-before-completion`
- 既存の `CJG35/CJG37/CJG41` requirement はそのまま維持し、残り 5 件だけを新設 requirement / acceptance で埋める
- `source_trace_refs` は `product_requirements_guardrails:CJGxx` と `customer_journeys:CJxx` を併記し、guardrails PRD と journey の両側から trace できるようにする
- 実装順は `1. rule 先行 2. deterministic check へ昇格 3. guardian は安全な正規化だけ` を守る

```mermaid
flowchart TD
    subgraph INPUT[インプット]
        I1[product requirements guardrails CJG36 CJG38 CJG39 CJG40 CJG44]
        I2[customer journeys CJ36 CJ38 CJ39 CJ40 CJ44]
        I3[existing stakeholder voices and coverage report]
    end

    subgraph PROCESS[処理 変換]
        P1[red coverage expectations]
        P2[guardrails requirements migration]
        P3[guardrails acceptance migration]
        P4[checker and coverage verification]
    end

    subgraph OUTPUT[アウトプット]
        O1[guardrails requirements in stakeholder voices]
        O2[guardrails acceptance in stakeholder voices]
        O3[reduced guardrails missing refs]
    end

    INPUT --> PROCESS --> OUTPUT

    classDef io fill:#e2e3f1,stroke:#3949ab,color:#000000;
    classDef proc fill:#fff3cd,stroke:#856404,color:#000000;
    classDef out fill:#d4edda,stroke:#155724,color:#000000;

    class I1,I2,I3 io;
    class P1,P2,P3,P4 proc;
    class O1,O2,O3 out;
```

```mermaid
flowchart TD
    D1[guardrails migration note 起票] --> D2[plan and red tests]
    D2 --> D3[requirements and acceptance migration]
    D3 --> D4[checker and coverage verification]
    D4 --> C1{CoVe:<br>Gherkin 1 と 2 を満たすか}
    C1 -->|No| D3
    C1 --> C2{CoVe:<br>Gherkin 3 と 4 を満たすか}
    C2 -->|No| D4
    C2 -->|Yes| DONE[完了]

    classDef cove fill:#fff3cd,stroke:#856404,color:#000000;
    classDef done fill:#d4edda,stroke:#155724,color:#000000;

    class C1,C2 cove;
    class DONE done;
```

---

## 4) Tasklist

```mermaid
flowchart TD
    T1[CC が writing-plans で詳細 plan を書く] --> C1{CoVe<br>guardrails 5 項目を全部支えられるか}
    C1 -->|No| T1
    C1 -->|Yes| T2[red test を追加]
    T2 --> C2{CoVe<br>missing guardrails trace を観測できるか}
    C2 -->|No| T2
    C2 -->|Yes| T3[requirements acceptance を移植]
    T3 --> C3{CoVe<br>coverage と checker が改善したか}
    C3 -->|No| T3
    C3 -->|Yes| DONE[✓ 完了]

    classDef done fill:#d4edda,stroke:#155724,color:#000000;
    classDef cove fill:#fff3cd,stroke:#856404,color:#000000;

    class DONE done;
    class C1,C2,C3 cove;
```

> 必ず上から順に実施。CCがCoVeで自力検証しながら進める。

- [x] （CC）`/superpowers:writing-plans` で plan を書き、この note に task 単位で反映する
  plan: [2026-05-10-stakeholder-voices-guardrails-prd-migration.md](/home/exedev/code-quest-pyxel/docs/superpowers/plans/2026-05-10-stakeholder-voices-guardrails-prd-migration.md)
- [x] （CC）guardrails migration 用 red test を追加する
- [x] （CC）`CJG36/CJG38/CJG39/CJG40/CJG44` を stakeholder voices に移植する
- [x] （CC）coverage report と checker の改善を確認する
- [x] （CC）Result に実装過程、Discussion に結論・懸念・次ノート候補を残す

### 作業記録

#### 2026年5月10日 起票

**Observe**：coverage report で `product_requirements_guardrails` は 5 件の missing が残っており、next slice として独立させやすい。  
**Think**：`CJG35/CJG37/CJG41` はすでに stakeholder voices 化されているので、残り 5 件だけを新設で埋める方が trace が読みやすい。  
**Act**：guardrails PRD migration 専用の task note を起票し、Journey / Gherkin / Design / Tasklist に `CJG36/CJG38/CJG39/CJG40/CJG44` 移植の作業枠を固定した。

---

## 5) Result（成果物）

- `writing-plans` に従って [2026-05-10-stakeholder-voices-guardrails-prd-migration.md](/home/exedev/code-quest-pyxel/docs/superpowers/plans/2026-05-10-stakeholder-voices-guardrails-prd-migration.md) を作成し、`coverage red -> YAML migration -> checker/report verify` の順に実装計画を固定した。
- red test として [test_source_trace_coverage_report.py](/home/exedev/code-quest-pyxel/test/test_source_trace_coverage_report.py) に `product_requirements_guardrails` の `referenced_refs == CJG35/CJG36/CJG37/CJG38/CJG39/CJG40/CJG41/CJG44` と `missing_refs == []` を追加し、[test_stakeholder_voices_checker.py](/home/exedev/code-quest-pyxel/test/test_stakeholder_voices_checker.py) に real repo の requirement / acceptance 数が 30 以上になる期待を追加した。移植前は guardrails coverage に 5 件の missing があり、`requirements == 25` で red だった。
- [stakeholder_voices.yml](/home/exedev/code-quest-pyxel/docs/stakeholder_voices.yml) に guardrails 系 requirement 5 件と acceptance 5 件を追加した。
  - requirements: `req_data_ssot_consistency`, `req_event_change_safe`, `req_system_change_scenario_guard`, `req_mode_change_save_compat`, `req_simplicity_enables_change_speed`
  - acceptance: `acc_data_ssot_consistency_regen`, `acc_event_change_safe_walkthrough`, `acc_system_change_scenario_guard`, `acc_mode_change_save_compat`, `acc_simplicity_enables_change_speed`
- 既存の `CJG35/CJG37/CJG41` requirement はそのまま維持し、残り 5 件だけを新設した。これで guardrails PRD の coverage が途中で分断されず、layer ごとの責務も読みやすくなった。
- `source_trace_refs` は 5 件すべてで `customer_journeys:CJ36/CJ38/CJ39/CJ40/CJ44` と `product_requirements_guardrails:CJG36/CJG38/CJG39/CJG40/CJG44` を持つため、guardrails PRD と journeys の両側から trace できる。
- CoVe:
  - シナリオ1 `guardrails PRD の残り 5 項目を stakeholder voices から辿れる`: coverage report で `product_requirements_guardrails` の `referenced_refs` が 8 件すべてそろい達成。
  - シナリオ2 `SSoT と safety gate の体験が acceptance に落ちている`: SSoT、一貫生成、イベント追加安全性、システム変更 safety gate、save 互換、複雑さ抑制を 5 requirement / 5 acceptance に分離して達成。
  - シナリオ3 `coverage report が guardrails docs の進捗改善を示す`: `product_requirements_guardrails` は `5 missing` から `0 missing` へ改善し達成。
  - シナリオ4 `checker と task note contract を壊さない`: `python tools/check_stakeholder_voices.py` は `warning_rules: 0` を維持し達成。
- focused verify:
  - `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q` -> `18 passed`
- full stakeholder verify:
  - `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q` -> `23 passed`
  - `python tools/report_source_trace_coverage.py`
  - `python tools/check_stakeholder_voices.py`

---

## 6) Discussion（反省）

- 結論：guardrails の残り 5 件は既存 request にぶら下げるだけで十分整理できた。新しい stakeholder type や request は不要だった。
- 結論：この slice は manual verification に逃げず、すべて deterministic proof で閉じられた。guardrails 領域はその方が設計意図に合っている。
- 懸念：`customer_journeys` の missing は `12` まで減ったが、これ以降は PRD ではなく theme 単位の束ね直しが必要になる。docs の粒度が stakeholder voices より細かいので、1 journey = 1 requirement に寄せすぎると逆に読みにくくなる。
- 懸念：`customer_jobs` もまだ `3 missing` 残っている。journey だけでなく job root とのつながりをどう補うかを次の設計で決める必要がある。
- 次に起票すべき task note 1：`customer_journeys` の残り missing 12 件を theme ごとに束ねる note
- 次に起票すべき task note 2：`customer_jobs` の `JOB:JIS_PARENT_AUTONOMY`, `JOB:JPL_CHILD_PLAYER`, `JOB:JSC_PARENT_GROWTH` を stakeholder voices に移植する note

---

### 反省とルール化

- 次にやること：journeys remaining themes note を起票し、`customer_journeys 12 missing` を次の red にする
