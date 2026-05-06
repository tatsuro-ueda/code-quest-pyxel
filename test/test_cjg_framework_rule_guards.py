"""CJG/crash regression: framework-rule.md M1〜M5 を grep / find で守る。

根拠:
- docs/framework-rule.md M1〜M5（5 メタルール）
- docs/product-requirements-guardrails.md（PRD 側で同じ M1〜M5 を参照）
- docs/customer-jobs.md Make3「ガードレール: クラッシュで好循環が途絶」

規約違反の多くは「落ちるバグの温床」になる（例: M4-1 違反の `player` dict が残ると
attribute 風と dict 風の混在で AttributeError / KeyError の両方を踏む）。
framework-rule.md の Scenario に対応する grep / find を pytest に落として、
違反が src/ に 1 件でも入ったら fail させる。

Pyxel 描画や音声のランタイムは headless で守れないので、本ファイルは **静的チェック**
（grep / find）に徹する。シナリオ4 撤収条件の適用。
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SRC = ROOT / "src"

# 特定ディレクトリに限定するか、src 全域をスキャンするかを明示するために
# 反復系の置換対象を集中管理する。
SCENE_DIRS = sorted((SRC / "scenes").iterdir()) if (SRC / "scenes").exists() else []


def _iter_py_files(base: Path):
    for path in base.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _grep(pattern: re.Pattern, files) -> list[tuple[Path, int, str]]:
    """対象ファイル群から pattern にマッチする行を (path, lineno, line) として返す。"""
    hits: list[tuple[Path, int, str]] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if pattern.search(line):
                hits.append((path, lineno, line))
    return hits


class M1PyxelBoundaryTest(unittest.TestCase):
    """M1-1: Pyxel **描画系 API** を直接呼んでよいのは View 層だけ。

    2026-05-05 改訂：読み取り系 API（pyxel.tilemaps[n].pget /
    pyxel.images[n].pget）は Model から直呼び OK（ImageBank=DB として）。
    禁止対象は描画系のみに絞る。
    """

    # 描画系 API（blt / bltm / text / line / rect / circ / cls / pset 等）。
    # 読み取り系（pget）と入力系（btn / btnp）は別ルールで管理する。
    PYXEL_DRAW_CALL = re.compile(
        r"(?:^|[^_a-zA-Z])pyxel\."
        r"(blt|bltm|text|line|rect|rectb|circ|circb|cls|pset|tri|trib|clip|camera)\b"
    )

    def test_no_pyxel_draw_calls_in_scene_models(self):
        """src/scenes/*/model.py に pyxel.* 描画系直呼びが無い。読み取り系 pget は許可。"""
        target_files = [
            d / "model.py" for d in SCENE_DIRS
            if d.is_dir() and (d / "model.py").exists()
        ]
        hits = _grep(self.PYXEL_DRAW_CALL, target_files)
        self.assertEqual(
            hits, [],
            f"scenes/*/model.py に pyxel.* 描画系直呼び: {hits}",
        )

    def test_no_pyxel_draw_calls_in_scene_presenters(self):
        """src/scenes/*/presenter.py に pyxel.* 描画系直呼びが無い。"""
        target_files = [
            d / "presenter.py" for d in SCENE_DIRS
            if d.is_dir() and (d / "presenter.py").exists()
        ]
        hits = _grep(self.PYXEL_DRAW_CALL, target_files)
        self.assertEqual(
            hits, [],
            f"scenes/*/presenter.py に pyxel.* 描画系直呼び: {hits}",
        )

    def test_no_pyxel_draw_calls_in_player_model(self):
        """PlayerModel は Pyxel 描画系を知らない（M4-1 + M1-1）。"""
        path = SRC / "shared" / "state" / "player_model.py"
        if not path.exists():
            self.skipTest("player_model.py が未整備")
        hits = _grep(self.PYXEL_DRAW_CALL, [path])
        self.assertEqual(hits, [], f"player_model.py に pyxel.* 描画系直呼び: {hits}")

    # M1-1 例外規定 (2026-05-06 明文化)：
    #   - audio_system.py: Audio ラッパ
    #   - image_banks.py: Resource ラッパ (pyxres ロード/保存、image bank/tilemap 書込)
    # それ以外の services/*.py で pyxel.* 描画系を直呼びしてはいけない。
    SERVICES_PYXEL_EXEMPT = frozenset({"audio_system.py", "image_banks.py"})

    def test_no_pyxel_draw_calls_in_shared_services_except_resource_audio(self):
        """src/shared/services/*.py で pyxel 描画系直呼びは Audio / Resource ラッパ以外 0 件。

        2026-05-06 改訂で M1-1 例外を Audio / Resource ラッパに限定し、
        message_display / vfx 等の UI 描画は shared/ui/ へ物理移動した。
        """
        services_dir = SRC / "shared" / "services"
        target_files = [
            p for p in services_dir.glob("*.py")
            if p.name not in self.SERVICES_PYXEL_EXEMPT
        ]
        hits = _grep(self.PYXEL_DRAW_CALL, target_files)
        self.assertEqual(
            hits, [],
            f"shared/services/*.py (例外 {sorted(self.SERVICES_PYXEL_EXEMPT)} 以外) "
            f"に pyxel 描画系直呼び: {hits}",
        )


