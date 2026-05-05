---
status: open
priority: normal
scheduled: 2026-05-06T00:00:00+09:00
dateCreated: 2026-05-05T17:45:00+09:00
dateModified: 2026-05-05T17:45:00+09:00
tags:
  - task
  - framework-rule
  - m4-3
  - m4-4
  - game-state
  - cleanup
---

# 2026年5月5日 Game クラス state 7 件の段階移行（M4-3 圧縮）

> 状態：① Journey 略式
> 分離元：`steering/20260425-autonomous-rule-compliance-loop.md` 判断待ち「2026-04-25 18:25 — `src/runtime/app.py` Game クラス state 7 件（M4-3 段階移行未完）」

---

## 1) Journey

- **深層的目的**：役割を分担し、編集しやすくすることで、好循環を回しやすくする

1. 💦 （開発者・AI）機能を追加したりバグ修正したい（コードエディタ／AI 起動時 context）
2. 💦 （開発者・AI）どの規約文書を最初に読むか考える（コードエディタ／AI 起動時 context）
3. Before
  1. 💦 `Game` クラスに 7 fields（`state`, `prev_state`, `debug_mode`, `debug_seq`, `cam_x`, `cam_y`, `dungeon_rooms`, `current_town`）が含まれている
  2. ❌ 見通しが悪い、修正しづらい
2. After
  1. ✅ 各 field の参照箇所がSceneManager / DebugService / ViewportService / WorldGenerationServiceに分かれている
  2. ✅ 見通しが良い、修正しやすい
  3. ♥️ 好循環が起きる

## 2) Gherkin

### シナリオ1：`current_town` が GameState に一元化される
> 🧱 Given: 現在 `Game` クラスに `current_town` field がある（`GameState.current_town` も別途存在し、二重管理）。🎬 When: Game から削除し、参照箇所をすべて `game_state.current_town` に統一する。✅ Then: `grep -rnE 'game\.current_town\b\|self\.current_town\b' src/runtime/app.py` がマッチ 0 件。`game_state.current_town` への参照だけになり、二重管理が解消する。pytest 全 green。

### シナリオ2：`cam_x` / `cam_y` が ExploreModel または ViewportService へ移送される
> 🧱 Given: 現在 `Game.cam_x` / `Game.cam_y` を ExplorePresenter が更新している。🎬 When: 移送先（ExploreModel か新 ViewportService のどちらか）を Design で確定し、field を移送する。✅ Then: `grep -rnE 'game\.cam_x\|self\.cam_x' src/runtime/app.py` が 0 件。Explore 描画のカメラ追従挙動は維持。pytest 全 green。

### シナリオ3：`state` / `prev_state` が SceneManager に移送される
> 🧱 Given: 現在 `Game.state` / `Game.prev_state` が src/ 全域から参照されている（最大の影響範囲）。🎬 When: 新規 `SceneManager` を導入し、参照を `scene_manager.state` 等に書き換える。✅ Then: `grep -rnE 'game\.state\b\|self\.state\b' src/runtime/app.py` が 0 件。シーン切替（splash / title / map / town_menu / shop / battle / menu）が pytest と既存 cjg test 群で全 green。

### シナリオ4：`debug_mode` / `debug_seq` が DebugService に移送される
> 🧱 Given: 現在 `Game.debug_mode` / `Game.debug_seq` がデバッグキー入力で操作されている。🎬 When: 新規 `DebugService` を導入し、field と関連ロジックを移送する。✅ Then: `Game` クラスから `debug_mode` / `debug_seq` field が消え、デバッグキー操作（F1 等）が新 service 経由で動作する。pytest 全 green。

### シナリオ5：`dungeon_rooms` が WorldGenerationService の cache に移送される
> 🧱 Given: 現在 `Game.dungeon_rooms` が `dungeon_template` と並んで持たれている（生成時の中間物）。🎬 When: `WorldGenerationService` の結果 cache に移送する。✅ Then: `Game` から `dungeon_rooms` field が消え、ダンジョン room 情報が必要な箇所（dungeon_spawn 計算等）が service 経由で取得できる。pytest 全 green。

