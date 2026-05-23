---
status: draft
origin:
  - docs/architecture_rules.yml
last_synced: 2026-05-23
---

# Architecture Checklist

`docs/architecture_rules.yml` を開発前に pass / fail で確認しやすい形へ落とした checklist。原典の `meta.status` が `draft` のため、この checklist も `draft` として扱う。

## Code Maker を子どもの正式編集面として守る

前提: Pyxel Code Maker は子どもの正式な編集面である。

- [ ] tilemap / sprite / sound / `.pyxres` の編集面では Code Maker を最初の正として扱っている
- [ ] 内部都合で Code Maker を不要化していない
- [ ] 内部都合で Code Maker を脇役化していない

## docs を要求として扱う

前提: docs と code のずれは未実装 / バグ / 仕様ずれとして扱う。

- [ ] code と docs が食い違う場合、差分を要求ベースで明記している
- [ ] code があるから正しい、という判断で片付けていない

## pyxres を正本として守る

前提: `.pyxres` は子どもと親が Code Maker で編集する正本である。

- [ ] AI は code / build / packaging / guardrail / test の側で支えている
- [ ] pyxel resource 実体を確認するときは、実物を最初の正としている
- [ ] `.pyxres` の中身をテキスト編集の主戦場にしていない

## dist を配布物として扱う

前提: `dist` は配布物の置き場であり source ではない。

- [ ] source の修正は `src` / `assets` / `tools` / `docs` 側で行っている
- [ ] `dist` 配下を手修正の正本にしていない

## done に実物確認を含める

前提: done はコード・テスト・実物確認を含む。

- [ ] zip / `.pyxres` / HTML / save data / 実行画面の実物確認を行っている
- [ ] runtime code や build script を直しただけで完了扱いにしていない