class M2ViewInputTest(unittest.TestCase):
    """M2-1: View は入力を見ない（ViewModel のみ受け取る）。"""

    INPUT_CALL = re.compile(r"(pyxel\.btnp|pyxel\.btn[^_]|input_state\.btnp|input_state\.btn[^_])")

    def test_no_input_reads_in_scene_views(self):
        """src/scenes/*/view.py / view_model.py に入力取得が無い。"""
        target_files: list[Path] = []
        for d in SCENE_DIRS:
            if not d.is_dir():
                continue
            for name in ("view.py", "view_model.py"):
                p = d / name
                if p.exists():
                    target_files.append(p)

        hits = _grep(self.INPUT_CALL, target_files)
        self.assertEqual(
            hits, [],
            f"view / view_model で入力を取得している: {hits}",
        )


class M3PresenterDrawingTest(unittest.TestCase):
    """M3-1: Presenter は描画しない（`pyxel.text` / `pyxel.rect` 等は View へ）。"""

    DRAW_CALL = re.compile(r"pyxel\.(text|rect|rectb|blt|bltm|cls|line|circ|circb|pset)")

    def test_no_draw_calls_in_scene_presenters(self):
        target_files = [
            d / "presenter.py" for d in SCENE_DIRS
            if d.is_dir() and (d / "presenter.py").exists()
        ]
        hits = _grep(self.DRAW_CALL, target_files)
        self.assertEqual(
            hits, [],
            f"presenter.py で直接描画している: {hits}",
        )


class M4PlayerDictBanTest(unittest.TestCase):
    """M4-1 / M4-4 Level 2: player dict 禁止（PlayerModel のみが正本）。"""

    GAME_PLAYER = re.compile(r"game\.player(?!_model)(?:[^_a-zA-Z0-9]|$)")
    PLAYER_DICT_BRACKET = re.compile(r"\bplayer\s*\[\s*['\"]")

    def test_no_game_player_attribute_reads_in_src(self):
        """src/ 配下に `game.player` の dict 風参照が残っていない。

        許可: `game.player_model` のみ。2026-04-25 の crash を再発させないため、
        import や docstring 含めて word-boundary で検出する。
        """
        files = [
            p for p in _iter_py_files(SRC)
            # 古い shim（backward-compat 用 module 名を知っている）や
            # 生成ファイルは除外する。現時点では player_state.py に残存する
            # 「PlayerModel へ委譲するだけ」の shim も含めてチェックする。
            if "generated" not in p.parts
        ]
        hits = _grep(self.GAME_PLAYER, files)
        self.assertEqual(
            hits, [],
            f"game.player dict 風参照が残っている: {[(str(h[0].relative_to(ROOT)), h[1], h[2].strip()) for h in hits]}",
        )

    def test_no_player_dict_bracket_access_in_scenes(self):
        """scenes/ 配下に `player["key"]` / `player['key']` が残っていない。"""
        scene_files = [p for d in SCENE_DIRS if d.is_dir() for p in _iter_py_files(d)]
        hits = _grep(self.PLAYER_DICT_BRACKET, scene_files)
        self.assertEqual(
            hits, [],
            f"scenes/ で player dict 風アクセス: {[(str(h[0].relative_to(ROOT)), h[1], h[2].strip()) for h in hits]}",
        )


