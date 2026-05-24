---
source: raw/tasknotes/steering/done/20260420-j51-repo-architecture-restructure.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月20日 J51 architecture.md に沿って repo 構成と build 出力を再構成した Summary Draft

## summary

この tasknote は、`architecture.md` と repo の現実のずれを埋めるために、親子の入口を壊さず build 出力から `production/` / `development/` へ寄せる話を整理した記録です。中心は、monolith と root 出力中心の現状をいきなり理想形へ動かすと selector を壊しやすいため、まずは配布物側から段階的に再構成する方が `CJ21/CJ31/CJ33` を守りやすいと判断したことでした。

## key_points

- `architecture.md` は責務分担を示していたが、repo の現実は monolith と root 出力中心でまだ一致していなかった。
- build / release をいきなり理想形へ寄せると、親子が触る selector 入口を壊しやすいと整理した。
- そのため、まずは build 出力を `production/` / `development/` へ寄せる段階的な移行を優先した。
- `architecture.md` を章立てとライブラリ責務つきで書き直すことも実装対象に含めた。
- build 出力先の failing test を追加して、構成変更を guardrail 付きで進める前提を置いた。
- この note は、repo 構造の理想形と子ども向け入口の安定運用を両立させるための再構成メモになった。

## important_quotes

- "monolith + root 出力"
- "親子の入口を残しつつ"
- "配布物だけ `production/` / `development/` へ寄せるべき"

## open_questions

- repo 構成の理想形へ寄せるとき、何を先に分けて何を最後まで残すべきか。
- `architecture.md` の責務分担は、build 出力再構成のどの段階から実物と一致しているべきか。
