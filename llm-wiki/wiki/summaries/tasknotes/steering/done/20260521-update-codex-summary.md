---
source: raw/tasknotes/steering/done/20260521-update-codex.md
source_type: tasknote
created: 2026-05-24
status: draft
---

# 2026年5月21日 Codexを更新する Summary Draft

## summary

この note は、複数経路に分裂していた Codex CLI を棚卸しし、呼び出し先を `0.132.0` へ揃えた記録です。単純な update task を、実際には `PATH` と symlink の整理問題として解いた形になっています。

## key_points

- `~/.local/bin`、Homebrew、`~/node/bin`、Rust binary の 4 経路を比較した。
- `which codex` と symlink を整理し、最終的に `codex --version` を `0.132.0` にした。
- PATH 変更ではなく symlink 張り替えで shell rc 無修正のまま終えた。

## important_quotes

- "`4 経路の整理`"
- "`codex-cli 0.132.0`"

## open_questions

- 新規 VM セットアップ時に、Codex CLI の正規更新経路をどこへ明文化するべきか。
- dotfiles / setup skill が CLI 本体更新まで持つべきかをどう判断するべきか。
