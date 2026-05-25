---
status: active
created: 2026-05-25
question_type: synthesis
asker: tatsuro
sources:
  - ../areas/single-source-of-truth-and-golden-path.md
  - ../areas/no-silent-failure-and-migration-safety.md
  - ../areas/guardrail-layering-and-ai-change-boundaries.md
  - ../areas/view-presenter-model-boundaries.md
  - ../summaries/knowledge/framework-rule-summary.md
---

# 2026年5月25日（tatsuro）docs/framework-rule.md に追加/削除はあるか

## Question

`docs/framework-rule.md` に追加したり削除したりすることある？

## Answer

採用 5 件を反映済み（追加 4 件 + 削除 1 件）。

### 追加 4 件

1. **M4-2 SfxSystem / ImageBanks**：Code Maker 由来の imported audio / image bank は runtime self-heal で巻き戻さず truth として尊重する、を明記
2. **M5-2 テスト優先順位**：`tools/test_headless.py`（headless 起動 gate）を 5 番目に追加（旧 5 番「Pyxel 実機確認」は 6 番へ）
3. **M5-3 新節「物理 guardrail（hook と AI session 設定）」**：`tools/hooks/*.sh` と `.claude/settings.json` を 2 系統 guardrail entrypoint として明記
4. **M5-3 新節「AI 自身が規約を見て自己矯正する compliance loop」**：AGENTS.md が周期的に AI 行動を矯正する役割を明示

### 削除 1 件

5. **付録「Phase 1.5 では…進める順序」を削除**：Phase 3 / M4-3 / M4-4 完了済みで古い

### 不採用 1 件

- 候補 4: `architecture_rules.yml` + checker/guardian を M5 に追加 → **PR レビューチェックリストの方が効くため framework-rule への追記は不採用**

## Evidence

- `wiki/areas/guardrail-layering-and-ai-change-boundaries.md`: 「imported Sound / Music / SFX を fixed definition で再初期化しないことは authoring と playback selection の境界を守る guardrail」「`.claude/settings.json` と `tools/hooks/*.sh` は wrong-path edit を最初に止める物理バリア」「`tools/test_headless.py` は import / 初期化 / 1 フレーム描画の失敗を build gate で止める最後のバリア」「autonomous compliance loop は AGENTS.md に M1〜M5 サマリを足した」
- `wiki/areas/single-source-of-truth-and-golden-path.md`: 「`.pyxres` の truth は runtime self-heal に置かず Code Maker 側の実体と build / verify 側の検査で守る」
- `wiki/areas/no-silent-failure-and-migration-safety.md`: 「stakeholder coverage report, trace-status separation, and deterministic boundary promotions reduced the chance that missing docs traceability or stale status handling quietly passes as healthy」
- `docs/framework-rule.md` 現状 (2026-05-25 反映前): M4-2 SfxSystem は「空 slot のみ fallback」までで imported との関係は不明示、M5-2 は 5 段階優先順位だが headless test が抜け、M5-3 に hook / AGENTS.md compliance loop への言及無し、付録「進める順序」は Phase 1.5 時点の記述

## Compared Pages

- `../areas/single-source-of-truth-and-golden-path.md`
- `../areas/no-silent-failure-and-migration-safety.md`
- `../areas/guardrail-layering-and-ai-change-boundaries.md`
- `../areas/view-presenter-model-boundaries.md`
- `../summaries/knowledge/framework-rule-summary.md`
- `../../../docs/framework-rule.md`

## Confidence

Medium. 追加候補は複数 area で言及されており確度高い。削除候補は履歴判断でユーザー依存 (Medium)。

## Decision Notes

候補 4（`architecture_rules.yml` + checker/guardian を M5 に追加）を不採用とした判断は重要:

- machine-readable な検証ツールチェーンの存在を **規約本体（framework-rule.md）** に書くか、それとも **運用フロー（PR レビューチェックリスト等）** に書くかは別問題
- 規範文書は「何をすべきか／してはいけないか」を述べる場で、ツールチェーンの実在は運用面で抑えるべき
- 逆流フローでは候補をそのまま全部 docs に流し込まず、適切な「居場所」を考えてから採用する必要がある

この decision は将来、他の docs/ への逆流フローでも「規範 vs 運用」の線引きの判断材料になる。