### シナリオ6：Game クラスが「ランタイム殻」相当に縮小されている
> 🧱 Given: 改修完了後の `src/runtime/app.py`。🎬 When: Game クラスの dataclass field 一覧を確認する。✅ Then: シナリオ1〜5 で移送した 7 field がすべて消えている。残るのは `pyxel.run` 配線に必要な最小限（`game_state`, 各 scene インスタンス, image_banks, sfx, audio, messages, input_state 等の DI 受け先）だけ。framework-rule.md M4-3「Game は最終的にランタイム殻にする」が実装に追いついている。

### シナリオ7：再侵入を防ぐ静的ガード
> 🧱 Given: 改修完了後、将来のコードで `Game.state` / `Game.cam_x` 等が復活する懸念。🎬 When: `test_cjg_framework_rule_guards.py` に「Game クラスの dataclass field が許可リスト外なら fail」する規約 test を追加する。✅ Then: 移送した 7 field を Game に書き戻す変更が pytest で即 fail する。Journey の After「役割が分担されている」が将来も保たれる。

### シナリオ8：5 ループの段階移行が独立 commit で revert 可能
> 🧱 Given: 各サブタスク（current_town / cam / state / debug / dungeon_rooms）がそれぞれ独立 commit。🎬 When: 任意の 1 commit を `git revert` する。✅ Then: 他のサブタスクへの影響なしで巻き戻せる。1 commit で複数 field を混在させない設計を Tasklist で守る。

## 3) Design

### 事前計測（2026-05-05 grep 実測値）

| Field | 参照件数 | 主な所在 |
|---|---|---|
| `(game\|self).state` | **66 件** | runtime/scenes 全域に散在（最大スコープ） |
| `(game\|self).prev_state` | 6 件 | runtime/app + 数 scene |
| `(game\|self).cam_x` / `cam_y` | **20 件** | `runtime/app.py:105-106`（初期化） + `scenes/explore/{presenter,view_model}.py` のみ（Explore 専用） |
| `(game\|self).current_town` | 11 件 | `runtime/app.py:94`（init 重複）+ `explore/presenter.py:133`（書き）+ `town/presenter.py:172`（None リセット）+ `shop/scene.py:30,35,36`（読み）+ `town/presenter.py:30,42,131`（index 計算用 read） |
| `dungeon_rooms` | 数件 | `runtime/app.py:80` + `explore/presenter.py:165` + `image_banks.py:151,154` |
| `debug_mode` / `debug_seq` | 着手時に grep | runtime + デバッグキー入力経路 |

### 移送先マトリクス（grep に基づき確定）

| Field | 移送先 | 確定根拠 |
|---|---|---|
| `current_town` | **GameState（既存 field を真値に統一、Game の field を撤去）** | 既に `GameState.current_town: TownContext \| None` 存在。`runtime/app.py:94` のコメント「GameState 完全統合後は game_state.current_town に移す」も同方向 |
| `cam_x` / `cam_y` | **`ExploreModel`** に確定 | 参照 20 件すべて Explore + runtime 初期化のみ。他 scene 未使用なので ViewportService（新 service）の正当化が無い |
| `state` / `prev_state` | **`SceneManager`（新設）**。**state holder のみ**（state machine ではない） | 既存 `_change_state(s)` 等の遷移メソッドは `app.py` に残置。SceneManager は `current: str` / `previous: str` の 2 field と単純な `set(s)` メソッドだけ持つ最小実装 |
| `debug_mode` / `debug_seq` | **`DebugService`（新設）**、**state-only** | 入力読み取り（`pyxel.btnp(F1)` 等）は `runtime/app.py:update()` 内に残置（Service 側で pyxel API を触らない＝M1 維持）。Service は `mode: bool` / `seq: list` を保持し、`runtime` から状態更新だけ受ける |
| `dungeon_rooms` | **GameState に統合**（cache 化はオーバーキル） | dungeon は 1 個前提なので key 設計が無く cache 化の正当化が無い。`game_state.dungeon_rooms: list = field(default_factory=list)` を新設し `Game.dungeon_rooms` を撤去 |

