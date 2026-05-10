from __future__ import annotations

"""architecture_rules.yml の deterministic rule を warning 形式で検証する CLI。"""

import argparse
import json
import re
import shlex
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[2]
VALID_DETERMINISTIC_REVIEWS = {
    "implemented",
    "candidate",
    "keep_llm_assisted",
    "keep_manual",
}
VALID_REPAIR_AUTOFIX = {
    "implemented",
    "candidate",
    "not_recommended",
}
PRIMARY_AUTOFIX_KEY = "guardian_autofix"
LEGACY_AUTOFIX_KEYS = (PRIMARY_AUTOFIX_KEY, "repair_autofix")


@dataclass
class CheckContext:
    repo_root: Path
    rules_path: Path
    data: dict[str, Any]


@dataclass
class CheckOutcome:
    status: str
    checked_paths: list[str]
    failed_checks: list[str] = field(default_factory=list)
    message: str | None = None
    suggested_actions: list[str] = field(default_factory=list)
    reason: str | None = None
    expected: dict[str, Any] | None = None
    observed: dict[str, Any] | None = None


def load_rules(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("architecture rules YAML must parse to a dict")
    for key in ("meta", "facts", "validation_rules"):
        if key not in data:
            raise KeyError(f"missing top-level key: {key}")
    # checker 本体は rule ごとの差分検出に集中させたいので、
    # 入口で YAML の骨格を先に落として異常系を早期に止める。
    validate_rules_schema(data)
    return data


def _coverage_autofix_key(coverage: dict[str, Any]) -> str | None:
    for key in LEGACY_AUTOFIX_KEYS:
        if key in coverage:
            return key
    return None

def validate_rules_schema(data: dict[str, Any]) -> None:
    tree = data.get("facts", {}).get("tree")
    if not isinstance(tree, dict):
        raise KeyError("facts.tree must be present")
    # facts.tree は repo 全体の基準木なので、root 形状が崩れた時点で
    # 個別 rule の判定を続けてもノイズしか増えない。
    if tree.get("path") != "." or tree.get("kind") != "root":
        raise ValueError("facts.tree must start with path='.' and kind='root'")
    contracts = data.get("facts", {}).get("codemaker_bundle_contracts", [])
    if contracts is not None:
        if not isinstance(contracts, list):
            raise TypeError("facts.codemaker_bundle_contracts must be a list")
        for contract in contracts:
            if not isinstance(contract, dict):
                raise TypeError("each codemaker bundle contract must be a dict")
            for key in ("id", "manifest_path", "required_paths"):
                if key not in contract:
                    raise KeyError(f"codemaker bundle contract missing key: {key}")
            if not isinstance(contract["required_paths"], list) or not contract["required_paths"]:
                raise TypeError("codemaker bundle contract required_paths must be a non-empty list")
    required_rule_keys = {
        "id",
        "summary",
        "severity",
        "enforcement",
        "scope",
        "evidence",
        "message",
        "suggested_actions",
        "coverage",
    }
    for rule in data["validation_rules"]:
        missing = required_rule_keys - set(rule)
        if missing:
            raise KeyError(f"rule {rule.get('id', '<unknown>')} missing keys: {sorted(missing)}")
        if not isinstance(rule["suggested_actions"], list):
            raise TypeError(f"rule {rule['id']} suggested_actions must be a list")
        if "mode" not in rule["enforcement"]:
            raise KeyError(f"rule {rule['id']} missing enforcement.mode")
        if not isinstance(rule.get("scope", {}).get("paths"), list):
            raise TypeError(f"rule {rule['id']} scope.paths must be a list")
        checks = rule.get("evidence", {}).get("checks")
        if not isinstance(checks, list) or not checks:
            raise TypeError(f"rule {rule['id']} evidence.checks must be a non-empty list")
        coverage = rule.get("coverage")
        if not isinstance(coverage, dict):
            raise TypeError(f"rule {rule['id']} coverage must be a dict")
        for key in ("deterministic_review", "next_checker_unit", "rationale"):
            if key not in coverage:
                raise KeyError(f"rule {rule['id']} coverage missing key: {key}")
        autofix_key = _coverage_autofix_key(coverage)
        if autofix_key is None:
            raise KeyError(
                f"rule {rule['id']} coverage missing key: {PRIMARY_AUTOFIX_KEY} (or legacy repair_autofix)"
            )
        if coverage["deterministic_review"] not in VALID_DETERMINISTIC_REVIEWS:
            raise ValueError(
                f"rule {rule['id']} coverage.deterministic_review must be one of "
                f"{sorted(VALID_DETERMINISTIC_REVIEWS)}"
            )
        next_checker_unit = coverage["next_checker_unit"]
        if next_checker_unit is not None and not isinstance(next_checker_unit, str):
            raise TypeError(f"rule {rule['id']} coverage.next_checker_unit must be a string or null")
        autofix_value = coverage[autofix_key]
        if autofix_value not in VALID_REPAIR_AUTOFIX:
            raise ValueError(
                f"rule {rule['id']} coverage.{autofix_key} must be one of "
                f"{sorted(VALID_REPAIR_AUTOFIX)}"
            )
        if not isinstance(coverage["rationale"], str) or not coverage["rationale"].strip():
            raise TypeError(f"rule {rule['id']} coverage.rationale must be a non-empty string")
        # deterministic rule は「実装した checker 名」と必ず 1 対 1 に対応させる。
        # ここが曖昧だと YAML 上では deterministic なのに実行不能という事故が起きる。
        if rule["enforcement"]["mode"] == "deterministic":
            for check_name in checks:
                if check_name not in CHECK_REGISTRY:
                    raise KeyError(f"rule {rule['id']} references unknown deterministic check: {check_name}")


def _scope_paths(rule: dict[str, Any]) -> list[str]:
    return list(rule.get("scope", {}).get("paths", []))


def iter_tree_nodes(node: dict[str, Any]):
    yield node
    for child in node.get("children", []):
        yield from iter_tree_nodes(child)


def find_tree_node(data: dict[str, Any], path_value: str) -> dict[str, Any] | None:
    for node in iter_tree_nodes(data["facts"]["tree"]):
        if node.get("path") == path_value:
            return node
    return None


def find_entry_point(data: dict[str, Any], entry_id: str) -> dict[str, Any] | None:
    entries = data.get("facts", {}).get("entry_points", [])
    return next((item for item in entries if item.get("id") == entry_id), None)


def generated_file_nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    nodes: list[dict[str, Any]] = []
    for node in iter_tree_nodes(data["facts"]["tree"]):
        path_value = node.get("path", "")
        if node.get("kind") == "file" and path_value.startswith("src/generated/"):
            nodes.append(node)
    return nodes


def distribution_artifact_nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    dist_node = find_tree_node(data, "dist")
    if dist_node is None:
        return []
    return [child for child in dist_node.get("children", []) if child.get("kind") == "file"]


def find_codemaker_bundle_contract(data: dict[str, Any], contract_id: str) -> dict[str, Any] | None:
    contracts = data.get("facts", {}).get("codemaker_bundle_contracts", [])
    return next((item for item in contracts if item.get("id") == contract_id), None)


def _warning(
    rule: dict[str, Any],
    checked_paths: list[str],
    failed_check: str,
    *,
    reason: str | None = None,
    expected: dict[str, Any] | None = None,
    observed: dict[str, Any] | None = None,
) -> CheckOutcome:
    message = rule.get("message")
    if reason:
        message = f"{message}: {reason}" if message else reason
    return CheckOutcome(
        status="warning",
        checked_paths=checked_paths,
        failed_checks=[failed_check],
        message=message,
        suggested_actions=list(rule.get("suggested_actions", [])),
        expected=expected,
        observed=observed,
    )


def _ok(rule: dict[str, Any], checked_paths: list[str]) -> CheckOutcome:
    return CheckOutcome(status="ok", checked_paths=checked_paths)


def _skipped(rule: dict[str, Any]) -> CheckOutcome:
    return CheckOutcome(
        status="skipped",
        checked_paths=_scope_paths(rule),
        reason="初版では deterministic rule のみ実行する",
    )


def _file_contains(path: Path, needle: str) -> bool:
    return needle in path.read_text(encoding="utf-8")


def _manifest_entries(path: Path) -> list[str]:
    entries: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        entries.append(line)
    return entries


SCENE_ALLOWED_FILES = {
    "__init__.py",
    "scene.py",
    "model.py",
    "presenter.py",
    "view.py",
    "view_model.py",
}
SCENE_DRAW_CALL = re.compile(
    r"(?:^|[^_a-zA-Z])pyxel\."
    r"(blt|bltm|text|line|rect|rectb|circ|circb|cls|pset|tri|trib|clip|camera)\b"
)
SCENE_INPUT_CALL = re.compile(r"(pyxel\.btnp|pyxel\.btn[^_]|input_state\.btnp|input_state\.btn[^_])")
PYXEL_ANY_CALL = re.compile(r"(?:^|[^_a-zA-Z])pyxel\.")
PLAYER_STATE_IMPORT = re.compile(
    r"from\s+src\.shared\.services\.player_state\s+import|import\s+src\.shared\.services\.player_state"
)
ITEM_USE_IMPORT = re.compile(
    r"from\s+src\.shared\.services\.item_use\s+import|import\s+src\.shared\.services\.item_use"
)
SHARED_SERVICE_PYXEL_EXEMPT = {"audio_system.py", "image_banks.py"}


def _iter_py_files(base: Path):
    if not base.exists():
        return
    for path in base.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        yield path


def _grep(pattern: re.Pattern[str], files: list[Path]) -> list[tuple[Path, int, str]]:
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


def _rel_hit(repo_root: Path, hit: tuple[Path, int, str]) -> str:
    path, lineno, line = hit
    return f"{path.relative_to(repo_root)}:{lineno}: {line.strip()}"


def scene_static_boundary_checks(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    scene_root = repo_root / "src" / "scenes"
    if not scene_root.is_dir():
        return _warning(rule, checked_paths, "scene_static_boundary_checks", reason="missing path: src/scenes")

    scene_dirs = sorted(p for p in scene_root.iterdir() if p.is_dir() and not p.name.startswith("__"))
    if not scene_dirs:
        return _warning(rule, checked_paths, "scene_static_boundary_checks", reason="src/scenes has no scene directories")

    # まず scene ディレクトリ構造そのものを検証する。
    # 構造が壊れている状態でレイヤ境界だけ見ても原因が読み取りにくいため。
    for scene_dir in scene_dirs:
        for required in ("model.py", "presenter.py", "view.py"):
            rel = f"src/scenes/{scene_dir.name}/{required}"
            if not (scene_dir / required).is_file():
                return _warning(
                    rule,
                    checked_paths,
                    "scene_static_boundary_checks",
                    reason=f"missing required scene file: {rel}",
                )
        if scene_dir.name == "town":
            if (scene_dir / "scene.py").exists():
                return _warning(
                    rule,
                    checked_paths,
                    "scene_static_boundary_checks",
                    reason="town/scene.py must not exist",
                )
        elif not (scene_dir / "scene.py").is_file():
            return _warning(
                rule,
                checked_paths,
                "scene_static_boundary_checks",
                reason=f"missing required scene file: src/scenes/{scene_dir.name}/scene.py",
            )
        unexpected = sorted(
            child.name
            for child in scene_dir.iterdir()
            if child.is_file() and child.suffix == ".py" and child.name not in SCENE_ALLOWED_FILES
        )
        if unexpected:
            return _warning(
                rule,
                checked_paths,
                "scene_static_boundary_checks",
                reason=f"unexpected python files in src/scenes/{scene_dir.name}: {unexpected}",
            )

    # 次に「どの層が pyxel を触っているか」を静的に洗う。
    # 最初の違反だけ返す設計なので、warning の指す場所が常に最短経路になる。
    model_hits = _grep(
        SCENE_DRAW_CALL,
        [scene_dir / "model.py" for scene_dir in scene_dirs if (scene_dir / "model.py").is_file()],
    )
    if model_hits:
        return _warning(
            rule,
            checked_paths,
            "scene_static_boundary_checks",
            reason=f"pyxel draw call in scene model: {_rel_hit(repo_root, model_hits[0])}",
        )

    presenter_hits = _grep(
        SCENE_DRAW_CALL,
        [scene_dir / "presenter.py" for scene_dir in scene_dirs if (scene_dir / "presenter.py").is_file()],
    )
    if presenter_hits:
        return _warning(
            rule,
            checked_paths,
            "scene_static_boundary_checks",
            reason=f"pyxel draw call in scene presenter: {_rel_hit(repo_root, presenter_hits[0])}",
        )

    view_like_files: list[Path] = []
    for scene_dir in scene_dirs:
        for name in ("view.py", "view_model.py"):
            path = scene_dir / name
            if path.is_file():
                view_like_files.append(path)
    input_hits = _grep(SCENE_INPUT_CALL, view_like_files)
    if input_hits:
        return _warning(
            rule,
            checked_paths,
            "scene_static_boundary_checks",
            reason=f"input read in scene view layer: {_rel_hit(repo_root, input_hits[0])}",
        )

    return _ok(rule, checked_paths)


def shared_directory_role_checks(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    services_root = repo_root / "src" / "shared" / "services"
    state_root = repo_root / "src" / "shared" / "state"
    if not services_root.is_dir():
        return _warning(rule, checked_paths, "shared_directory_role_checks", reason="missing path: src/shared/services")
    if not state_root.is_dir():
        return _warning(rule, checked_paths, "shared_directory_role_checks", reason="missing path: src/shared/state")

    # player_model.py は shared/state 側の SSoT として明示されているので、
    # facts 側の role/status が崩れていないかを先に点検する。
    player_model_node = find_tree_node(context.data, "src/shared/state/player_model.py")
    if player_model_node is not None:
        if player_model_node.get("role") != "player_source_of_truth" or player_model_node.get("status") != "active":
            return _warning(
                rule,
                checked_paths,
                "shared_directory_role_checks",
                reason="player_model.py facts are not aligned with source-of-truth role",
                expected={"path": "src/shared/state/player_model.py", "role": "player_source_of_truth", "status": "active"},
                observed={"role": player_model_node.get("role"), "status": player_model_node.get("status")},
            )
    for rel_path, expected_role in (
        ("src/shared/services/player_state.py", "legacy_player_snapshot"),
        ("src/shared/services/item_use.py", "legacy_item_use_bridge"),
    ):
        node = find_tree_node(context.data, rel_path)
        if node is not None and (node.get("status") != "legacy" or node.get("role") != expected_role):
            return _warning(
                rule,
                checked_paths,
                "shared_directory_role_checks",
                reason=f"{Path(rel_path).name} facts are not aligned with legacy bridge status",
                expected={"path": rel_path, "role": expected_role, "status": "legacy"},
                observed={"role": node.get("role"), "status": node.get("status")},
            )

    # facts 上の role 整合を見た後、実ファイルに pyxel や legacy bridge 参照が
    # 残っていないかを grep で二重確認する。
    for node in iter_tree_nodes(find_tree_node(context.data, "src/shared/services") or {"children": []}):
        if node.get("kind") != "file":
            continue
        role = str(node.get("role", ""))
        if role.endswith("_source_of_truth"):
            return _warning(
                rule,
                checked_paths,
                "shared_directory_role_checks",
                reason=f"service file keeps source-of-truth role: {node.get('path')}",
            )
    for node in iter_tree_nodes(find_tree_node(context.data, "src/shared/state") or {"children": []}):
        if node.get("kind") != "file":
            continue
        role = str(node.get("role", ""))
        if role.endswith("_bridge") or role.endswith("_state_holder"):
            return _warning(
                rule,
                checked_paths,
                "shared_directory_role_checks",
                reason=f"state file has service-like role: {node.get('path')}",
            )

    state_hits = _grep(PYXEL_ANY_CALL, list(_iter_py_files(state_root)))
    if state_hits:
        return _warning(
            rule,
            checked_paths,
            "shared_directory_role_checks",
            reason=f"pyxel access in shared/state file: {_rel_hit(repo_root, state_hits[0])}",
        )

    service_files = [
        path for path in services_root.glob("*.py")
        if path.name not in SHARED_SERVICE_PYXEL_EXEMPT
    ]
    service_hits = _grep(SCENE_DRAW_CALL, service_files)
    if service_hits:
        return _warning(
            rule,
            checked_paths,
            "shared_directory_role_checks",
            reason=f"pyxel draw call in shared/services file: {_rel_hit(repo_root, service_hits[0])}",
        )

    dependency_targets = list(_iter_py_files(repo_root / "src" / "runtime"))
    dependency_targets.extend(_iter_py_files(repo_root / "src" / "scenes"))
    player_state_hits = _grep(PLAYER_STATE_IMPORT, dependency_targets)
    if player_state_hits:
        return _warning(
            rule,
            checked_paths,
            "shared_directory_role_checks",
            reason=f"runtime/scenes import legacy player_state shim: {_rel_hit(repo_root, player_state_hits[0])}",
        )
    item_use_hits = _grep(ITEM_USE_IMPORT, dependency_targets)
    if item_use_hits:
        return _warning(
            rule,
            checked_paths,
            "shared_directory_role_checks",
            reason=f"runtime/scenes import legacy item_use bridge: {_rel_hit(repo_root, item_use_hits[0])}",
        )

    return _ok(rule, checked_paths)


def wrapper_chain_present(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    for rel_path in checked_paths:
        if not (repo_root / rel_path).exists():
            return _warning(rule, checked_paths, "wrapper_chain_present", reason=f"missing path: {rel_path}")

    # この rule は「facts に書いてある入口チェーン」と「実コード上の import/run 連鎖」の
    # 両方が一致して初めて OK とする。
    entry = find_entry_point(context.data, "runtime_entry_chain")
    if entry is None:
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="facts.entry_points.runtime_entry_chain is missing")
    entry_chain = list(entry.get("nodes", []))
    entry_paths = [item.get("path") for item in entry_chain]
    if entry_paths != checked_paths:
        return _warning(
            rule,
            checked_paths,
            "wrapper_chain_present",
            reason="facts.entry_points.runtime_entry_chain paths do not match scope",
            expected={"scope_paths": checked_paths},
            observed={"entry_chain_paths": entry_paths},
        )
    if entry_chain[-1].get("symbol") != "Game":
        return _warning(
            rule,
            checked_paths,
            "wrapper_chain_present",
            reason="runtime_game symbol is not Game",
            expected={"runtime_game_symbol": "Game"},
            observed={"runtime_game_symbol": entry_chain[-1].get("symbol")},
        )

    main_path = repo_root / "main.py"
    shim_path = repo_root / "src/runtime/main_runtime.py"
    app_path = repo_root / "src/runtime/app.py"

    if not _file_contains(main_path, "main_runtime.py"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="main.py does not point at runtime shim")
    if not _file_contains(main_path, "run()"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="main.py does not call run()")
    if not _file_contains(shim_path, "from src.runtime.app import Game"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime shim does not re-export Game")
    if not _file_contains(shim_path, "from src.runtime.app import run as _run"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime shim does not import run() from app")
    if not _file_contains(shim_path, "def run()"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime shim does not expose run()")
    if not _file_contains(app_path, "class Game"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime app does not define Game")
    if not _file_contains(app_path, "def run()"):
        return _warning(rule, checked_paths, "wrapper_chain_present", reason="runtime app does not define run()")

    return _ok(rule, checked_paths)


def distribution_paths_marked_non_source(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    dist_root = find_tree_node(context.data, "dist")
    if dist_root is None:
        return _warning(rule, checked_paths, "distribution_paths_marked_non_source", reason="dist root is missing from facts.tree")
    if dist_root.get("status") != "distribution":
        return _warning(
            rule,
            checked_paths,
            "distribution_paths_marked_non_source",
            reason="dist root status is not distribution",
            expected={"status": "distribution"},
            observed={"status": dist_root.get("status")},
        )
    if dist_root.get("source_of_truth") is not False:
        return _warning(
            rule,
            checked_paths,
            "distribution_paths_marked_non_source",
            reason="dist root source_of_truth is not false",
            expected={"source_of_truth": False},
            observed={"source_of_truth": dist_root.get("source_of_truth")},
        )
    if not (repo_root / "dist").exists():
        return _warning(rule, checked_paths, "distribution_paths_marked_non_source", reason="dist directory does not exist")
    return _ok(rule, checked_paths)


def generated_entries_mark_non_hand_editable_and_sources(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    entries = generated_file_nodes(context.data)
    if not (repo_root / "tools/gen_data.py").is_file():
        return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason="tools/gen_data.py is missing")

    for entry in entries:
        rel_path = entry.get("path")
        if not rel_path or not (repo_root / rel_path).is_file():
            return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason=f"generated target is missing: {rel_path}")
        if entry.get("hand_editable") is not False:
            return _warning(
                rule,
                checked_paths,
                "generated_entries_mark_non_hand_editable_and_sources",
                reason=f"hand_editable must be false for {entry.get('id')}",
                expected={"hand_editable": False, "generated_from_prefix": "assets/"},
                observed={"entry_id": entry.get("id"), "hand_editable": entry.get("hand_editable")},
            )
        sources = entry.get("generated_from")
        if not isinstance(sources, list) or not sources:
            return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason=f"generated_from is missing for {entry.get('id')}")
        for source in sources:
            if not str(source).startswith("assets/"):
                return _warning(
                    rule,
                    checked_paths,
                    "generated_entries_mark_non_hand_editable_and_sources",
                    reason=f"generated_from must point to assets/* for {entry.get('id')}",
                    expected={"hand_editable": False, "generated_from_prefix": "assets/"},
                    observed={"entry_id": entry.get("id"), "generated_from": sources},
                )
            if not (repo_root / source).is_file():
                return _warning(rule, checked_paths, "generated_entries_mark_non_hand_editable_and_sources", reason=f"generated source is missing: {source}")

    return _ok(rule, checked_paths)


def codemaker_manifest_includes_required_paths(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    contract = find_codemaker_bundle_contract(context.data, "codemaker_non_scene_bundle")
    if contract is None:
        return _warning(
            rule,
            checked_paths,
            "codemaker_manifest_includes_required_paths",
            reason="facts.codemaker_bundle_contracts.codemaker_non_scene_bundle is missing",
        )

    manifest_rel = contract.get("manifest_path")
    if not isinstance(manifest_rel, str) or not manifest_rel:
        return _warning(
            rule,
            checked_paths,
            "codemaker_manifest_includes_required_paths",
            reason="manifest_path is missing from codemaker bundle contract",
        )
    manifest_path = repo_root / manifest_rel
    if not manifest_path.is_file():
        return _warning(
            rule,
            checked_paths,
            "codemaker_manifest_includes_required_paths",
            reason=f"manifest file is missing: {manifest_rel}",
        )

    required_paths = contract.get("required_paths", [])
    if not isinstance(required_paths, list) or not required_paths:
        return _warning(
            rule,
            checked_paths,
            "codemaker_manifest_includes_required_paths",
            reason="required_paths is empty in codemaker bundle contract",
        )
    for rel_path in required_paths:
        if not (repo_root / rel_path).is_file():
            return _warning(
                rule,
                checked_paths,
                "codemaker_manifest_includes_required_paths",
                reason=f"required bundle path is missing on disk: {rel_path}",
            )

    entries = set(_manifest_entries(manifest_path))
    missing_paths = [path for path in required_paths if path not in entries]
    if missing_paths:
        return _warning(
            rule,
            checked_paths,
            "codemaker_manifest_includes_required_paths",
            reason="required non-scene bundle paths are missing from manifest",
            expected={"required_paths": required_paths},
            observed={"missing_paths": missing_paths},
        )
    return _ok(rule, checked_paths)


def _command_script_paths(command: str) -> list[str]:
    tokens = shlex.split(command)
    if "-c" in tokens:
        return []
    return [token for token in tokens if token.endswith(".py")]


def compare_runbook_commands_and_artifact_defs(context: CheckContext, rule: dict[str, Any]) -> CheckOutcome:
    checked_paths = _scope_paths(rule)
    repo_root = context.repo_root
    artifact_paths = {item["path"] for item in distribution_artifact_nodes(context.data)}
    runbooks = context.data["facts"].get("runbooks", [])

    for rel_path in checked_paths:
        if not (repo_root / rel_path).exists():
            return _warning(rule, checked_paths, "compare_runbook_commands_and_artifact_defs", reason=f"missing scoped path: {rel_path}")

    for runbook in runbooks:
        for step in runbook.get("steps", []):
            command = step.get("command", "")
            for script_path in _command_script_paths(command):
                if not (repo_root / script_path).exists():
                    return _warning(rule, checked_paths, "compare_runbook_commands_and_artifact_defs", reason=f"runbook command references missing script: {script_path}")
            for output_path in step.get("outputs", []):
                if output_path not in artifact_paths:
                    return _warning(
                        rule,
                        checked_paths,
                        "compare_runbook_commands_and_artifact_defs",
                        reason=f"runbook output not declared as distribution artifact: {output_path}",
                        expected={"artifact_paths": sorted(artifact_paths)},
                        observed={"missing_output": output_path},
                    )
                if not (repo_root / output_path).exists():
                    return _warning(rule, checked_paths, "compare_runbook_commands_and_artifact_defs", reason=f"distribution artifact path is missing: {output_path}")

    return _ok(rule, checked_paths)


CHECK_REGISTRY = {
    "wrapper_chain_present": wrapper_chain_present,
    "distribution_paths_marked_non_source": distribution_paths_marked_non_source,
    "generated_entries_mark_non_hand_editable_and_sources": generated_entries_mark_non_hand_editable_and_sources,
    "scene_static_boundary_checks": scene_static_boundary_checks,
    "codemaker_manifest_includes_required_paths": codemaker_manifest_includes_required_paths,
    "shared_directory_role_checks": shared_directory_role_checks,
    "compare_runbook_commands_and_artifact_defs": compare_runbook_commands_and_artifact_defs,
}


def run_deterministic_rule(context: CheckContext, rule: dict[str, Any]) -> dict[str, Any]:
    checks = list(rule.get("evidence", {}).get("checks", []))
    if not checks:
        raise KeyError(f"rule {rule.get('id')} has no evidence.checks")
    outcome = _ok(rule, _scope_paths(rule))
    for check_name in checks:
        fn = CHECK_REGISTRY.get(check_name)
        if fn is None:
            raise KeyError(f"no check function registered for {check_name}")
        outcome = fn(context, rule)
        if outcome.status != "ok":
            break
    return result_record(rule, outcome)


def result_record(rule: dict[str, Any], outcome: CheckOutcome) -> dict[str, Any]:
    return {
        "rule_id": rule["id"],
        "status": outcome.status,
        "severity": rule.get("severity"),
        "mode": rule["enforcement"]["mode"],
        "coverage": dict(rule.get("coverage", {})),
        "checked_paths": outcome.checked_paths,
        "failed_checks": outcome.failed_checks,
        "message": outcome.message,
        "suggested_actions": outcome.suggested_actions,
        "reason": outcome.reason,
        "expected": outcome.expected,
        "observed": outcome.observed,
        "rule_source": str(rule.get("__rules_path", "")),
    }


def build_coverage_review(results: list[dict[str, Any]]) -> dict[str, Any]:
    mode_counts = {
        "deterministic": 0,
        "llm_assisted": 0,
        "manual": 0,
    }
    deterministic_candidate_rule_ids: list[str] = []
    next_checker_units: list[dict[str, str]] = []
    repair_candidate_rule_ids: list[str] = []
    repair_implemented_rule_ids: list[str] = []
    keep_non_deterministic_rule_ids: list[str] = []

    # ここは検査結果の要約ではなく、「この rule 群を今後どこまで自動化できるか」の
    # 棚卸しを返すメタレポート。
    for item in results:
        mode = item["mode"]
        if mode in mode_counts:
            mode_counts[mode] += 1
        coverage = item.get("coverage", {})
        deterministic_review = coverage.get("deterministic_review")
        if deterministic_review == "candidate":
            deterministic_candidate_rule_ids.append(item["rule_id"])
            next_checker_unit = coverage.get("next_checker_unit")
            if next_checker_unit:
                next_checker_units.append(
                    {
                        "rule_id": item["rule_id"],
                        "unit": next_checker_unit,
                    }
                )
        elif deterministic_review in {"keep_llm_assisted", "keep_manual"}:
            keep_non_deterministic_rule_ids.append(item["rule_id"])

        autofix_key = _coverage_autofix_key(coverage)
        repair_autofix = coverage.get(autofix_key) if autofix_key is not None else None
        if repair_autofix == "candidate":
            repair_candidate_rule_ids.append(item["rule_id"])
        elif repair_autofix == "implemented":
            repair_implemented_rule_ids.append(item["rule_id"])

    return {
        "mode_counts": mode_counts,
        "deterministic_candidate_rule_ids": deterministic_candidate_rule_ids,
        "next_checker_units": next_checker_units,
        "repair_candidate_rule_ids": repair_candidate_rule_ids,
        "repair_implemented_rule_ids": repair_implemented_rule_ids,
        "keep_non_deterministic_rule_ids": keep_non_deterministic_rule_ids,
    }


def build_output(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "total_rules": len(results),
        "executed_rules": sum(1 for item in results if item["status"] in {"ok", "warning"}),
        "warning_rules": sum(1 for item in results if item["status"] == "warning"),
        "skipped_rules": sum(1 for item in results if item["status"] == "skipped"),
        "error_rules": sum(1 for item in results if item["status"] == "error"),
    }
    return {
        "run_ok": summary["error_rules"] == 0,
        "has_warnings": summary["warning_rules"] > 0,
        "summary": summary,
        "coverage_review": build_coverage_review(results),
        "results": results,
    }


def run_checker(
    repo_root: Path,
    rules_path: Path,
    *,
    rule_ids: set[str] | None = None,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    rules_path = rules_path.resolve()
    data = load_rules(rules_path)
    context = CheckContext(repo_root=repo_root, rules_path=rules_path, data=data)
    results: list[dict[str, Any]] = []
    for rule in data["validation_rules"]:
        rule["__rules_path"] = str(rules_path)
        if rule_ids is not None and rule["id"] not in rule_ids:
            continue
        mode = rule["enforcement"]["mode"]
        # 非 deterministic rule も結果から消さず、skipped として残す。
        # これで coverage_review 側が「まだ人手/LLM に寄っている rule」を集計できる。
        if mode != "deterministic":
            results.append(result_record(rule, _skipped(rule)))
            continue
        results.append(run_deterministic_rule(context, rule))
    return build_output(results)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT, help="repository root to inspect")
    parser.add_argument(
        "--rules-path",
        type=Path,
        default=ROOT / "docs" / "architecture_rules.yml",
        help="path to architecture rules YAML",
    )
    parser.add_argument("--rule-id", action="append", default=[], help="run only the specified rule id (repeatable)")
    parser.add_argument("--fail-on-warning", action="store_true", help="return exit 1 when warnings remain")
    args = parser.parse_args(argv)
    try:
        result = run_checker(
            args.repo_root,
            args.rules_path,
            rule_ids=set(args.rule_id) if args.rule_id else None,
        )
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.fail_on_warning and result["has_warnings"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
