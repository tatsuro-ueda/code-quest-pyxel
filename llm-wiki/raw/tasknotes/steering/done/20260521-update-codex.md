---
status: done
priority: normal
scheduled: 2026-05-21T00:00:00.000+09:00
dateCreated: 2026-05-21T00:00:00.000+09:00
dateModified: 2026-05-21T11:30:00.000+09:00
tags:
  - task
  - codex
  - maintenance
---

# 2026年5月21日 Codexを更新する

> 状態：⑩ Closed
> 次のゲート：—

---

## 1) Journey（どこへ行くか）

> 補足：深層的目的 exe.dev VM 上の Codex 関連ツール群を最新化し、長時間セッションでも安定して使える状態を保つ
> 補足：やらないこと Codex の設定ファイル（`~/.codex/config.toml`）や認証情報（`~/.codex/auth.json`）の変更、dotfiles 配下の Codex 設定の改修
> 補足：責務分担厳格度 basic

1. 前提条件
   1. 💦 dotfiles の `install.sh` は `Codex superpowers` を git pull する処理を含むが、Codex CLI 本体の更新は別
   2. 💦 exe.dev VM 上では Homebrew (`/home/linuxbrew/.linuxbrew/bin/`) が主なパッケージ経路
   3. 💦 直前の `dotfiles更新` で `install.sh` を実行済み → Codex superpowers は最新

2. Before
   1. 💦 Codex CLI のバージョンが最新か未確認
   2. ❌ もどかしい

3. After
   1. ✅ Codex CLI が最新版にアップデートされている
   2. ✅ 更新前後のバージョンが記録されている
   3. ❤️ スッキリ

4. 例外
   1. すでに最新なら no-op として記録のみ残す
   2. インストール経路が不明な場合は、まず `which codex` と該当パッケージマネージャでの管理状態を確認する

5. 境界条件
   1. 対象は Codex CLI 本体（および付随する Codex superpowers / Claude skill sync が dotfiles 経由で同期されていること）
   2. 設定ファイルや認証情報は触らない
   3. exe.dev VM の `setup-new-machine` スキルとの整合性を崩さない

6. 委任度
   1. 🟢 更新コマンド実行は CC のみで可
   2. 🟡 更新範囲が「Codex CLI 本体だけ」か「周辺ツール含む」かは人と相談

---

## 2) ユーザーストーリーマップ

> 委任度：🟡 更新対象の範囲確認後は CC が完走可能
> 残る曖昧さ：更新対象を Codex CLI 本体のみに限定するか、周辺ツールも含めるか

### 事前確認

- [ ] tasknote確認済み:
  - [ ] 過去の Codex 更新／セットアップ系 tasknote
- [ ] skill・tool・MCP確認済み:
  - [ ] `setup-new-machine`（exe.dev VM セットアップ手順）
  - [ ] `update-dotfiles`（直前に実行済み）
- [ ] 永続的ドキュメント確認済み:
  - [ ] dotfiles の `install.sh` 内 Codex 関連処理

### 本体

1. 現在の Codex CLI のインストール経路とバージョンを確認する
2. 更新対象の範囲を人に確認する（CLI 本体のみ / 周辺ツール含む）
3. 適切なパッケージマネージャで更新を実行する
4. 更新後のバージョンを記録する
5. Codex を起動して動作確認する

---

## 3) Gherkin（完了条件）

> 委任度：🟢 確認内容は明確、CC で検証可能
> 残る曖昧さ：なし

### シナリオ一覧

- [ ] シナリオ1：Codex CLI を最新版に更新する

1. 🧱 exe.dev VM 上で Codex CLI が古いバージョンで動いている
2. 🎬 適切なパッケージマネージャで更新コマンドを実行する
3. ✅ Codex CLI のバージョンが最新になり、起動も成功する

```gherkin
Given exe.dev VM 上で Codex CLI が利用可能である
And 現在のバージョンが確認されている
When 適切なパッケージマネージャで Codex CLI を更新する
Then 更新後のバージョンが最新版と一致する
And `codex --version`（または相当コマンド）が正常に応答する
```

---

## 4) Design（どうやるか）

- **関連スキル・MCP**：`setup-new-machine`（参照のみ）

更新経路の候補：

- Homebrew 経由：`brew upgrade codex`
- npm 経由：`npm update -g @openai/codex`
- 公式インストーラ：再ダウンロード

→ `which codex` の結果と `brew list | grep codex` などで実際の経路を確定してから更新する。

---

## 5) Tasklist

- [x] （CC）`which codex` と現在バージョンを確認する
- [x] （CC）インストール経路（Homebrew / npm / その他）を特定する
- [x] （ユーザー）更新範囲を確認（CLI 本体のみ / 周辺含む）→ npm global 一本化
- [x] （CC）更新コマンドを実行する → 既存4経路の整理
- [x] （CC）更新後バージョンを確認し、起動テストを行う
- [x] （CC）Result に before/after バージョンを記録する

---

## 6) Result（成果物）

### Before（4 経路が混在、PATH 順で最古が呼ばれていた）

| 経路 | バージョン | 実体 |
|---|---|---|
| `~/.local/bin/codex`（PATH先頭、呼出中） | **0.120.0** | `~/.local/lib/node_modules/@openai/codex/`（Apr 12 設置） |
| `/home/linuxbrew/.linuxbrew/bin/codex` | 0.129.0 | `/home/linuxbrew/.linuxbrew/lib/node_modules/@openai/codex/`（May 8 設置） |
| `~/node/bin/codex` | 0.132.0 | `~/node/lib/node_modules/@openai/codex/`（May 21、最新） |
| `/usr/local/bin/codex` | 0.117.0 | 180MB の ELF static-pie binary（Mar 26、Rust製単体） |

### After（npm global 一本化）

- `which codex` → `/home/exedev/.local/bin/codex` → `~/node/bin/codex` → `~/node/lib/node_modules/@openai/codex/bin/codex.js`
- `codex --version` → **`codex-cli 0.132.0`**
- 他3経路（linuxbrew / ~/.local/lib の旧 npm install / /usr/local/bin の binary）は削除済み

### 実行コマンド

```bash
# linuxbrew経由削除
/home/linuxbrew/.linuxbrew/bin/npm uninstall -g @openai/codex

# ~/.local の古い npm install を削除
npm uninstall -g --prefix /home/exedev/.local @openai/codex

# ハンドル張り替え（PATH変更を避け、shell rc 無修正）
ln -s /home/exedev/node/bin/codex /home/exedev/.local/bin/codex

# /usr/local/bin の binary 削除（sudo必要）
sudo rm /usr/local/bin/codex
```

---

## 7) Discussion（反省）

- 「Codex を更新」という単純タスクが実際は「4 経路の整理」になった。`dotfiles更新` の install.sh は Codex superpowers と Claude skill sync は同期するが、CLI 本体の更新経路までは管理しないため、定期メンテで経路が分岐しがち。
- exe.dev VM では Homebrew / npm global / 公式 Rust binary が並存しやすい。新規 VM 立ち上げ時の `setup-new-machine` スキル側で「Codex CLI は npm global に統一」と明文化する余地があるが、今回のスコープ外。
- PATH 変更を伴わない symlink 張り替えで shell rc 無修正のまま完了できた点は判断として良かった。

---

## 8) 参考文献

- dotfiles `install.sh`（Codex superpowers / Claude skill sync 関連処理）
- `~/.claude/skills/setup-new-machine/SKILL.md`
