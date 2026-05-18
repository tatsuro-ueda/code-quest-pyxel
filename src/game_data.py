"""Game data module.

このファイルに含まれる関数・クラス：

- load_yaml: 任意の YAML ファイルを読み込んで Python データに変換する関数
- glitch_lord_phase: ボス HP 比からフェーズ名（phase1/2/3）を返す関数
- load_enemies: テスト向け互換 API として敵データ一覧を返す関数
- load_items: テスト向け互換 API としてアイテム一覧を返す関数
- load_weapons: テスト向け互換 API として武器一覧を返す関数
- load_armors: テスト向け互換 API として防具一覧を返す関数
- load_spells: テスト向け互換 API として呪文一覧を返す関数
- load_shops: テスト向け互換 API としてショップ設定全体を返す関数
- load_dialogue: 指定言語の会話データを返す関数
- _is_event_only_enemy: zone 一覧から除外するイベント敵かを返す述語関数
- _build_zone_enemies: zone -> list[enemy] にグルーピングする private 関数
- _resolve_glitch_lord_phase: ボス HP 比からフェーズ名を解決する private 関数
- _resolve_dialogue_by_language: 言語コードから会話辞書を解決する private 関数
- _read_yaml_lazy: PyYAML を遅延 import して YAML を読み込む private 関数

Problems:
    - Pyodide 実行環境には PyYAML が無いので、runtime 側で YAML を読むと
      動かない。一方 build 時 (tools/gen_data) では YAML を読みたい。
    - 派生データ (ZONE_ENEMIES / GLITCH_LORD_DATA など) を build せずに
      個別 import すると、ボス・イベント敵フラグの判定が複数箇所に散る。
    - 会話データを言語ごとに別 module から import すると、呼び出し側に
      "ja/en どちらを使うか" の分岐が漏れ出てしまう。

Solutions:
    - 純粋 Python データ (src/generated/*.py) を一括 import し、本 module で
      派生データ (ZONE_ENEMIES など) を構築する。YAML 読みは load_yaml に
      閉じ込めて遅延 import にし、runtime からは呼ばれない設計にする。
    - 公開ローダ (load_enemies / load_items / ...) はテスト互換のみを担い、
      runtime からは module-level 定数 (ENEMIES / ITEMS / ...) を直接参照する。
    - 言語フォールバックは load_dialogue("ja"|"en") に集約し、未知言語は
      ValueError で早期に弾く。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from src.generated.armors import ARMORS
from src.generated.dialogue import DIALOGUE_EN, DIALOGUE_JA
from src.generated.enemies import ENEMIES
from src.generated.items import ITEMS
from src.generated.shops import SHOPS
from src.generated.spells import SPELLS
from src.generated.weapons import WEAPONS

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"


# === Public API ===


def load_yaml(path: str | Path) -> Any:
    """Load any YAML file under the project.

    Args:
        path: 読みたい YAML ファイルへのパス。
    Returns:
        yaml.safe_load の結果（dict / list / str など）。
    Policy:
        - `yaml` (PyYAML) の遅延 import と読込は _read_yaml_lazy に委譲する。
          Pyodide 実行環境には PyYAML が入っていないが、runtime は
          src/generated/*.py（YAML から事前生成済みの純粋 Python データ）を
          読むだけなので、本関数は build 時の tools/gen_data 側からしか
          呼ばれない。
    """
    return _read_yaml_lazy(path)


def glitch_lord_phase(hp_ratio: float) -> str:
    """ボスHP比からフェーズ名（phase1/2/3）を返す（JS版 getBossPhases 相当）。

    Args:
        hp_ratio: ボス HP の現在比率 (0.0 - 1.0)。
    Returns:
        "phase1" / "phase2" / "phase3" のいずれか。
    Policy:
        - HP 閾値の判定はすべて _resolve_glitch_lord_phase に委譲し、
          本体は private 委譲 + return のステップ列に揃える。
    """
    return _resolve_glitch_lord_phase(hp_ratio)


def load_enemies() -> list[dict[str, Any]]:
    """テスト向け互換API：敵データ一覧を返す。

    Returns:
        生成済みの敵データ一覧 (ENEMIES)。
    Policy:
        - module-level 定数 ENEMIES への薄い委譲のみ。
    """
    return ENEMIES


def load_items() -> list[dict[str, Any]]:
    """テスト向け互換API：アイテム一覧を返す。

    Returns:
        生成済みのアイテム一覧 (ITEMS)。
    Policy:
        - module-level 定数 ITEMS への薄い委譲のみ。
    """
    return ITEMS


def load_weapons() -> list[dict[str, Any]]:
    """テスト向け互換API：武器一覧を返す。

    Returns:
        生成済みの武器一覧 (WEAPONS)。
    Policy:
        - module-level 定数 WEAPONS への薄い委譲のみ。
    """
    return WEAPONS


def load_armors() -> list[dict[str, Any]]:
    """テスト向け互換API：防具一覧を返す。

    Returns:
        生成済みの防具一覧 (ARMORS)。
    Policy:
        - module-level 定数 ARMORS への薄い委譲のみ。
    """
    return ARMORS


def load_spells() -> list[dict[str, Any]]:
    """テスト向け互換API：呪文一覧を返す。

    Returns:
        生成済みの呪文一覧 (SPELLS)。
    Policy:
        - module-level 定数 SPELLS への薄い委譲のみ。
    """
    return SPELLS


def load_shops() -> dict[str, Any]:
    """テスト向け互換API：ショップ設定全体を返す。

    Returns:
        生成済みのショップ設定 (SHOPS)。
    Policy:
        - module-level 定数 SHOPS への薄い委譲のみ。
    """
    return SHOPS


def load_dialogue(language: str) -> dict[str, Any]:
    """指定言語（ja/en）の会話データを返す。未知の言語は ValueError。

    Args:
        language: "ja" または "en"。
    Returns:
        指定言語の会話データ辞書 (DIALOGUE_JA / DIALOGUE_EN)。
    Raises:
        ValueError: language が "ja" / "en" 以外のとき。
    Policy:
        - 言語選択の分岐はすべて _resolve_dialogue_by_language に委譲し、
          本体は private 委譲 + return のステップ列に揃える。
    """
    return _resolve_dialogue_by_language(language)


# === Internal helpers (private) ===


def _is_event_only_enemy(enemy: dict[str, Any]) -> bool:
    """zone 一覧から除外したいイベント敵・ボス類かを判定する。

    Args:
        enemy: 敵データ 1 件分の辞書。
    Returns:
        bool: is_glitch_lord / is_professor / post_clear_only /
              is_noise_guardian のどれかが真なら True。
    Policy:
        - ZONE_ENEMIES に含めない敵のフラグ判定を 1 箇所に集約する。
    """
    if enemy.get("is_glitch_lord"):
        return True
    if enemy.get("is_professor"):
        return True
    if enemy.get("post_clear_only"):
        return True
    return bool(enemy.get("is_noise_guardian"))


def _build_zone_enemies(
    enemies: list[dict[str, Any]],
) -> dict[int, list]:
    """zone -> list[enemy] にグルーピング。イベント敵やボス等は除外。

    Args:
        enemies: 敵データ一覧。
    Returns:
        dict[int, list]: zone 番号 -> その zone の敵リスト。
    Policy:
        - イベント敵判定は _is_event_only_enemy 述語に切り出し、
          ここでは zone でグルーピングする責務だけを残す。
    """
    by_zone: dict[int, list] = {}
    for e in enemies:
        if _is_event_only_enemy(e):
            continue
        by_zone.setdefault(e["zone"], []).append(e)
    return by_zone


def _resolve_glitch_lord_phase(hp_ratio: float) -> str:
    """ボス HP 比からフェーズ名を解決する。

    Args:
        hp_ratio: ボス HP の現在比率 (0.0 - 1.0)。
    Returns:
        "phase1" / "phase2" / "phase3" のいずれか。
    Policy:
        - 閾値 0.6 / 0.3 で 3 段階に区切る。glitch_lord_phase を
          述語呼び出し + 委譲 + return のステップ列に保つための分離。
    """
    if hp_ratio > 0.6:
        return "phase1"
    if hp_ratio > 0.3:
        return "phase2"
    return "phase3"


def _resolve_dialogue_by_language(language: str) -> dict[str, Any]:
    """言語コードから会話データ辞書を解決する。

    Args:
        language: "ja" または "en"。
    Returns:
        DIALOGUE_JA / DIALOGUE_EN のいずれか。
    Raises:
        ValueError: 未知の言語コードのとき。
    Policy:
        - load_dialogue を private 委譲 + return のステップ列に保つため、
          言語分岐を本ヘルパーに閉じ込める。
    """
    if language == "ja":
        return DIALOGUE_JA
    if language == "en":
        return DIALOGUE_EN
    raise ValueError(f"unknown dialogue language: {language}")


def _read_yaml_lazy(path: str | Path) -> Any:
    """PyYAML を遅延 import して YAML を読み込む。

    Args:
        path: 読みたい YAML ファイルへのパス。
    Returns:
        yaml.safe_load の結果（dict / list / str など）。
    Policy:
        - import 文を本ヘルパーに閉じ込めて load_yaml を private 委譲 +
          return のステップ列に保つ。
    """
    import yaml
    text = Path(path).read_text(encoding="utf-8")
    return yaml.safe_load(text)


# --- derived module-level data (private helper 定義後に評価する) ---

ZONE_ENEMIES = _build_zone_enemies(ENEMIES)
GLITCH_LORD_DATA = next(e for e in ENEMIES if e.get("is_glitch_lord"))
PROFESSOR_DATA = next(e for e in ENEMIES if e.get("is_professor"))
GLITCH_CLONE_DATA = next(e for e in ENEMIES if e.get("post_clear_only"))
NOISE_GUARDIAN_DATA = next(e for e in ENEMIES if e.get("is_noise_guardian"))

SPELL_BY_NAME = {s["name"]: s for s in SPELLS}

INN_PRICES = SHOPS["inn_prices"]
SHOP_LIST = SHOPS["shops"]


GLITCH_LORD_PHASE_MESSAGES = {
    "phase2": "ボスの様子が変わった！",
    "phase3": "ボスは最後の力を振り絞っている！",
}
