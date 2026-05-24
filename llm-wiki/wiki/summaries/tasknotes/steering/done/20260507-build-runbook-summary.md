---
source: raw/tasknotes/steering/done/20260507-build-runbook.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月7日 build 起動方法 runbook を docs に明文化 Summary Draft

## summary

この note は、AI が毎回 build 起動方法で迷わないよう `docs/architecture.md` に runbook を追加した記録です。Code Maker 単体再生成、full release、BGM/pyxres 変更後の順序、PYTHONPATH の罠まで 1 箇所に集めました。

## key_points

- `docs/architecture.md` に `## 3.5 build の起動方法（runbook）` を追加した。
- `build_codemaker.py` と `build_web_release.py` の正しい起動コマンド、および `PYTHONPATH=.` が必要な理由を明記した。
- pytest -> release build -> bundle 自己検査 -> git status の順序を、BGM/pyxres/view/scene 変更時の既定手順にした。

## important_quotes

- "`主に AI で運用するので毎回迷わず`"
- "`PYTHONPATH=.`"

## open_questions

- build tooling 側を将来 package 化して、runbook から `PYTHONPATH` 依存を消すべきか。
- build / release / debug の runbook を今後どこまで分割していくべきか。
