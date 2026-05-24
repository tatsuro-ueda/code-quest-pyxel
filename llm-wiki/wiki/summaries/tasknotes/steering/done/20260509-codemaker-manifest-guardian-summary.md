---
source: raw/tasknotes/steering/done/20260509-codemaker-manifest-guardian.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月9日 Code Maker manifest 完全性 rule と guardian autofix Summary Draft

## summary

この note は、Code Maker bundle の必須 path を architecture rule と guardian autofix で守るようにした記録です。manifest の欠落を deterministic に検知し、安全な追記だけを guardian が自動修復できる形へ進めました。

## key_points

- `docs/architecture_rules.yml` に Code Maker non-scene bundle contract を追加した。
- `codemaker_manifest_non_scene_paths` rule と manifest required path check を checker に実装した。
- guardian には manifest の safe autofix を加え、回帰 test も追加した。

## important_quotes

- "`manifest required path`"
- "`safe autofix`"

## open_questions

- bundle 契約を今後広げるなら、facts 側の required path と guardian の autofix 境界をどう揃えるべきか。
- manifest で自動修復してよい変更と、人判断に残す変更をどこで線引きするべきか。