class M4ShopSsotTest(unittest.TestCase):
    """M4-4 相当の追加ガード: generated/ の SSoT を scene が直接 import しない。"""

    SHOPS_DIRECT = re.compile(r"M\.SHOPS\b|\bSHOPS\s*\[")
    GENERATED_IMPORT = re.compile(r"from\s+src\.generated\.")

    def test_scenes_do_not_reference_raw_shops_dict(self):
        """M.SHOPS[idx] のような生参照は KeyError の温床（2026-04-25 の bug）。"""
        scene_files = [p for d in SCENE_DIRS if d.is_dir() for p in _iter_py_files(d)]
        hits = _grep(self.SHOPS_DIRECT, scene_files)
        self.assertEqual(
            hits, [],
            f"scenes/ で SHOPS 辞書を直接参照: {[(str(h[0].relative_to(ROOT)), h[1], h[2].strip()) for h in hits]}",
        )

    def test_scenes_do_not_import_from_src_generated(self):
        """generated/ は src/game_data.py で unpack された名前を介してのみ触る。"""
        scene_files = [p for d in SCENE_DIRS if d.is_dir() for p in _iter_py_files(d)]
        hits = _grep(self.GENERATED_IMPORT, scene_files)
        self.assertEqual(
            hits, [],
            f"scenes/ から generated/ を直接 import: {[(str(h[0].relative_to(ROOT)), h[1], h[2].strip()) for h in hits]}",
        )


class M5SceneStructureTest(unittest.TestCase):
    """M5-1: scene ディレクトリの構造規約（scene.py / model.py / presenter.py / view.py 群）。"""

    ALLOWED_FILES = {
        "__init__.py", "scene.py", "model.py", "presenter.py", "view.py", "view_model.py",
    }

    def test_each_scene_dir_has_minimum_mpv_files(self):
        """各 scenes/*/ は model / presenter / view を最低限持つ。"""
        for d in SCENE_DIRS:
            if not d.is_dir() or d.name.startswith("__"):
                continue
            with self.subTest(scene=d.name):
                for required in ("model.py", "presenter.py", "view.py"):
                    self.assertTrue(
                        (d / required).exists(),
                        f"{d.name}/{required} が存在しない（M5-1 命名規約違反）",
                    )

    def test_no_unexpected_files_in_scene_dirs(self):
        """scenes/*/ に `ALLOWED_FILES` 以外の .py が混在していない。"""
        for d in SCENE_DIRS:
            if not d.is_dir() or d.name.startswith("__"):
                continue
            with self.subTest(scene=d.name):
                unexpected = [
                    p.name for p in d.iterdir()
                    if p.suffix == ".py" and p.name not in self.ALLOWED_FILES
                ]
                self.assertEqual(
                    unexpected, [],
                    f"{d.name}/ に規約外の .py: {unexpected}",
                )


