---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/knowledge/product-requirements-guardrails-summary.md
  - ../summaries/knowledge/repository-structure-summary.md
  - ../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md
  - ../summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j36-dialogue-ssot-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-3-headless-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation-summary.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/knowledge/docs/product-requirements-guardrails.md
  - ../../raw/knowledge/docs/repository-structure.md
  - ../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
  - ../../raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md
  - ../../raw/tasknotes/steering/done/20260412-j36-dialogue-ssot.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md
---

# Single Source Of Truth And Golden Path

## 核心

`framework-rule` は、AI が壊しやすい場所を「正本を一つにする」と「本番の通り道を通す」で先に封じる。データの正しい置き場と、実際のユーザー導線を固定しておけば、見かけだけの green を減らせる。

## SSoT

- 同じ意味のデータを複数箇所に持たない
- 生データ直読みや都合のよい参照先切り替えをしない
- ユーザー編集より自動生成を優先しない
- `src/` と `assets/` を正本にし、 `dist/` を source 扱いしない
- `assets/*.yaml -> tools/gen_data.py -> src/generated/*.py -> src/game_data.py` の一方向生成を守り、手動多重更新より regenerate を優先する
- dialogue も `assets/dialogue.yaml -> tools/gen_data.py -> src/generated/dialogue.py -> src/game_data.py` の一方向へ寄せ、`src/dialogue_data.py` は互換レイヤーにとどめる
- `.pyxres` の truth は runtime self-heal に置かず、Code Maker 側の実体と build / verify 側の検査で守る

## Golden Path

- unit test green だけで終わらない
- 起動、メニュー、戦闘、配布物など本番導線を最低 1 回は通す
- bundle や実物確認を後回しにしない
- Code Maker zip、公開 URL、play log のような user-facing artifact も通り道に含める
- Code Maker 向け zip では、zip 内 `main.py` と `my_resource.pyxres` が現行正本と一致し、展開物が headless 起動することまで確かめる
- build gate では構文 green だけでなく、headless 起動で `Game()` 初期化と 1 フレーム描画が通ることを最低条件にする

## この repo への含意

- docs、pyxres、配布物、save payload のどれが正本かを先に固定する
- 「直した」ではなく「ユーザーが触る通り道で動いた」ことを done とみなす
- generated data や packaging artifact も、`正本から再現できるか` で点検する
- resource mismatch を startup self-repair に任せず、verify で止める方が current truth と相性が良い
- `main.py` が single-file 同期を持つなら、SSoT 移行は generated file だけでなく sync script まで含めて完了扱いにする

## 関連ページ

- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
- [Repository Operating Structure](./repository-operating-structure.md)
