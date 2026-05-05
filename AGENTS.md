# AGENTS.md — Block Quest Pyxel の作業ルール（AI 用最優先・自動 load）

> **役割**: AI がこの repo に入って最初に読む 100 行以内のエントリポイント。
> **補足（人用詳細）**: [docs/architecture.md](docs/architecture.md)
> **規約本体（M1〜M5）**: [docs/framework-rule.md](docs/framework-rule.md)
>
> 起動時は本ファイル → 必要なら architecture.md → 必要なら framework-rule.md の順に辿る。

## いちばん大事な約束

製品の根本価値は **子どもがゲームを編集できる** こと。`Pyxel Code Maker` は子どもの正式な編集面。Code Maker を不要 / 脇役 / 廃止する方向に勝手に話を進めない。tilemap / sprite / sound / .pyxres の編集面を内部都合で置き換えない。子どもが見ているものが主語の問題では、その実物を最初の正として扱う。

## docs と code が食い違ったら

- code = 現在の実態 / docs = 守るべき要求
- ずれは **未実装 / バグ / 仕様ずれ**。「code があるから正しい」と考えない
- ずれは言い訳せず、どこがずれているかを明記する

## ユーザーへの向き合い方

- ユーザーに道具選びを押しつけない（道具選びは AI の責任）
- ユーザーが「まだ違う」と言ったら、まず現物を確認する（先に defending しない）
- AI の仕事は **ユーザー指示の技術翻訳**

## まず何を正とするか（実物優先）

| 問題の主語 | 最初に見るもの |
|---|---|
| `Code Maker / Tilemap / Sprite / Sound / .pyxres` | `pyxel` MCP で resource 実体 |
| Web ページ / 公開 URL | ブラウザ / 実 endpoint |
| build 生成物 / zip / 配布物 | 出来上がったファイルの中身 |
| save/load | 実際の save payload |
| ゲーム画面の動き | 実行画面 / 実機 |

`runtime code を直した` `build script を直した` だけで終わらない。zip / .pyxres / HTML / save data の **実物** を見る。

## `.pyxres` の扱い

- 子ども/親が `Code Maker` で編集する。AI は code/build/packaging/guardrail/test を整える
- AI が `.pyxres` の中身をテキスト編集しない / 実体を直接いじる依頼を抱え込まない
- `pyxel` MCP で調べる・Code Maker 互換 build を直すのは責務
- `runtime が .pyxres を自動更新する設計` は特に慎重に（`CJ26` / `CJG23/24/26/37/41` 確認）

## 実装の事実

- runtime 入口：root `main.py` (8 行 wrapper) → `src/runtime/main_runtime.py` (47 行 shim) → **`src/runtime/app.py::Game`**（pyxel 初期化＋全 Scene/Service の組み立て＋update/draw dispatcher、326 行）
- 共有 state：`GameState`（dataclass）／`SceneManager`（current/previous の 2 値 state holder、`shared/services/scene_manager.py`）／`DebugService`（mode/UUDD seq）／`PlayerModel`（`shared/state/player_model.py`）
- M4-3 段階移行：`Game.current_town / debug_mode / state / prev_state` は @property forward。`Game.__init__` で `self.X = ...` 直接初期化すると static guard で fail
- `src/app.py::BlockQuestApp` は Phase 1 由来の legacy shell（test/Code Maker bundler 互換のため残置）
- pyxres = SSoT：`ImageBanks` は **書き込み・初期化・fallback のみ**（`regenerate_world_tilemap_fallback` 等）。Model は `pyxel.tilemaps[0]` / `pyxel.images[n]` を直読
- 配布物：`production/pyxel.html / .pyxapp / code-maker.zip`、`index.html` は子ども向けトップ（Phase 3 で dev/prod 分離廃止、本番一本化）

## まず読む文書（順序）

1. 本ファイル（AGENTS.md）
2. 必要に応じ `docs/architecture.md`（人用詳細・ディレクトリ規約）
3. 必要に応じ `docs/framework-rule.md`（M1〜M5 規約本体）
4. `docs/customer-journeys.md` / `docs/product-requirements-*.md` / 関係 `steering/`

## コード階層規約（M1〜M5 サマリ）

詳細は `docs/framework-rule.md`。実装前に該当 M 番号を確認。

1. **M1**: Pyxel API と入力は **View と最外殻** の 1 か所に閉じる
2. **M2**: View は **ViewModel** しか見ない（Model / GameState 直参照禁止）
3. **M3**: Presenter は **入力解釈・Scene 遷移・副作用指揮** のみ
4. **M4**: Model は **dataclass** 中心、共有状態は GameState / SceneModel / ServiceState を明示
5. **M5**: 層規約は AI が自力で検証できる形（命名・テスト・ガードレール）

### 実装ルール抜粋

- View 以外で `pyxel.*` 描画系を呼ばない（M1-1）。読み取り系 `tilemaps[n].pget` は Model から OK（imagebank=DB）
- Model で副作用なし／Presenter で直接描画なし／View は Model 直参照なし
- 新規 state は `dataclass`（dict 禁止）。共有 state は GameState / SceneModel / ServiceState を明示
- 副作用は command / request として返す。1 PR で Scene 構造とゲームルールを同時大改造しない

## データの流れ

```text
assets/*.yaml -> tools/gen_data.py -> src/generated/*.py -> src/game_data.py -> main.py
```

| Path | 理由 | 代わりに |
|---|---|---|
| `src/generated/*.py` | YAML から自動生成 | `assets/*.yaml` を直して `python tools/gen_data.py` |
| `*.pyxres` | Code Maker 編集物 | Code Maker で編集、AI は build/verify で支える |
| `from src.generated.*` import | loader 経由前提 | `from src.game_data import ENEMIES` |

## 変更したら毎回

```bash
python tools/gen_data.py    # YAML を変えたとき
python -m pytest test/ -q
```

テストが落ちたらそのままにしない。「docs だけだからテスト不要」と決めつけない。

## done の意味

`done` = コードがある + テストが通る + **人がタイトルを見て自然に期待する状態**。実物確認まで含む。
