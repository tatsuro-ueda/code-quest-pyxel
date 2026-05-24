---
source: raw/tasknotes/steering/done/20260425-autonomous-rule-compliance-loop.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月25日 既存コードを最新ルール群に自律的に準拠させる（サイクリックループ） Summary Draft

## summary

この tasknote は、既存コードを `framework-rule` の最新 M1〜M5 群へ自律的に寄せるためのサイクリックな compliance loop を回し、即完走できるものと人判断が要るものを切り分けた記録です。結果として、M5-1 命名規約は違反 0 件、M5-3 は AGENTS.md へ M1〜M5 サマリと検証コマンドを追加するところまで閉じ、残りは services/ui 描画例外や M3-3 command 化など 6 件の judgment item として停止しました。

## key_points

- loop は M1〜M5 の各サブルールを小さく検査し、最小修正で閉じられるものだけ進める方針で回された。
- M5-1 命名規約は file/class 命名とも違反 0 件で即完走だった。
- M5-3 は AGENTS.md に `コード階層規約（M1〜M5）` セクションを追加し、AI 向けの最短サマリと検証コマンドを置いた。
- M4-1 他 scene model 直代入は 0 件まで解消し、M4-3 / M4-4 の段階移行は scope 大として判断待ちへ倒した。
- 最終的に services/ui の pyxel draw、M3-3 command 化、M4-2 service 分類、Game state 7 件、old shim 群、ARCHITECTURE 名称の 6 件を review 候補として明示した。

## important_quotes

- "Phase 1 〜 Phase 6 全 6 Phase 完走"
- "AGENTS.md に新セクション「## コード階層規約（M1〜M5）」を追加"
- "ループ自走を一旦停止し、ユーザーレビュー待ちにするのが合理的"

## open_questions

- 残った 6 件の judgment item を、どの順で別 loop へ切り出すべきか。
- services/ui 内の pyxel draw 例外を rule 側で許容するか、構造側をさらに寄せるべきか。
