# 01 練習用プロジェクトの正本 docs と Git snapshot 候補を棚卸しする

- 推奨タイトル:
  - `YYYY年M月D日 練習用プロジェクトの正本 docs と Git snapshot 候補を棚卸しする`
- 目的:
  - `latest docs` と `history snapshots` の候補を分ける
- 入力:
  - `architecture.md`
  - `ux-policy.md`
  - `customer-journey.md`
  - `customer-jobs.md`
  - `git log --follow`
- 完了条件:
  - 今の正本 docs 一覧が決まっている
  - Git 履歴の節目 snapshot 候補が 2〜3 個に絞られている
- 最初の一手:
  - docs 一覧を出し、`git log --follow -- <doc>` で変化点を拾う
- メモ:
  - 全 commit を入れず、方針転換点だけを拾う
- 委任メモ:
  - 🟢 候補出しと履歴拾いは委任しやすい。正本の最終採否だけ最後に人が決める
- 先に決めること:
  - `old-` 系や draft 系をどこまで deprecated 扱いするか

---

## code-quest-pyxel 固有メモ（2026-05-22）

### 入力の現状

下書き入力のうち `architecture.md` `ux-policy.md` `customer-journey.md` は **存在しない**。
実際にある docs は以下：

| ファイル | サイズ | 状態 / 用途 |
|---|---|---|
| `docs/architecture_rules.yml` | 63KB | `status: draft` 正本候補 / principles + must / must_not 構造 |
| `docs/repository-structure.md` | 26KB | architecture_rules.yml にリプレース予定 |
| `docs/framework-rule.md` | 35KB | 命名・運用ルール |
| `docs/customer-jobs.md` | 7.8KB | 現行？ |
| `docs/old-customer-jobs.md` | 5.0KB | deprecated？ |
| `docs/customer-journeys.md` | 95KB | 大型 journey 集 |
| `docs/story-concepts.md` | 5.5KB |  |
| `docs/stakeholder_voices.yml` | 107KB | 大型 |
| `docs/product-requirements-av.md` | 17KB |  |
| `docs/product-requirements-battle.md` | 10KB |  |
| `docs/product-requirements-guardrails.md` | 56KB | 大型 |
| `docs/product-requirements-map.md` | 15KB |  |
| `docs/product-requirements-narrative.md` | 10KB |  |
| `docs/product-requirements-platform.md` | 39KB |  |

### ユーザー判断ゲート

棚卸し中にユーザー確認が必要：

- `architecture_rules.yml` vs `repository-structure.md`: どちらを正本扱い？
- `customer-jobs.md` vs `old-customer-jobs.md`: どちらを正本扱い？
- 大型 docs（>50KB）の章分割粒度をここで決めるか、04 まで持ち越すか
- `product-requirements-*` 群を**全部正本扱い**か、それとも **area 別に分けて部分採用**か

### 棚卸し手順（具体化）

1. `ls -la docs/` で全 docs を確認
2. 各 docs に対して `git log --follow --oneline -- docs/<file>` で履歴を取る
3. commit 数が多いファイルから方針転換点 commit を拾う
4. ユーザー確認: 「これを正本／これを deprecated」マッピング
5. 候補出力フォーマット:
   - `latest_docs:` リスト
   - `history_snapshots:` `(file, commit_hash, reason)` のリスト
   - `deprecated:` リスト

### 委任時の暴走パターン

- 全 docs を「正本」扱いしてしまう（`old-` プレフィクスを見落とす）
- → AI に「`old-` プレフィクスは deprecated 扱い」を先に指示
- 大型 docs を理由なしに章分割してしまう
- → 章分割は 04 で粒度判断のあとに行う
