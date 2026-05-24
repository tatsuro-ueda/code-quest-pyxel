---
source: raw/tasknotes/steering/done/20260518-flake8-cr-scenes-rest27.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月18日 src/scenes 残 27 件に flake8-cr 新ルールを適用（タスク C） Summary Draft

## summary

この note は、新しい flake8-cr ルール込みで `src/scenes/` の残り 27 件を片付け、scene 全域を 0 件にした記録です。A/B で決めた分割パターンを presenter/scene/view へ展開し、最後に lint 0 + verify/build green まで閉じました。

## key_points

- battle、explore、menu、professor、shop、title の残り CR202/CR204/CM001/E501 を順に消した。
- 乱数順に敏感な battle attack 系は最小分割に留め、pytest/verify/build green を保った。
- `flake8-cr src/scenes/` 0 件を達成した。

## important_quotes

- "`flake8-cr 0 件`"
- "`乱数順を保つ最小分割`"

## open_questions

- 今回の helper/述語命名パターンを、今後どこまで codegen や lint autofix へ寄せるべきか。
- scene 全域 0 件達成後の維持を、pre-commit/CI でどこまで hard gate 化するべきか。
