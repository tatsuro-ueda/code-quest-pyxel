# アーキテクチャ概要

> **この文書の役割**：採用技術と選定理由、そこから導かれる制約をまとめる「**設計判断の SSoT**」。
>
> **上位文書（最優先・自動 load）**：[../AGENTS.md](../AGENTS.md)（≤100 行、AI 用エントリポイント）
>
> **責務分担表（どこに何があるか）**：[repository-structure.md](repository-structure.md)
>
> **規約本体（M1〜M5）**：[framework-rule.md](framework-rule.md)

`repository-structure.md` が「**どこに何があるか**」を答え、`framework-rule.md` が「**どう書くか**」を答えるのに対し、本文書は「**なぜそうなっているか**」を答える。技術選定 → 制約 → 規約の論理鎖を一望できるようにする。

## 1. 製品の前提

Block Quest Pyxel は **子どもが Pyxel Code Maker で自分のゲームを編集できる** ことを根本価値に据えた RPG プロジェクト。AI コーディング前提で運用し、3 つのジョブ（プレイ／編集／配信）を回す好循環をつくる。

すべての設計判断は次の 3 つの前提から派生する：

- **子どもが正本を編集する**：`.pyxres` は子どもの編集物。AI / runtime が勝手に書き換えない（CJ26 / CJG23/24/26/37/41）。
- **AI コーディング前提**：規約は AI が自力で発見・検証できる形（M5）。文書は 3 層構造で迷子を防ぐ（→ 6 章）。
- **好循環の前提＝変える速さ**（CJ44）：中央集権クラスや一時 UI を増やさず、シンプルさを優先する。

## 2. 採用技術と役割

| 技術 | 役割 | 主な配置 |
|---|---|---|
| **Pyxel** | レトロゲームエンジン（描画 / 入力 / 音 / pyxres） | `src/runtime/*.py`, `src/scenes/*/view.py`, build 系 |
| **Python 3** | ゲーム本体の実装言語 | `src/` 全体 |
| **Pyodide** | ブラウザで Python を動かすランタイム（WASM） | `dist/pyxel.html`（`pyxel app2html` の中身） |
| **JS bridge** | ブラウザ側 save / Code Maker import の橋渡し | `src/shared/services/save_store.py`, `browser_resource_override.py` |
| **sqlite3** | Web プレイ記録の永続化（標準ライブラリ） | `src/shared/services/play_session_logging.py` |
| **pytest** | 自動検証（102 ファイル / 717 tests） | `test/` |
| **Playwright** | 配布 HTML を実ブラウザで起動する delivery gate | `tools/test_web_compat.py` |
| **YAML + 自前 codegen** | データ正本（敵・アイテム・呪文・店・武具・会話） | `assets/*.yaml` → `tools/gen_data.py` → `src/generated/*.py` |
| **exe.dev VM** | 開発・配信サーバの常時起動環境（Linux） | `tools/web_runtime_server.py`, AI セッション常駐 |

## 3. 選定理由と狙い

### 3.1 Pyxel を選んだ理由

- **子どもが触れる範囲がせまい**：tilemap / sprite / sound / music が一つの `.pyxres` に閉じている。**Pyxel Code Maker**（ブラウザ版エディタ）と直結しており、子どもが編集 → そのままゲームに反映できる。
- **配布が軽い**：`pyxel app2html` で WASM ＋ Pyodide にパッケージできる。インストール不要で URL 1 本で遊べる（友達にシェアできる導線が短い）。
- **制約が強い → 規約を書きやすい**：「単一 main.py」「描画 API はグローバル状態」など制約を逆手に取って M1〜M5 規約を作れる（→ 4 章）。

### 3.2 Pyodide / JS bridge を選んだ理由

- **ブラウザでも同じ Python コードが動く**：dev / prod の二系統 artifact を持たず、**1 つの `dist/` に一本化**できる（→ memory `single_distribution_policy`）。
- **ブラウザ側にしかない API を Protocol で吸収**：`SaveStore` Protocol を立て、`localStorage` / ファイル / インメモリの 3 実装を切り替える。Python 側はバックエンド差を意識しない。

### 3.3 MVP パターン（M1〜M5）を選んだ理由

- **AI が改修するとき「どこに書くか」がブレない**：Pyxel API は View、状態は Model、入力は Presenter、共有は GameState、と一意に決まる。
- **Model / Presenter が pyxel なしでテストできる**：headless で単体テストが書ける（M5-2 のテスト優先順位 1〜2 位）。
- **`tools/test_headless.py` で build gate を機械化**：import / 初期化 / 1 フレーム描画を build の前段で必ず通す。

### 3.4 YAML SSoT を選んだ理由

- **データ編集は人が読める形に**：敵・アイテム・呪文・店・武具・会話は `assets/*.yaml` を直接編集する。
- **runtime には自動生成物だけ流す**：`tools/gen_data.py` → `src/generated/*.py` の一方向（→ memory `ssot_policy`）。AI が dict を勝手に増やせない。
- `generated/*.py` は、YAML を先に読みやすい形へ写した「清書ノート」。
- 今の repo は、ゲーム本番にその清書ノートだけを持って行く作り。
- そうすると、ブラウザで YAML を読む準備や追加部品がいらない。
- Code Maker 用の配布物も、この清書ノートを前提にまとめている。
- つまり今は、「本番で迷わず確実に動かす」ために `generated/*.py` を使う。

### 3.5 exe.dev VM を選んだ理由

