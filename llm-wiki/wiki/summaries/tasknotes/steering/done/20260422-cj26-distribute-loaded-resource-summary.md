---
source: raw/tasknotes/steering/done/20260422-cj26-distribute-loaded-resource.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年4月22日 CJ26 読み込んだ resource と配布する resource を一致させる Summary Draft

## summary

この tasknote は、子どもが今遊んでいる resource と親があとで持ち出す配布 artifact の resource を同じ source にそろえる試みと、その未完部分を記録したものです。実装では selector を server-first import に切り替え、shared staging と shared artifact を更新する build 分割まで進めましたが、後半で `development/production` の実 artifact が本当に同じ resource を見ている証明が薄いと分かり、note 自体を再オープンしました。

## key_points

- `assets/blockquest.pyxres` 固定と `candidate.resource_source` 採用が混在し、読み込んだ resource と配る resource の契約が揺れていた。
- browser localStorage を正本にすると別マシン共有ができないため、shared staging / shared artifact を truth にする方針へ切り替えた。
- `resolve_release_source_of_truth.py`、`build_release_artifacts.py`、`render_release_selector.py` を追加して build を分割した。
- selector は server import API を優先し、browser 保存は fallback へ落とす server-first import に切り替えた。
- 一方で、`development/production` の実 artifact まで同じ resource を見ている証明は薄く、ユーザー報告を受けて note を再オープンした。

## important_quotes

- "`いま読んでいる resource` と `あとで配る resource` を同じ source から選ぶ契約"
- "正本は browser ではなく shared staging / shared artifact でなければならない。"
- "`development/production` の実 artifact まで同じ resource を見ていると証明した記録は薄い。"

## open_questions

- development と production の実 artifact は、どこまで同じ resource source を共有するべきか。
- 「配布する resource が一致した」とは、zip だけでなくどの artifact まで揃った状態を指すのか。
