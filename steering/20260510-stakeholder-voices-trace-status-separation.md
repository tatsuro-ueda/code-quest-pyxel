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
  - traceability
  - status
requirement_ids:
  - req_child_goal_guidance_visible
  - req_scene_transition_polish_deferred
acceptance_ids:
  - acc_child_goal_guidance_visible
  - acc_scene_transition_polish_deferred
stakeholder_ids:
  - st_child_user
  - st_parent_customer
  - st_repo_developer
affected_paths:
  - docs/stakeholder_voices.yml
  - docs/superpowers/plans/2026-05-10-stakeholder-voices-trace-status-separation.md
  - test/test_source_trace_coverage_report.py
  - test/test_stakeholder_voices_checker.py
  - tools/stakeholder_voices/source_trace_coverage.py
  - tools/stakeholder_voices/check_stakeholder_voices.py
  - steering/
verification_refs:
  - python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q
  - python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q
  - python tools/report_source_trace_coverage.py
  - python tools/check_stakeholder_voices.py
done_checks:
  - python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q
  - python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q
  - python tools/report_source_trace_coverage.py
  - python tools/check_stakeholder_voices.py
---

# 2026年5月10日 stakeholder_voices trace status separation

> 状態：⑤ Result（実装完了）
> 実装 plan: [2026-05-10-stakeholder-voices-trace-status-separation.md](/home/exedev/code-quest-pyxel/docs/superpowers/plans/2026-05-10-stakeholder-voices-trace-status-separation.md)

---

## 1) Journey（どこへ行くか）

- **深層的目的**：trace completeness と implementation status を分ける
- **やらないこと**：requirement 全体の status 設計を大改造すること

**Before（現状）**：
- 💦 source trace coverage は `active` の item しか数えない
- 💦 `CJ14` や `CJ19` のような backlog/defer 領域を coverage に乗せるため、status を active backlog に寄せている
- 💦 checker の `source_traceability_integrity` も active 限定なので、later/wont の trace drift を見落とす

**After（達成状態）**：
- ❤️ source trace coverage は trace を持つ `later/wont` item も数える
- ❤️ `source_traceability_integrity` も traced backlog を検査する
- ❤️ `req_child_goal_guidance_visible` と `req_scene_transition_polish_deferred` を `later` に戻しても `total_missing_refs: 0` を維持できる

---

## 2) Gherkin（完了条件）

### シナリオ1：later item でも source trace coverage に入る

🧱 Given：requirement や acceptance が backlog として `later` になっている  
🎬 When：source trace coverage report を作る  
✅ Then：その item の `source_trace_refs` は coverage に含まれる

---

### シナリオ2：later item の trace drift も checker が見つける

🧱 Given：later item に壊れた `source_trace_refs` がある  
🎬 When：checker を実行する  
✅ Then：`source_traceability_integrity` が warning を返す

---

### シナリオ3：implementation-oriented rule は active 限定のまま維持する

🧱 Given：code hint や acceptance verification は実装系の rule である  
🎬 When：trace status separation を入れる  
✅ Then：`requirement_has_code_hints` や `acceptance_has_verification` の active 限定挙動は変わらない

---

### シナリオ4：defer 項目を later に戻しても zero missing を保つ

🧱 Given：`CJ14` と `CJ19` は backlog/defer として扱いたい  
🎬 When：該当 requirement / acceptance を `later` に戻す  
✅ Then：coverage report は `total_missing_refs: 0` のままで、checker は warning 0 を保つ

---

## 3) Design（どうやるか）

- **関連スキル・MCP**：`writing-plans`, `test-driven-development`, `verification-before-completion`
- `source_trace_coverage.py` は `active` 専用 iterator をやめ、trace を数える status 群を明示する
- checker の `source_traceability_integrity` も同じ status 群を使う
- `requirement_has_code_hints` や `acceptance_has_verification` は触らず、trace rule だけ分離する
- 実装後に `req_child_goal_guidance_visible` と `req_scene_transition_polish_deferred` を `later` へ戻して zero missing を確認する

---

## 4) Tasklist

- [x] （CC）`/superpowers:writing-plans` で plan を書き、この note に task 単位で反映する
- [x] （CC）trace status separation 用 red test を追加する
- [x] （CC）coverage/checker の tracked-status 判定を実装する
- [x] （CC）`CJ14/CJ19` を `later` に戻し、zero missing と warning 0 を確認する
- [x] （CC）Result に実装過程、Discussion に結論・懸念・次ノート候補を残す

