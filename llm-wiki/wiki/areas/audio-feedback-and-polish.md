---
status: active
last_updated: 2026-05-23
sources:
  - ../summaries/knowledge/product-requirements-av-summary.md
  - ../summaries/knowledge/ux-policy-summary.md
  - ../../raw/knowledge/docs/product-requirements-av.md
  - ../../raw/knowledge/docs/ux-policy.md
  - ../summaries/tasknotes/steering/done/20260506-bgm-pyxres-ssot-summary.md
  - ../../raw/tasknotes/steering/done/20260506-bgm-pyxres-ssot.md
  - ../summaries/tasknotes/steering/done/20260507-bundle-rebuild-after-bgm-ssot-summary.md
  - ../../raw/tasknotes/steering/done/20260507-bundle-rebuild-after-bgm-ssot.md
  - ../summaries/tasknotes/steering/done/20260510-stakeholder-voices-av-guidance-theme-migration-summary.md
  - ../../raw/tasknotes/steering/done/20260510-stakeholder-voices-av-guidance-theme-migration.md
---

# Audio Feedback And Polish

## 核心

`product-requirements-av` は、BGM・SFX・VFX を polish ではなく `差が分かる体験` の本体として扱う。しかもその polish は複雑な設定 UI でなく、scene ごとの直接再生、イベントに結びつく手応え、子どもが Code Maker で作った音をそのまま聞けることによって成立する。

## 守るべきこと

- 場所や場面が変わったら音の雰囲気も変わる
- 攻撃、回復、成長、被弾などの重要イベントに手応えが返る
- Sound / Music の authoring は人が持ち、AI は import / build で支える
- CJ44 の方針により、比較のための複雑な ON/OFF UI は増やさない

## この repo への含意

- audio 実装では `誰が音を作るか` と `runtime がどう鳴らすか` を混ぜない
- pyxres を SSoT として保ち、Python 側の固定メロディ上書きを避ける
- UX 的には「押した」「勝った」「移った」がすぐ伝わることを優先する

- BGM pyxres SSoT and bundle rebuild moved music truth into pyxres plus scene views, then verified the shipped artifacts reflect that simpler audio ownership.

- the AV guidance/theme migration brought audio and guidance expectations under stakeholder trace coverage, making it easier to separate traced intent from implemented polish.

## 関連ページ

- [Guardrail Layering And AI Change Boundaries](./guardrail-layering-and-ai-change-boundaries.md)
- [Child Readable UX And Parent Assist](./child-readable-ux-and-parent-assist.md)