- **AI コーディング前提の開発環境**：Claude Code などの AI セッションが常駐できる Linux VM。
- **HTTPS proxy 経由でブラウザ動作確認**：[exe.dev/docs/proxy.md](https://exe.dev/docs/proxy.md) 経由で配信物を実ブラウザに通せる。
- **documented features 以外は触らない**：undocumented な local endpoint は unstable / unsupported なので使わない（CLAUDE.md にも記載）。

## 4. 採用技術から導かれる制約

各制約は「**どの技術が原因か**」「**どの規約に落ちているか**」をひもづけて読む。

| 制約 | 原因 | 落ちている場所 |
|---|---|---|
| **`pyxel.*` 描画 API は View / 最外殻だけ**、Model / Presenter / Service では呼ばない | Pyxel（グローバル状態 API） | `framework-rule.md` M1-1 |
| **入力（`pyxel.btn / btnp`）はフレーム冒頭にスナップショット化し、Presenter は `InputStateTracker` 経由でしか見ない** | Pyxel（入力もグローバル状態） | `framework-rule.md` M1-2 |
| **単一 main.py に bundler で concat する**（手 inlined 維持禁止） | Pyxel（Code Maker / `app2html` が単一 main.py を要求） | `tools/build_codemaker.py`, `repository-structure.md` 3.5 章 |
| **pyxres = SSoT、runtime は読み取りのみ**（ImageBanks は書き込み・初期化・fallback のみ） | Pyxel + 子ども編集前提 | `framework-rule.md` M4-2, `repository-structure.md` 4.5 |
| **`SaveStore` Protocol でセーブ先を抽象化**（InMemory / File / LocalStorage の 3 実装） | Pyodide / JS bridge | `src/shared/services/save_store.py`, `framework-rule.md` M4-2 |
| **dev / prod artifact 分離禁止、`dist/` 一本化** | Pyodide / 子ども前提（友達にシェア導線が短いこと） | memory `single_distribution_policy` |
| **YAML を直読しない、`src/generated/` を直書きしない** | Python + AI コーディング前提 | `framework-rule.md` M5-3, `tools/hooks/*.sh` |
| **`tools/test_headless.py` / `test_web_compat.py` を build gate に置く** | Pyxel + Pyodide | `repository-structure.md` 5.2 |
| **`tools/hooks/*.sh` + `.claude/settings.json` の 2 系統 guardrail** | 子ども編集前提 + AI コーディング | `framework-rule.md` M5-3 |
| **AGENTS.md は ≤100 行**（自動 load の context を圧迫させない） | AI コーディング前提 | `test_cjg_framework_rule_guards.py::test_agents_md_under_100_lines` |
| **中央集権クラスや一時 UI（ON/OFF メニュー等）を増やさない** | CJ44（変える速さ＝好循環の前提条件） | memory `cj44_simplicity` |
| **子ども向け UI はひらがな表記・iframe 全画面・ボタンフェードアウト** | 子ども前提 | memory `ui_policy` |
| **`src/` モジュール冒頭は関数・クラス箇条書きの日本語 docstring**（`from __future__` より前） | AI コーディング前提（AI が読み始めで構造を把握できるよう） | memory `module_docstring_policy` |

## 5. 開発環境

| 項目 | 内容 |
|---|---|
| **OS** | Linux（exe.dev VM） |
| **VM ドキュメント** | [exe.dev/docs.md](https://exe.dev/docs.md)（HTTPS proxy: [exe.dev/docs/proxy.md](https://exe.dev/docs/proxy.md)） |
| **常駐サーバ** | `tools/web_runtime_server.py` を systemd user unit で常時起動（残タスク：`repository-structure.md` 9 章 参照） |
| **AI セッション** | Claude Code（`.claude/settings.json` で permission / hook を制御） |
| **build runbook** | `repository-structure.md` 3.5 章（`build_codemaker.py` / `build_web_release.py` の使い分け） |

> **重要**：exe.dev VM の undocumented な local endpoint は触らない（unstable / unsupported）。documented features（[exe.dev/docs.md](https://exe.dev/docs.md)）のみ利用する。

## 6. 文書 3 層構造

| 文書 | 答える問い | サイズ制約 |
|---|---|---|
| `../AGENTS.md` | **最初に何を読むか・何を絶対にやらないか** | ≤100 行（static guard あり） |
| **`architecture.md`（本文書）** | **なぜこの作りなのか**（採用技術 → 制約） | 制限なし |
| `repository-structure.md` | **どこに何があるか**（責務分担表 + ディレクトリ規約 + build runbook） | 制限なし |
| `framework-rule.md` | **どう書くか**（M1〜M5 規約本体） | 制限なし |

読む順序：

1. `AGENTS.md`（自動 load）
2. **「なぜこの作り？」が分からないとき → `architecture.md`**
3. 「どこに何がある？」が分からないとき → `repository-structure.md`
4. 「規約の詳細は？」を確認したいとき → `framework-rule.md`
5. 詳細要件は `customer-jobs.md` / `customer-journeys.md` / `product-requirements-*.md` / 関係 `steering/`

## 7. 関連文書

- `customer-jobs.md` — 顧客のジョブと好循環（製品前提の根拠）
- `customer-journeys.md` — CJ44 シンプルさ優先・CJ26 子ども編集物保護 などの ID 元
- `product-requirements-*.md` — 6 分野の gherkin（av / battle / guardrails / map / narrative / platform）
- `llm-wiki-ops-schema.md` — LLM 向け永続 wiki の運用 schema
- `superpowers/` — 製品の核となる体験設計メモ
