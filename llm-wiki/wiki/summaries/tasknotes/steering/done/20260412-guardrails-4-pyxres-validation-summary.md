---
source: raw/tasknotes/steering/done/20260412-guardrails-4-pyxres-validation.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月12日 ガードレール(4) pyxres整合チェック Summary Draft

## summary

この tasknote は、もともと `pyxres` とコード定数のずれを runtime 側で検出し、必要なら自動再生成して吸収する前提で書かれていました。ただし 2026年4月19日の注記で、その前提は現行正本ではないと明示されており、現在は `.pyxres` の実体は人が Pyxel Code Maker で編集し、AI / Codex は direct edit や runtime self-heal ではなく、build / packaging / verify で支える方針へ読み替える必要があります。

## key_points

- もとの深層的目的は、`pyxres` とコード定数の乖離を自動検出することだった。
- 当時の note は `_tile_bank_layout_valid()` と headless 起動を通じて、起動時自己修復までを guardrail とみなしていた。
- 2026年4月19日の注記で、「runtime が `.pyxres` を自動再生成する」前提は現在の正本ではないと明記された。
- 現在の方針では、見た目や音の実体は人が Pyxel Code Maker で修正し、AI / Codex は `.pyxres` を直接編集しない。
- したがって現在の guardrail は、mismatch を silent self-heal に逃がすのではなく、build / packaging / verify で検出して止める方向で解釈すべきである。
- G4、G6 を headless test とどう結び直すかは、現行の Code Maker truth に合わせて再定義が必要である。

## important_quotes

- "この note の「runtime が `.pyxres` を自動再生成する」前提は、現在の正本ではありません。"
- "AI / Codex は `.pyxres` を直接編集せず、build / packaging / verify で支えることです。"
- "pyxresとコード定数の乖離を自動検出する。"

## open_questions

- 現行方針での `pyxres` validator は、何を build 時に fail させるべきか。
- tile/resource mismatch を headless 起動テスト、専用 validator、health-check のどこで担保するか。
- G6 のサウンド再初期化確認を、今の audio/resource 境界でどう検証し直すか。