class M4SsotGuardTest(unittest.TestCase):
    """M4: snapshot field の再侵入を防ぐ静的ガード。

    `game.world_map` / `self.world_map` 仕込みは 2026-05-05 に撤去済
    （pyxres = SSoT に統一）。再侵入を pytest で即 fail させる。
    """

    WORLD_MAP_PATTERN = re.compile(r"\b(?:game|self)\.world_map\b")

    def test_no_world_map_field_assignment_in_src(self):
        """src/ 配下に `(game|self).world_map` の参照がない。

        pyxres を SSoT 化し、`GameState.world_map` フィールドと
        `self.world_map` 初期化を撤去した（2026-05-05）。動的属性として
        復活させると "2 つの真実が並走" 状態に戻るため禁止。
        """
        hits = _grep(self.WORLD_MAP_PATTERN, _iter_py_files(SRC))
        self.assertEqual(
            hits, [],
            f"src/ に `(game|self).world_map` 参照が侵入: {hits}",
        )

    def test_no_world_map_field_assignment_in_tests(self):
        """test/ 配下に world_map field 代入がない。

        ExploreModel が pyxel.tilemaps[0].pget を直読する新仕様
        （2026-05-05）に対し、 game の world_map field 仕込みは
        無効（dead code）になる。混乱の元なので test 内でも禁止する。
        """
        test_dir = ROOT / "test"
        pattern = re.compile(r"\b(?:game|self)\.world_map\s*=")
        files = [p for p in _iter_py_files(test_dir) if p != Path(__file__)]
        hits = _grep(pattern, files)
        self.assertEqual(
            hits, [],
            f"test/ に world_map field 代入が侵入: {hits}",
        )

    DUNGEON_MAP_PATTERN = re.compile(r"\b(?:game|self)\.dungeon_map\b")

    def test_no_dungeon_map_field_in_src(self):
        """src/ 配下に `(game|self).dungeon_map` の参照がない。

        dungeon の入退出は player_model.in_dungeon フラグと
        GameState.dungeon_spawn だけで完結する（2026-05-05）。snapshot
        field を復活させると "in_dungeon と dungeon_map の両方を見る"
        混乱が再発するため禁止。
        """
        hits = _grep(self.DUNGEON_MAP_PATTERN, _iter_py_files(SRC))
        self.assertEqual(
            hits, [],
            f"src/ に `(game|self).dungeon_map` 参照が侵入: {hits}",
        )

    def test_no_dungeon_map_field_assignment_in_tests(self):
        """test/ 配下に dungeon_map field 代入がない。

        ExploreModel が pyxel.tilemaps[0].pget を直読する新仕様
        （2026-05-05）に対し、game の dungeon_map field 仕込みは
        無効（dead code）になる。混乱の元なので test 内でも禁止する。
        新規 test は `test/_helpers/imagebank_stub.py::stub_explore_tilemap_read`
        を使うこと。
        """
        test_dir = ROOT / "test"
        pattern = re.compile(r"\b(?:game|self)\.dungeon_map\s*=")
        files = [p for p in _iter_py_files(test_dir) if p != Path(__file__)]
        hits = _grep(pattern, files)
        self.assertEqual(
            hits, [],
            f"test/ に dungeon_map field 代入が侵入: {hits}",
        )

    DEPRECATED_GAME_FIELDS = frozenset({
        "current_town", "cam_x", "cam_y", "dungeon_rooms", "dungeon_map",
        "debug_mode", "debug_seq", "state", "prev_state", "world_map",
    })

    def test_agents_md_is_within_100_lines(self):
        """AGENTS.md は AI 用最優先・自動 load 文書として ≤100 行に保つ。

        Code Maker / Claude Code 起動時に context として読み切れるサイズを
        守るため、100 行を超えたら fail (M5-3 の 2 層文書構造を維持)。
        """
        agents_path = ROOT / "AGENTS.md"
        self.assertTrue(agents_path.exists(), "AGENTS.md が存在しない")
        line_count = sum(1 for _ in agents_path.read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(
            line_count, 100,
            f"AGENTS.md が {line_count} 行 (制限 100 行)。M5-3 文書 2 層構造に従い圧縮要",
        )

    def test_docs_architecture_md_exists(self):
        """人用詳細リファレンス docs/architecture.md が存在する（M5-3）。

        2026-05-05: docs/repository-structure.md からリネームして
        AGENTS.md の補足として位置付けた。
        """
        arch_path = ROOT / "docs" / "architecture.md"
        self.assertTrue(arch_path.exists(), "docs/architecture.md が存在しない")

    def test_game_init_does_not_directly_initialize_deprecated_fields(self):
        """Game.__init__ で M4-3 段階移行済みの field を直接初期化していないこと。

        2026-05-05 改訂：current_town → GameState、cam_x/y → ExploreModel、
        debug_mode/seq → DebugService、state/prev_state → SceneManager、
        world_map / dungeon_map / dungeon_rooms は撤去済。
        Game クラスを「ランタイム殻」に保つため、これらの直接初期化が
        復活したら即 fail させる（@property フォワードは許可）。
        """
        import ast as _ast
        path = SRC / "runtime" / "app.py"
        source = path.read_text(encoding="utf-8")
        tree = _ast.parse(source)
        init_node = None
        for node in _ast.walk(tree):
            if isinstance(node, _ast.ClassDef) and node.name == "Game":
                for item in node.body:
                    if isinstance(item, _ast.FunctionDef) and item.name == "__init__":
                        init_node = item
                        break
        self.assertIsNotNone(init_node, "Game.__init__ が見つからない")
        direct_fields: set[str] = set()
        for stmt in _ast.walk(init_node):
            if isinstance(stmt, _ast.Assign):
                for target in stmt.targets:
                    if (
                        isinstance(target, _ast.Attribute)
                        and isinstance(target.value, _ast.Name)
                        and target.value.id == "self"
                    ):
                        direct_fields.add(target.attr)
        violations = direct_fields & self.DEPRECATED_GAME_FIELDS
        self.assertEqual(
            violations, set(),
            f"Game.__init__ で deprecated field を直接初期化: {sorted(violations)}",
        )


class TopChangesAutoUpdateGuardTest(unittest.TestCase):
    """commit log → top_changes.json → kid-pixel index.html のパイプラインを守る。

    2026-05-06: index.html を build から切り離し、post-commit hook で
    Anthropic API による解釈 → top_changes.json 自動追記 → render に変更。
    将来「make build が index.html を上書きする」regression を構造的に防ぐ。
    """

    INDEX_HTML = ROOT / "index.html"
    TOP_CHANGES_JSON = ROOT / "top_changes.json"
    BUILD_WEB_RELEASE = ROOT / "tools" / "build_web_release.py"

    def test_g1_build_web_release_does_not_write_index_html(self):
        """G1: build_web_release.py に index.html を出力するコードが無い。

        旧 regression：tools/build_web_release.py L123-130 が
        `index_path = output_dir / "index.html"` + `shutil.copy2(selector_path, index_path)`
        で kid-pixel index.html (645 行) を 111 行 selector で上書きしていた。
        この commit で削除済。再侵入したら即 fail。
        """
        if not self.BUILD_WEB_RELEASE.exists():
            self.skipTest("tools/build_web_release.py が無い")
        text = self.BUILD_WEB_RELEASE.read_text(encoding="utf-8")
        # `output_dir / "index.html"` の代入と shutil.copy2(... index_path) の組み合わせを検出
        forbidden = re.compile(r'(output_dir|root)\s*/\s*[\'"]index\.html[\'"]')
        hits = forbidden.findall(text)
        self.assertEqual(
            hits, [],
            f"build_web_release.py に index.html 出力コードが残っている: {hits}",
        )

    def test_g2_index_html_has_top_changes_markers(self):
        """G2: index.html に TOP_CHANGES_START / END マーカーがペアで存在する。"""
        self.assertTrue(self.INDEX_HTML.exists(), "index.html が見つからない")
        text = self.INDEX_HTML.read_text(encoding="utf-8")
        self.assertIn("<!-- TOP_CHANGES_START -->", text, "TOP_CHANGES_START マーカー欠落")
        self.assertIn("<!-- TOP_CHANGES_END -->", text, "TOP_CHANGES_END マーカー欠落")
        # ペアの順序確認（START が END より前にある）
        start_idx = text.index("<!-- TOP_CHANGES_START -->")
        end_idx = text.index("<!-- TOP_CHANGES_END -->")
        self.assertLess(start_idx, end_idx, "TOP_CHANGES マーカーの順序が逆転")

    def test_g3_top_changes_json_is_valid(self):
        """G3: top_changes.json が valid JSON で `changes` キーが list[str]。"""
        import json
        self.assertTrue(self.TOP_CHANGES_JSON.exists(), "top_changes.json が無い")
        data = json.loads(self.TOP_CHANGES_JSON.read_text(encoding="utf-8"))
        self.assertIn("changes", data, "top_changes.json に 'changes' キーが無い")
        self.assertIsInstance(data["changes"], list, "'changes' が list ではない")
        for entry in data["changes"]:
            self.assertIsInstance(entry, str, f"changes エントリが str でない: {entry!r}")


if __name__ == "__main__":
    unittest.main()
