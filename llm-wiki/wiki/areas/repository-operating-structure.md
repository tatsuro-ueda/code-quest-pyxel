---
status: active
last_updated: 2026-05-24
sources:
  - ../summaries/knowledge/repository-structure-summary.md
  - ../summaries/knowledge/framework-rule-summary.md
  - ../summaries/tasknotes/done/20260412-g12-rebuild-codemaker-zip-summary.md
  - ../summaries/tasknotes/done/20260412-guardrails-1-ssot-codegen-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-5-save-compat-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-2-hooks-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-3-headless-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j31-fix-selector-links-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j36-dialogue-ssot-summary.md
  - ../summaries/tasknotes/steering/done/20260412-guardrails-6-web-delivery-test-summary.md
  - ../summaries/tasknotes/steering/done/20260412-j38-preview-build-flow-summary.md
  - ../summaries/tasknotes/steering/done/20260413-j21-access-log-visibility-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j43-public-access-log-runtime-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime-summary.md
  - ../summaries/tasknotes/steering/done/20260414-j46-web-cache-bust-preview-current-summary.md
  - ../summaries/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen-summary.md
  - ../summaries/tasknotes/steering/done/20260416-j49-bind-preview-to-open-request-note-summary.md
  - ../../raw/knowledge/docs/repository-structure.md
  - ../../raw/knowledge/docs/framework-rule.md
  - ../../raw/tasknotes/done/20260412-g12-rebuild-codemaker-zip.md
  - ../../raw/tasknotes/done/20260412-guardrails-1-ssot-codegen.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-5-save-compat.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-2-hooks.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-3-headless-test.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md
  - ../../raw/tasknotes/steering/done/20260412-j31-fix-selector-links.md
  - ../../raw/tasknotes/steering/done/20260412-j36-dialogue-ssot.md
  - ../../raw/tasknotes/steering/done/20260412-guardrails-6-web-delivery-test.md
  - ../../raw/tasknotes/steering/done/20260412-j38-preview-build-flow.md
  - ../../raw/tasknotes/steering/done/20260413-j21-access-log-visibility.md
  - ../../raw/tasknotes/steering/done/20260414-j43-public-access-log-runtime.md
  - ../../raw/tasknotes/steering/done/20260414-j44-stale-preview-selector-runtime.md
  - ../../raw/tasknotes/steering/done/20260414-j46-web-cache-bust-preview-current.md
  - ../../raw/tasknotes/steering/done/20260416-j47-preview-first-selector-autogen.md
  - ../../raw/tasknotes/steering/done/20260416-j49-bind-preview-to-open-request-note.md
---

# Repository Operating Structure

## 核心

`repository-structure` は、repo を `どこを直すべきか迷わない operating map` として固定する。`framework-rule` が why を与え、こちらが where を与える関係で、runtime 入口、scene/service/state の置き場、build runbook、dependency rule を実務レベルまで落としている。

## source ownership

- `src/` と `assets/` が source of truth
- `dist/` は配布物置き場で source ではない
- `src/runtime/app.py::Game` が実装の窓口
- scenes、services、state、generated の責務を分ける
- `assets/*.yaml -> tools/gen_data.py -> src/generated/*.py -> src/game_data.py` が data 系の更新経路になる
- Code Maker 向け `code-maker.zip` は build 生成物だが、中身は `main.py` と `blockquest.pyxres` の現行正本に追従する必要がある
- `.claude/settings.json` と `tools/hooks/*.sh` が generated / `.pyxres` / import path の誤操作を止める guardrail entrypoint になる
- `tools/test_headless.py` が build 前段で import / init / 1 フレーム描画を検査する runtime guardrail になる
- `tools/test_web_compat.py` が wrapper から実ブラウザ起動までを検査する
  user-facing delivery gate になる
- `tests/fixtures/save_v1.json` と `tools/test_save_compat.py` が save schema 変更の migration safety を守る tool layer になる
- `generate_wrapper()` で作る `play.html` は selector page から実ゲームへつなぐ user-facing artifact lane の一部である
- `tools/build_web_release.py` は current / preview 分離と `--promote` を持つ
  approval build lane の中核でもある
- `tools/web_runtime_server.py` と `src/play_session_logging.py` は shared play の
  session facts を残す server lane になる
- dialogue も `assets/dialogue.yaml -> tools/gen_data.py -> src/generated/dialogue.py -> src/game_data.py` と `tools/sync_main_data.py` の同期経路へ収まる
- `tools/web_runtime_server.py` は、shared play logging を含む実公開 lane の
  正式な server 入口として扱う必要がある
- preview source が無いときに stale preview を掃除する処理も、
  build artifact lane の責務に含まれる
- `tools/build_web_release.py` は build token 付き URL と preview diff 由来の
  metadata を生成する release lane でもある
- preview/current の昇格は request note の目視一致でなく、
  source を回す promotion flow として扱う

## 運用上の意味

- build の順序と落とし穴が明文化されている
- `docs と code がずれたら未実装/仕様ずれ` の扱いを固定する
- AI 修正時に `どこを触ってはいけないか` も含めて案内できる
- generated pipeline と packaging lane の両方を知っていると、AI が直す場所と regenerate する場所を混同しにくい
- hooks、headless test、resource verify の置き場が見えていると、guardrail を「仕組み」として保守しやすい

## この repo への含意

- architecture review や ingest/query 時の root reference として使いやすい
- guardrail の多くは、この責務分担が前提になっている
- repo structure が stale になると、AI の修正面も stale になる
- packaging artifact や generated data の通り道が stale になると、AI の修正入口そのものがずれていく
- `.pyxres` の current truth が変わったときも、runtime self-heal と build verify のどちらが正式経路かを repo map に反映しておく必要がある
- selector から辿る wrapper artifact が欠けるだけでも、repo map と child-facing delivery は同時に壊れる
- dialogue のような旧来の直書き data は、single-file `main.py` 同期まで含めて repo map に戻さないと半端な二重管理になる
- preview/current 分離や play-session logging も、build lane と wrapper lane の
 責務として repo map に載っていないと運用がすぐずれる
- 実公開 server lane が repo map に載っていないと、コードが正しくても
  運用で facts が落ちる
- 説明 metadata や preview artifact を build-owned と明示しないと、
  SoT がすぐ分裂する

## 関連ページ

- [View Presenter Model Boundaries](./view-presenter-model-boundaries.md)
- [Single Source Of Truth And Golden Path](./single-source-of-truth-and-golden-path.md)
- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
- [Guardrails Protect The Loop](./guardrails-protect-the-loop.md)
