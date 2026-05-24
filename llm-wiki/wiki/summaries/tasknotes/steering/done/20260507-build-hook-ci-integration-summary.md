---
source: raw/tasknotes/steering/done/20260507-build-hook-ci-integration.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月7日 検証スクリプトを pre-commit / CI に統合（B2 + C4 の補足） Summary Draft

## summary

この note は、verify/test スクリプトを local hook と GitHub Actions CI に接続した記録です。`make verify` を pre-commit と remote verify lane の両方に載せ、human / AI どちらの変更でも同じ入口を通す形に整えました。

## key_points

- `.pre-commit-config.yaml` と `.github/workflows/verify.yml` を追加し、`tools/install_hooks.sh` を冪等更新した。
- ローカル hook から `make verify + pytest` が exit 0 になるところまで確認した。
- GitHub Actions は YAML 構造とステップ存在を確認し、実起動は push 後確認と明記した。

## important_quotes

- "`pre-commit + post-commit`"
- "`make verify`"

## open_questions

- 最初の remote run 後、CI の実測結果をどこへ記録して運用 knowledge に戻すべきか。
- verify lane が重くなった時、local hook と CI の責務配分をどう再調整するべきか。