### 作業記録

#### 2026年5月10日 起票

**Observe**：trace coverage complete は作れたが、そのために backlog item の一部を active に寄せている。  
**Think**：coverage completeness と implementation status を同じ `status` に載せたままだと、今後また似た歪みが出る。  
**Act**：trace status separation 専用 note を起票し、coverage/checker/tooling のみを対象に直す枠を固定した。

---

## 5) Result（成果物）

- `writing-plans` に従って [2026-05-10-stakeholder-voices-trace-status-separation.md](/home/exedev/code-quest-pyxel/docs/superpowers/plans/2026-05-10-stakeholder-voices-trace-status-separation.md) を作成し、`red unit tests -> tooling change -> status restore -> zero-missing verify` の順を固定した。
- red test を 2 本追加した。
  - [test_source_trace_coverage_report.py](/home/exedev/code-quest-pyxel/test/test_source_trace_coverage_report.py) に `test_build_report_counts_later_status_trace_refs`
  - [test_stakeholder_voices_checker.py](/home/exedev/code-quest-pyxel/test/test_stakeholder_voices_checker.py) に `test_run_checker_warns_when_later_requirement_has_missing_source_trace`
- tooling を更新した。
  - [source_trace_coverage.py](/home/exedev/code-quest-pyxel/tools/stakeholder_voices/source_trace_coverage.py) に `TRACKED_TRACE_STATUSES = {"active", "later", "wont"}` を導入し、coverage 集計を active 専用から tracked-status へ切り替えた
  - [check_stakeholder_voices.py](/home/exedev/code-quest-pyxel/tools/stakeholder_voices/check_stakeholder_voices.py) の `source_traceability_integrity` も同じ tracked-status 群を使うようにした
- implementation-oriented rule は触らなかった。
  - `requirement_has_code_hints` と `acceptance_has_verification` は引き続き active item のみを対象にしている
- [stakeholder_voices.yml](/home/exedev/code-quest-pyxel/docs/stakeholder_voices.yml) では `req_child_goal_guidance_visible`, `acc_child_goal_guidance_visible`, `req_scene_transition_polish_deferred`, `acc_scene_transition_polish_deferred` を `later` へ戻した
- CoVe:
  - シナリオ1 `later item でも source trace coverage に入る`: `test_build_report_counts_later_status_trace_refs` が通り、later requirement の `CJ14` が report に含まれて達成。
  - シナリオ2 `later item の trace drift も checker が見つける`: `test_run_checker_warns_when_later_requirement_has_missing_source_trace` が通り、source trace checker が later item も見ることを確認して達成。
  - シナリオ3 `implementation-oriented rule は active 限定のまま維持する`: real repo の checker は `warning_rules: 0` のまま、既存 rule count も変えず達成。
  - シナリオ4 `defer 項目を later に戻しても zero missing を保つ`: `total_missing_refs: 0` を維持したまま `CJ14/CJ19` を later に戻せたので達成。
- focused verify:
  - `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py -q` -> `24 passed`
- full stakeholder verify:
  - `python -m pytest test/test_source_trace_coverage_report.py test/test_stakeholder_voices_checker.py test/test_fix_stakeholder_voices.py test/test_repair_stakeholder_voices.py -q` -> `29 passed`
  - `python tools/report_source_trace_coverage.py` -> `status: OK`, `total_missing_refs: 0`
  - `python tools/check_stakeholder_voices.py` -> `warning_rules: 0`

---

## 6) Discussion（反省）

- 結論：trace completeness は implementation status から切り離せた。これで backlog/defer item を active に寄せなくても source migration 完了を示せる。
- 結論：`source_traceability_integrity` も tracked-status を見るようになったので、later/wont の trace drift を今後は見落とさない。
- 懸念：現状の tracked statuses はコード定数に固定した。将来 `archived` や `draft` をどう扱うかは明文化していない。
- 懸念：coverage complete になったことで、次は「どの requirement が実装済みか」を別軸で見たくなる。status だけでは混ざりやすいので、implementation status 専用の field を検討してもよい。
- 次に起票すべき task note 1：`stakeholder_voices.yml` から implementation status dashboard を生成する note
- 次に起票すべき task note 2：task note frontmatter の `requirement_ids` から `verification_refs` と `source_trace_refs` を自動補完する note

---

### 反省とルール化

- 次にやること：implementation status 専用の見える化 note を切る
