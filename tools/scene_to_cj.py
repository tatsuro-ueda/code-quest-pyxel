"""コード変更から関連 CJ / カスタマージョブカテゴリへの影響範囲を提示する CLI。

このファイルに含まれる関数・クラス：

- load_map: 対応表 JSON を読み込む純粋関数
- get_changed_files: git diff --name-only から変更ファイル一覧を取得するヘルパ
- extract_scenes_and_areas: 変更ファイル一覧から scene 名 / area 名を抽出する純粋関数
- collect_cj_categories: customer-journeys.md から CJ ID → カテゴリを引く純粋関数
- verify_map_against_journey: 対応表中の CJ ID が customer-journeys.md に実在することを検証
- print_for_keys: scene / area キー群に対応する CJ + カテゴリを stdout に出す
- run_main: --list / --since の 2 モードを切り替える CLI entry
- main: 互換のため残す run_main の薄いエイリアス

Problems:
    - コード変更が、どの CJ / カスタマージョブカテゴリに影響しているのか
      対応表越しに目視で追わないと分からない。
    - 対応表中の CJ ID が customer-journeys.md から消えていても気付けない。

Solutions:
    - tools/scene_to_cj.json と docs/customer-journeys.md を読み合わせ、
      `--list` で全 scene / area を、`--since` で git diff 由来の変更を提示する。
    - `--verify-only` で対応表中の CJ ID が customer-journeys.md に実在するかだけ
      検証する Make ターゲットを用意し、CI / 手動 verify から呼び出せるようにする。
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


CJ_HEADING_RE = re.compile(r"^### (CJ\d+):", re.MULTILINE)
CATEGORY_LINE_RE = re.compile(r"該当カテゴリ：(.+?)→", re.DOTALL)


# === Public API ===


def load_map(path: Path) -> dict:
    """対応表 JSON を読んで dict として返す。

    Args:
        path: 対応表 JSON のパス。

    Returns:
        scenes / areas キーを含む対応表 dict。

    Policy:
        - I/O だけを担当し、構造検証は呼び出し側に委ねる。
    """
    return json.loads(path.read_text(encoding="utf-8"))


def get_changed_files(since: str) -> list[str]:
    """`git diff --name-only <since> HEAD` の結果を返す。

    Args:
        since: 比較基点となる commit-ish（例: HEAD~1）。

    Returns:
        変更ファイル名のリスト。git が非ゼロ終了した場合は空リスト。

    Policy:
        - subprocess 呼び出しと結果整形を private helper に閉じ込め、
          本体は委譲と return のみで構成する。
    """
    return _collect_changed_files(since)


def extract_scenes_and_areas(files: list[str],
                             scene_keys: list[str],
                             area_keys: list[str]) -> tuple[set[str],
                                                            set[str]]:
    """変更ファイルから scene 名と area 名を抽出する。

    Args:
        files: 変更ファイルのパス文字列リスト。
        scene_keys: 対応表に登録されている scene 名のリスト。
        area_keys: 対応表に登録されている area 名のリスト。

    Returns:
        (検出された scene 名集合, 検出された area 名集合)。

    Policy:
        - 走査本体は private helper に委譲し、ステップ列を保つ。
    """
    return _extract_scene_area_sets(files, scene_keys, area_keys)


def collect_cj_categories(journey_md: Path) -> dict[str, list[str]]:
    """customer-journeys.md から CJ ID -> カテゴリトークンのリストを抽出する。

    Args:
        journey_md: customer-journeys.md のパス。

    Returns:
        CJ ID をキーに、カテゴリトークン（例: '①ふしぎ'）のリストを値とする dict。

    Policy:
        - section 分割と category 抽出は private helper に閉じ込める。
    """
    return _load_cj_category_map(journey_md)


def verify_map_against_journey(mapping: dict, journey_md: Path) -> list[str]:
    """対応表中の CJ ID が customer-journeys.md に実在するか検証し、欠損リストを返す。

    Args:
        mapping: 対応表 dict（scenes / areas キーを持つ）。
        journey_md: customer-journeys.md のパス。

    Returns:
        実在しなかった "group.key -> CJxxx" 形式の文字列リスト（無ければ空）。

    Policy:
        - 「### CJxxx:」見出しを真とし、対応表中の CJ ID をすべて照合する。
    """
    return _check_map_cj_refs(mapping, journey_md)


def print_for_keys(label: str, keys: set[str], mapping: dict, group: str,
                   cj_categories: dict[str, list[str]]) -> None:
    """label と key 群について、対応する CJ + カテゴリを stdout に出す。

    Args:
        label: セクション見出しのラベル。
        keys: 出力対象の scene / area キー集合。
        mapping: 対応表 dict。
        group: "scenes" または "areas"。
        cj_categories: CJ ID -> カテゴリトークンのリスト。

    Policy:
        - 空キー判定とヘッダ・本文出力を private helper に委譲する。
    """
    _print_section_if_any(label, keys, mapping, group, cj_categories)


def run_main(argv: list[str] | None = None) -> int:
    """CLI entry。--list / --since / --verify-only を切り替えて結果を出す。

    Args:
        argv: コマンドライン引数（None なら sys.argv を使う）。

    Returns:
        exit code（0=成功 / 1=欠損あり / 2=入力エラー or 引数なし）。

    Policy:
        - 引数解析と検証と各モード dispatch を private helper に委譲するステップ列。
    """
    return _execute_cli(argv)


def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """run_main の互換エイリアス（外部から `main` で呼ばれる経路を維持する）。

    Args:
        argv: コマンドライン引数（None なら sys.argv を使う）。

    Returns:
        exit code。run_main と同義。

    Policy:
        - 実体は run_main に委譲し、引数と戻り値の意味は同一。
    """
    return run_main(argv)


# === Internal helpers (private) ===


def _collect_changed_files(since: str) -> list[str]:
    """git diff の呼び出しと結果整形を担う private 本体。

    Args:
        since: 比較基点となる commit-ish。

    Returns:
        変更ファイル名のリスト。失敗時は空リスト。

    Policy:
        - returncode が 0 でないときは空リストにフォールバックする。
    """
    out = _run_git_diff(since)
    if out.returncode != 0:
        return []
    return _split_diff_lines(out.stdout)


def _run_git_diff(since: str) -> subprocess.CompletedProcess:
    """`git diff --name-only <since> HEAD` を起動して結果を返す。

    Args:
        since: 比較基点となる commit-ish。

    Returns:
        subprocess.CompletedProcess: capture_output=True / check=False で取得した結果。

    Policy:
        - check=False で例外を投げず、終了コードを呼び出し側に判定させる。
    """
    return subprocess.run(
        ["git", "diff", "--name-only", since, "HEAD"],
        capture_output=True, text=True, check=False,
    )


def _split_diff_lines(stdout: str) -> list[str]:
    """stdout を行ごとに分割し、空行を除いて返す。

    Args:
        stdout: git diff の標準出力文字列。

    Returns:
        空でない行のリスト。

    Policy:
        - splitlines + strip で空行を除外する。
    """
    return [line for line in stdout.splitlines() if line.strip()]


def _extract_scene_area_sets(
        files: list[str],
        scene_keys: list[str],
        area_keys: list[str]) -> tuple[set[str], set[str]]:
    """ファイル列を走査して scene 名集合と area 名集合を作る private 本体。

    Args:
        files: 変更ファイルのパス文字列リスト。
        scene_keys: 対応表に登録されている scene 名のリスト。
        area_keys: 対応表に登録されている area 名のリスト。

    Returns:
        (scene 名集合, area 名集合)。

    Policy:
        - 1 ファイル分の判定は _accumulate_scene_and_area に委ねる。
    """
    scenes: set[str] = set()
    areas: set[str] = set()
    for file_path in files:
        _accumulate_scene_and_area(file_path, scene_keys, area_keys,
                                   scenes, areas)
    return scenes, areas


def _accumulate_scene_and_area(file_path: str,
                               scene_keys: list[str],
                               area_keys: list[str],
                               scenes: set[str],
                               areas: set[str]) -> None:
    """1 ファイル分の scene / area を accumulator に加算する。

    Args:
        file_path: 変更ファイルのパス文字列。
        scene_keys: 対応表に登録されている scene 名のリスト。
        area_keys: 対応表に登録されている area 名のリスト。
        scenes: 検出済み scene 名集合（破壊的に更新）。
        areas: 検出済み area 名集合（破壊的に更新）。

    Policy:
        - src/scenes/<scene>/ なら scene として、src/<area>/ なら area として登録。
        - 対応表に無いキーは silently skip する。
    """
    parts = file_path.split("/")
    if _is_scene_path(parts, scene_keys):
        scenes.add(parts[2])
    if _is_area_path(parts, area_keys):
        areas.add(parts[1])


def _is_scene_path(parts: list[str], scene_keys: list[str]) -> bool:
    """parts が src/scenes/<known-scene>/ で始まるなら True。

    Args:
        parts: ファイルパスを '/' で split した断片リスト。
        scene_keys: 対応表に登録されている scene 名のリスト。

    Returns:
        scene として認識できるなら True、そうでなければ False。

    Policy:
        - 長さ 3 未満、または src/scenes/ で始まらない場合は False。
    """
    if len(parts) < 3:
        return False
    if not _is_src_scenes_prefix(parts):
        return False
    return parts[2] in scene_keys


def _is_src_scenes_prefix(parts: list[str]) -> bool:
    """parts[0:2] が ['src', 'scenes'] なら True。

    Args:
        parts: ファイルパスを '/' で split した断片リスト。

    Returns:
        src/scenes/ で始まるパスなら True。

    Policy:
        - 先頭 2 要素のみを比較する純粋判定。
    """
    return parts[0] == "src" and parts[1] == "scenes"


def _is_area_path(parts: list[str], area_keys: list[str]) -> bool:
    """parts が src/<known-area>/ で始まるなら True。

    Args:
        parts: ファイルパスを '/' で split した断片リスト。
        area_keys: 対応表に登録されている area 名のリスト。

    Returns:
        area として認識できるなら True、そうでなければ False。

    Policy:
        - 長さ 2 未満、または src/ で始まらない場合は False。
    """
    if len(parts) < 2:
        return False
    if parts[0] != "src":
        return False
    return parts[1] in area_keys


def _load_cj_category_map(journey_md: Path) -> dict[str, list[str]]:
    """journey_md を読み込んで CJ ID -> カテゴリトークンのリストを返す。

    Args:
        journey_md: customer-journeys.md のパス。

    Returns:
        CJ ID をキーにしたカテゴリトークンのリスト dict。

    Policy:
        - I/O と section 分割を済ませてから _build_cj_category_map に委譲する。
    """
    text = journey_md.read_text(encoding="utf-8")
    sections = re.split(r"^### ", text, flags=re.MULTILINE)
    return _build_cj_category_map(sections)


def _build_cj_category_map(sections: list[str]) -> dict[str, list[str]]:
    """### で split された各 section から CJ ID -> カテゴリトークンを抽出する。

    Args:
        sections: re.split で得た section 断片のリスト。

    Returns:
        CJ ID をキーにしたカテゴリトークンのリスト dict。

    Policy:
        - 「### CJxxx:」形式のヘッダだけを採用し、カテゴリ行が無い CJ は除外する。
    """
    out: dict[str, list[str]] = {}
    for sec in sections:
        match = re.match(r"(CJ\d+):", sec)
        if not match:
            continue
        cj_id = match.group(1)
        cats = _extract_category_tokens(sec)
        if cats:
            out[cj_id] = cats
    return out


def _extract_category_tokens(section: str) -> list[str]:
    """section から「該当カテゴリ：...→」行のカテゴリトークン列を取り出す。

    Args:
        section: 1 つの CJ section テキスト。

    Returns:
        カテゴリトークン（'①ふしぎ' など）のリスト。

    Policy:
        - 丸数字（①-⑳）で始まる単位をカテゴリトークンとして抽出する。
    """
    cats: list[str] = []
    for catline in CATEGORY_LINE_RE.findall(section):
        for token in re.findall(r"[①-⑳][^,，、]+", catline):
            cats.append(token.strip())
    return cats


def _check_map_cj_refs(mapping: dict, journey_md: Path) -> list[str]:
    """対応表中の CJ ID 参照が journey_md に実在するか確認し欠損を返す。

    Args:
        mapping: 対応表 dict。
        journey_md: customer-journeys.md のパス。

    Returns:
        欠損 "group.key -> CJxxx" 文字列のリスト。

    Policy:
        - 見出し集合の取得と欠損集計を順に行うステップ列。
    """
    headings = _load_cj_headings(journey_md)
    return _collect_missing_cj_refs(mapping, headings)


def _load_cj_headings(journey_md: Path) -> set[str]:
    """customer-journeys.md から「### CJxxx:」の CJ ID 集合を返す。

    Args:
        journey_md: customer-journeys.md のパス。

    Returns:
        ファイル内に存在する CJ ID の集合。

    Policy:
        - 正規表現マッチで集めるだけの純粋関数。
    """
    text = journey_md.read_text(encoding="utf-8")
    return set(CJ_HEADING_RE.findall(text))


def _collect_missing_cj_refs(mapping: dict, headings: set[str]) -> list[str]:
    """対応表中の CJ ID で headings に無いものを "group.key -> CJxxx" 形式で集める。

    Args:
        mapping: 対応表 dict。
        headings: customer-journeys.md に実在する CJ ID 集合。

    Returns:
        欠損 CJ 参照を表す文字列のリスト。

    Policy:
        - scenes / areas の 2 グループを走査する。
    """
    missing: list[str] = []
    for group_name in ("scenes", "areas"):
        for key, cjs in mapping.get(group_name, {}).items():
            for cj in cjs:
                if cj not in headings:
                    missing.append(f"{group_name}.{key} -> {cj}")
    return missing


def _print_section_if_any(label: str,
                          keys: set[str],
                          mapping: dict,
                          group: str,
                          cj_categories: dict[str, list[str]]) -> None:
    """キー集合が非空のときだけセクションヘッダと本文を出力する。

    Args:
        label: セクション見出しのラベル。
        keys: 出力対象キー集合。
        mapping: 対応表 dict。
        group: "scenes" または "areas"。
        cj_categories: CJ ID -> カテゴリトークンのリスト。

    Policy:
        - 空集合のときは何も出力しない。
    """
    if not keys:
        return
    _print_section_header(label)
    _print_key_lines(keys, mapping, group, cj_categories)


def _print_section_header(label: str) -> None:
    """`## <label>` を 1 行出す。

    Args:
        label: 表示するラベル文字列。

    Policy:
        - I/O のみを担当する単純関数。
    """
    print(f"## {label}")


def _print_key_lines(keys: set[str], mapping: dict, group: str,
                     cj_categories: dict[str, list[str]]) -> None:
    """key ごとの CJ 行とカテゴリ行を sorted 順で出力する。

    Args:
        keys: 出力対象キー集合。
        mapping: 対応表 dict。
        group: "scenes" または "areas"。
        cj_categories: CJ ID -> カテゴリトークンのリスト。

    Policy:
        - CJ が無いキーは "(no CJ mapped)" と表示し、カテゴリ無しは "(no categories)"。
    """
    for key in sorted(keys):
        cjs = mapping.get(group, {}).get(key, [])
        _print_one_key_line(key, cjs, cj_categories)


def _print_one_key_line(key: str, cjs: list[str],
                        cj_categories: dict[str, list[str]]) -> None:
    """1 キー分の見出し行と CJ ごとのカテゴリ行を出す。

    Args:
        key: scene / area キー文字列。
        cjs: 対応する CJ ID のリスト。
        cj_categories: CJ ID -> カテゴリトークンのリスト。

    Policy:
        - 空 CJ リストは "(no CJ mapped)" にフォールバックする。
    """
    cj_text = ", ".join(cjs) if cjs else "(no CJ mapped)"
    print(f"- {key} → {cj_text}")
    for cj in cjs:
        cats = cj_categories.get(cj, [])
        cats_str = ", ".join(cats) if cats else "(no categories)"
        print(f"    {cj}: {cats_str}")


def _execute_cli(argv: list[str] | None) -> int:
    """CLI 全体の本体（引数解析 → 検証 → モード dispatch）。

    Args:
        argv: コマンドライン引数（None なら sys.argv を使う）。

    Returns:
        exit code（run_main と同じ意味）。

    Policy:
        - 引数解析と各モード dispatch を private helper に委譲する。
    """
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    if not args.map.is_file():
        return _report_map_missing(args.map)
    mapping = load_map(args.map)
    missing = verify_map_against_journey(mapping, args.journey)
    _print_missing_refs(missing)
    return _dispatch_main_mode(args, parser, mapping, missing)


def _build_arg_parser() -> argparse.ArgumentParser:
    """argparse parser を組み立てて返す。

    Returns:
        構築済みの argparse parser。

    Policy:
        - 既存 CLI 互換のため引数名・default 値・help 文言を維持する。
    """
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--map",
        type=Path,
        default=Path("tools/scene_to_cj.json"),
        help="対応表 JSON")
    parser.add_argument(
        "--journey",
        type=Path,
        default=Path("docs/customer-journeys.md"))
    parser.add_argument("--list", action="store_true",
                        help="全 scene / area の対応表を一覧表示する")
    parser.add_argument(
        "--since", type=str, default=None,
        help="この commit-ish から HEAD までの差分から影響範囲を出す（例: HEAD~1）")
    parser.add_argument(
        "--verify-only", action="store_true",
        help="対応表の CJ ID が customer-journeys.md に実在するかだけ検証する")
    return parser


def _report_map_missing(map_path: Path) -> int:
    """対応表ファイルが無い旨を stderr に出し、exit code 2 を返す。

    Args:
        map_path: 見つからなかった対応表 JSON のパス。

    Returns:
        固定値 2（exit code）。

    Policy:
        - I/O のみを担当する。
    """
    print(f"map file not found: {map_path}", file=sys.stderr)
    return 2


def _print_missing_refs(missing: list[str]) -> None:
    """欠損 CJ ID リストを stderr に流す。

    Args:
        missing: "group.key -> CJxxx" 文字列のリスト。

    Policy:
        - リストが空なら何も出さない。
    """
    for ref in missing:
        print(f"map references missing CJ: {ref}", file=sys.stderr)


def _dispatch_main_mode(args: argparse.Namespace,
                        parser: argparse.ArgumentParser,
                        mapping: dict,
                        missing: list[str]) -> int:
    """--verify-only / --list / --since の各モードに分岐する。

    Args:
        args: argparse の解析結果。
        parser: usage 出力に使う argparse parser。
        mapping: 対応表 dict。
        missing: 欠損 CJ 参照のリスト。

    Returns:
        exit code（モードごとの規約に従う）。

    Policy:
        - verify-only は missing 有無を exit code に直結。
        - list / since はカテゴリを引いてから print 関数に委譲。
        - どのモードでもなければ help を出して exit code 2。
    """
    if args.verify_only:
        return _run_verify_only_mode(missing)
    cj_categories = collect_cj_categories(args.journey)
    if args.list:
        return _run_list_mode(mapping, cj_categories, missing)
    if args.since:
        return _run_since_mode(args.since, mapping, cj_categories, missing)
    parser.print_help(sys.stderr)
    return 2


def _run_verify_only_mode(missing: list[str]) -> int:
    """--verify-only モードの結果出力と exit code を決める。

    Args:
        missing: 欠損 CJ 参照のリスト。

    Returns:
        欠損があれば 1、無ければ 0。

    Policy:
        - missing 有無で exit code が決まる単純判定。
    """
    if missing:
        return 1
    print("scene_to_cj map OK", file=sys.stdout)
    return 0


def _run_list_mode(mapping: dict,
                   cj_categories: dict[str, list[str]],
                   missing: list[str]) -> int:
    """--list モードの本体（全 scene / area を出力）。

    Args:
        mapping: 対応表 dict。
        cj_categories: CJ ID -> カテゴリトークンのリスト。
        missing: 欠損 CJ 参照のリスト。

    Returns:
        missing があれば 1、無ければ 0。

    Policy:
        - scenes と areas を順に print_for_keys に渡すステップ列。
    """
    print_for_keys(
        "scenes",
        set(mapping.get("scenes", {}).keys()),
        mapping, "scenes", cj_categories)
    print_for_keys(
        "areas",
        set(mapping.get("areas", {}).keys()),
        mapping, "areas", cj_categories)
    return 1 if missing else 0


def _run_since_mode(since: str,
                    mapping: dict,
                    cj_categories: dict[str, list[str]],
                    missing: list[str]) -> int:
    """--since モードの本体（変更ファイルから影響 scene / area を出力）。

    Args:
        since: 比較基点となる commit-ish。
        mapping: 対応表 dict。
        cj_categories: CJ ID -> カテゴリトークンのリスト。
        missing: 欠損 CJ 参照のリスト。

    Returns:
        欠損があれば 1、無ければ 0。

    Policy:
        - git diff → 抽出 → 出力のステップ列。変更が無ければその旨だけ出す。
    """
    files = get_changed_files(since)
    scenes, areas = extract_scenes_and_areas(
        files,
        list(mapping.get("scenes", {}).keys()),
        list(mapping.get("areas", {}).keys()),
    )
    if _has_no_relevant_changes(scenes, areas):
        print(
            f"no relevant scene / area changes since {since}",
            file=sys.stdout)
        return 0
    print_for_keys(
        "changed scenes", scenes, mapping, "scenes", cj_categories)
    print_for_keys(
        "changed areas", areas, mapping, "areas", cj_categories)
    return 1 if missing else 0


def _has_no_relevant_changes(scenes: set[str], areas: set[str]) -> bool:
    """検出された scene 集合と area 集合がどちらも空なら True。

    Args:
        scenes: 検出された scene 名集合。
        areas: 検出された area 名集合。

    Returns:
        両方とも空なら True、いずれかに要素があれば False。

    Policy:
        - 「変更なし」判定を述語関数として切り出すための単純判定。
    """
    return not scenes and not areas


if __name__ == "__main__":
    raise SystemExit(run_main())