### 進め方（5 ループ、依存少 → 多の順）

| ループ | 内容 | 影響範囲 | commit 単位 |
|---|---|---|---|
| 1 | `current_town`：`runtime/app.py:94` 削除、`game.current_town = ...` を `game.game_state.current_town = ...` に書換（または既存の `game.current_town` 動的属性を `__getattr__` 経由で GameState にフォワード） | 11 件 | 1 commit |
| 2 | `cam_x` / `cam_y`：`ExploreModel` に field 追加、`presenter.py` の `game.cam_x = ...` を `model.cam_x = ...` に書換、`view_model.py` も同様 | 20 件 | 1 commit |
| 3 | `dungeon_rooms`：`GameState.dungeon_rooms` 新設、`Game.dungeon_rooms` 撤去、参照書換（`image_banks.py:151,154` も含む） | 数件 | 1 commit |
| 4 | `debug_mode` / `debug_seq`：`DebugService` 新設、入力読み取りは `app.py` に残し state だけ Service に移送 | 着手時 grep | 1 commit |
| 5 | `state` / `prev_state`：`SceneManager` 新設（最小実装）、66 + 6 = 72 箇所書換 | **最大スコープ**、複数 PR 候補 | 1 commit（または PR 内で複数 commit） |

順序の理由：`current_town`（既存 field 流用）→ `cam`（Explore に閉じる）→ `dungeon_rooms`（小規模）→ `debug`（新 service だが state 限定）→ `state`（最大、最後に変更スコープが見える状態でやる）。

### 新 service の責務粒度（明示）

| Service | field | メソッド | 持たないもの |
|---|---|---|---|
| `SceneManager` | `current: str`, `previous: str` | `set(next: str) -> None`（previous = current; current = next） | 遷移 validation、scene 起動コールバック、pyxel API |
| `DebugService` | `mode: bool`, `seq: list[str]` | `toggle()`, `record(key: str)`, `reset()` | 入力読み取り（`pyxel.btnp` は `app.py` に残置）、描画 |

### Game クラス許可リストの所在

- **test 内ハードコード**：`test_cjg_framework_rule_guards.py` 内に `ALLOWED_GAME_FIELDS = {...}` を持つ
- ガード test：`@dataclass` field 一覧が許可リストの subset であることを `dataclasses.fields(Game)` で検証
- docs/framework-rule.md M4-3 の「Game は最終的にランタイム殻」記述と test の許可リストを **手動同期**（自動化はオーバーキル、5 ループ完了時に 1 度更新するだけ）

### test 影響（commit 5 のリスク）

- `state` 66 件書換のうち test 側参照（`game.state` 直読）は Discussion に件数記録 → 別タスク or 同 PR 内で書換判断
- 着手時に `grep -rnE '(game|self)\.state\b' test/` で実測

### commit 戦略

- **1 ループ = 1 commit**（シナリオ8 revert 独立性を満たす）
- ループ5（state/prev_state）は影響範囲が最大なので、PR 単位は分けて中間 review を入れる選択肢を残す
- 各 commit 直前に pre-commit pytest 全 green 確認

### 関連スキル・MCP
- 標準ツール：Bash / Edit / Grep / pytest

### 委任度
🟡 中：ループ1〜4 は影響範囲が確定しているので 🟢 高、ループ5 は state 66 件書換 + scene 切替動作の手動検証が必要で 🔴 低。**ループ単位で委任度を分ける**。新 service の責務粒度（上表）はユーザー確認推奨。

## 4) Tasklist

（着手時にループ別に詳細化）

## 5) Result / 6) Discussion

（着手時に追記）
