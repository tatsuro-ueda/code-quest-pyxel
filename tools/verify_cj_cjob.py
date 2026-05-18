"""タスクノートと customer-journeys.md / customer-jobs.md の整合を検証する CLI。

このファイルに含まれる関数・クラス：

- Markdown のコードブロック / インラインコードを除去する純粋関数
- steering/*.md から CJ ID 出現集合を抽出する純粋関数
- customer-journeys.md から見出し ID 集合を抽出する純粋関数
- customer-journeys.md の各 CJ セクションから「該当カテゴリ」表記を抽出する純粋関数
- customer-jobs.md にカテゴリトークンが存在するかを判定する純粋関数
- run_verify_cj_cjob: 引数解析・走査・exit code 制御をまとめる CLI 入口

Problems:
    - タスクノートに書いた CJ ID が customer-journeys.md から消えても気付けず、
      参照リンクが silent に切れる。
    - 各 CJ の「該当カテゴリ」が customer-jobs.md から外れても CR / レビュー
      段階まで顕在化しない。
    - Gherkin 例文や正規表現片に偽 CJ ID（CJ999 や `rg "CJ4[0-2]"` 等）が
      含まれ、素朴な grep だと false positive で検証が崩れる。

Solutions:
    - コードブロック / インラインコードを事前剥離した上で CJ ID 集合を抽出する。
    - run_verify_cj_cjob を「引数解析 → 入力検査 → C1/C2 評価 → exit code 算出」
      のステップ列に揃え、各ステップを private helper に閉じ込める。
    - make verify からは exit code 1/2 で機械的に失敗を伝える契約を維持する。
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


CJ_ID_RE = re.compile(r"\bCJ\d+\b")
CJ_HEADING_RE = re.compile(r"^### (CJ\d+):", re.MULTILINE)
CATEGORY_LINE_RE = re.compile(r"該当カテゴリ：(.+?)→", re.DOTALL)
# 全角丸数字 ① 〜 ⑳（必要なら ⑩+ も拾えるよう範囲拡張）
CIRCLED_DIGIT_RE = re.compile(r"[①-⑳]")


# === Public API ===


def strip_code_blocks(text: str) -> str:
    """Markdown のコードブロックとインラインコードを除去する。

    Args:
        text: 加工前の Markdown 本文。

    Returns:
        str: ``` フェンスと ` インラインコードを除いた本文。

    Policy:
        - Gherkin 例文や正規表現片からの false positive を避けるため、
          コードブロック / インラインコードを段階的に剥離する。
    """
    return _strip_inline_code(_strip_fenced_blocks(text))


def collect_cj_ids_from_notes(steering_dir: Path) -> dict[str, set[Path]]:
    """steering/*.md から CJ ID を抽出し、CJ ID -> ファイル集合 を返す。

    Args:
        steering_dir: タスクノートのルート（steering/）。

    Returns:
        dict[str, set[Path]]: CJ ID をキーに、出現したファイル集合を値に持つ辞書。

    Policy:
        - Gherkin 例文の false positive を避けるため、strip_code_blocks で
          コードブロック内の CJ ID を除外してから収集する。
    """
    return _collect_cj_ids_from_notes(steering_dir)


def collect_cj_headings(journey_md: Path) -> set[str]:
    """customer-journeys.md の見出し集合 (### CJxx:) を返す。

    Args:
        journey_md: customer-journeys.md のパス。

    Returns:
        set[str]: 見出しから抽出した CJ ID 集合。

    Policy:
        - 見出し正規表現 (CJ_HEADING_RE) のマッチ結果をそのまま集合化する。
    """
    text = journey_md.read_text(encoding="utf-8")
    return set(CJ_HEADING_RE.findall(text))


def collect_cj_categories(journey_md: Path) -> dict[str, list[str]]:
    """customer-journeys.md から CJ ID -> カテゴリトークン列を抽出する。

    Args:
        journey_md: customer-journeys.md のパス。

    Returns:
        dict[str, list[str]]: CJ ID をキーに、カテゴリトークン（丸数字含む文字列）
        のリストを値に持つ辞書。

    Policy:
        - 各 ### CJxx: セクションごとに「該当カテゴリ：…→」行を走査し、
          丸数字始まりトークンを集約する。
    """
    text = journey_md.read_text(encoding="utf-8")
    return _collect_cj_categories_from_text(text)


def has_category_in_jobs(category_token: str, jobs_text: str) -> bool:
    """カテゴリトークンが customer-jobs.md 内に登場するかを判定する。

    Args:
        category_token: 丸数字始まりのカテゴリトークン。
        jobs_text: customer-jobs.md 全文。

    Returns:
        bool: 丸数字が jobs_text 内に存在すれば True。

    Policy:
        - 丸数字部分だけを抽出してマッチングする（後続のカテゴリ名は
          揺れる可能性があるため）。
    """
    return _is_circled_digit_in_jobs(category_token, jobs_text)


# 後方互換: 旧名 category_exists_in_jobs を残しておく（外部から呼ばれた場合の安全網）。
def category_exists_in_jobs(  # noqa: CR100
    category_token: str, jobs_text: str,
) -> bool:
    """has_category_in_jobs の旧名エイリアス。

    Args:
        category_token: 丸数字始まりのカテゴリトークン。
        jobs_text: customer-jobs.md 全文。

    Returns:
        bool: has_category_in_jobs の戻り値そのまま。

    Policy:
        - 旧 API 名を温存し、新しい述語名 has_category_in_jobs に委譲する。
    """
    return has_category_in_jobs(category_token, jobs_text)


def run_verify_cj_cjob(argv: list[str] | None = None) -> int:
    """CLI 入口: 引数解析と全件走査と exit code 制御をまとめる。

    Args:
        argv: コマンドライン引数（None なら sys.argv[1:] 相当）。

    Returns:
        int: 0=OK / 1=整合違反あり / 2=入力ファイル不在。

    Policy:
        - 「引数解析 → 入力検査 → C1 評価 → C2 評価 → exit code 算出」の
          ステップ列に揃え、本体は委譲のみで構成する。
    """
    args = _parse_verify_args(argv)
    return _run_verify_with_args(args)


# 後方互換: 旧 main エントリ名を残しておく（外部スクリプト保険）。
def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """run_verify_cj_cjob の旧名エイリアス。

    Args:
        argv: コマンドライン引数。

    Returns:
        int: run_verify_cj_cjob と同じ exit code。

    Policy:
        - 既存の `python tools/verify_cj_cjob.py` 起動と同じ振る舞いを保つ。
    """
    return run_verify_cj_cjob(argv)


# === Internal helpers (private) ===


def _is_circled_digit_in_jobs(category_token: str, jobs_text: str) -> bool:
    """カテゴリトークン先頭の丸数字が jobs_text 内に存在するかを判定する。

    Args:
        category_token: 丸数字始まりのカテゴリトークン。
        jobs_text: customer-jobs.md 全文。

    Returns:
        bool: 丸数字を抽出でき、かつ jobs_text に含まれていれば True。

    Policy:
        - 丸数字が抽出できない時点で False を返し、判定責務を 1 箇所に集約する。
    """
    match = CIRCLED_DIGIT_RE.search(category_token)
    if match is None:
        return False
    return match.group(0) in jobs_text


def _run_verify_with_args(args: argparse.Namespace) -> int:
    """検査本体: 入力検査 → C1 評価 → C2 評価 → exit code を算出する。

    Args:
        args: _parse_verify_args の戻り値。

    Returns:
        int: 0=OK / 1=整合違反あり / 2=入力ファイル不在。

    Policy:
        - 入力不備があれば 2 を返し、揃っていれば C1 / C2 違反件数を合算して
          exit code に変換する。
    """
    input_error = _validate_inputs(args)
    if input_error is not None:
        return input_error
    fail = _count_link_violations(args) + _count_category_violations(args)
    return _exit_code_for_fail_count(fail)


def _strip_fenced_blocks(text: str) -> str:
    """``` フェンスのコードブロックを除去する。

    Args:
        text: 加工前の Markdown 本文。

    Returns:
        str: ``` で挟まれた区間を空文字に置換した本文。

    Policy:
        - 非貪欲マッチで複数フェンスを順次除去する。
    """
    return re.sub(r"```[\s\S]*?```", "", text)


def _strip_inline_code(text: str) -> str:
    """` で囲まれたインラインコードを除去する。

    Args:
        text: フェンス除去済みの Markdown 本文。

    Returns:
        str: ` 〜 ` 区間を空文字に置換した本文。

    Policy:
        - 改行を跨ぐパターンは対象外とし、行内のインライン記法のみを剥がす。
    """
    return re.sub(r"`[^`\n]+`", "", text)


def _collect_cj_ids_from_notes(steering_dir: Path) -> dict[str, set[Path]]:
    """steering 配下の .md を走査して CJ ID -> ファイル集合 を組み立てる。

    Args:
        steering_dir: steering/ ディレクトリ。

    Returns:
        dict[str, set[Path]]: CJ ID をキーに、出現ファイル集合を値に持つ辞書。

    Policy:
        - strip_code_blocks で偽 CJ ID を除いてから集合化する。
    """
    out: dict[str, set[Path]] = {}
    for md_path in sorted(steering_dir.rglob("*.md")):
        text = md_path.read_text(encoding="utf-8", errors="replace")
        text_no_code = strip_code_blocks(text)
        for cj_id in set(CJ_ID_RE.findall(text_no_code)):
            out.setdefault(cj_id, set()).add(md_path)
    return out


def _collect_cj_categories_from_text(text: str) -> dict[str, list[str]]:
    """customer-journeys.md 全文から CJ ID -> カテゴリトークン列を組み立てる。

    Args:
        text: customer-journeys.md 全文。

    Returns:
        dict[str, list[str]]: CJ ID をキーに、カテゴリトークン列を値に持つ辞書。

    Policy:
        - ### で分割した各セクションの先頭 CJ ID を抽出し、
          「該当カテゴリ：…→」行から丸数字始まりトークンを収集する。
    """
    sections = re.split(r"^### ", text, flags=re.MULTILINE)
    out: dict[str, list[str]] = {}
    for section in sections:
        cj_match = re.match(r"(CJ\d+):", section)
        if cj_match is None:
            continue
        cats = _extract_category_tokens(section)
        if cats:
            out[cj_match.group(1)] = cats
    return out


def _extract_category_tokens(section: str) -> list[str]:
    """1 つの CJ セクションから「該当カテゴリ」トークン列を抽出する。

    Args:
        section: ### 区切りで分割した 1 セクション本文。

    Returns:
        list[str]: 丸数字始まりのカテゴリトークン列。

    Policy:
        - CATEGORY_LINE_RE で抽出した行から、[①-⑳][^,，、]+ 形式のトークン
          をすべて取り出して strip する。
    """
    cats: list[str] = []
    for catline in CATEGORY_LINE_RE.findall(section):
        for token in re.findall(r"[①-⑳][^,，、]+", catline):
            cats.append(token.strip())
    return cats


def _parse_verify_args(argv: list[str] | None) -> argparse.Namespace:
    """argparse を組み立てて Namespace を返す。

    Args:
        argv: コマンドライン引数（None なら sys.argv[1:] 相当）。

    Returns:
        argparse.Namespace: --steering / --journey / --jobs を持つ Namespace。

    Policy:
        - 既存 CLI 互換のため引数名と既定値はそのまま維持する。
    """
    description = (__doc__ or "").splitlines()[0]
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--steering", type=Path, default=Path("steering"),
        help="タスクノートのルート（デフォルト: steering）",
    )
    parser.add_argument(
        "--journey",
        type=Path,
        default=Path("docs/customer-journeys.md"),
    )
    parser.add_argument(
        "--jobs",
        type=Path,
        default=Path("docs/customer-jobs.md"),
    )
    return parser.parse_args(argv)


def _validate_inputs(args: argparse.Namespace) -> int | None:
    """入力ファイル群が揃っているかを検証し、エラーなら exit code を返す。

    Args:
        args: _parse_verify_args の戻り値。

    Returns:
        int | None: 全て揃っていれば None、欠けがあれば 2。

    Policy:
        - 3 種の入力（steering ディレクトリ / journey ファイル / jobs ファイル）
          を順に確認し、最初に見つけた欠落で 2 を返す。
    """
    if not args.steering.is_dir():
        print(
            f"steering directory not found: {args.steering}",
            file=sys.stderr,
        )
        return 2
    if not args.journey.is_file():
        print(
            f"customer-journeys.md not found: {args.journey}",
            file=sys.stderr,
        )
        return 2
    if not args.jobs.is_file():
        print(
            f"customer-jobs.md not found: {args.jobs}",
            file=sys.stderr,
        )
        return 2
    return None


def _count_link_violations(args: argparse.Namespace) -> int:
    """C1: タスクノート中の CJ ID が customer-journeys.md に存在するかを検証する。

    Args:
        args: _parse_verify_args の戻り値。

    Returns:
        int: 解決できなかった CJ ID の件数。

    Policy:
        - 違反があれば 1 件ずつ stderr に出し、ゼロ件なら OK 行を stdout に出す。
    """
    cj_in_notes = collect_cj_ids_from_notes(args.steering)
    headings = collect_cj_headings(args.journey)
    missing = sorted(set(cj_in_notes.keys()) - headings)
    if missing:
        _report_missing_cj_links(missing, cj_in_notes)
        return len(missing)
    print(
        f"CJ link OK: {len(cj_in_notes)} unique CJ IDs in steering/, "
        "all resolved",
        file=sys.stdout,
    )
    return 0


def _report_missing_cj_links(
    missing: list[str],
    cj_in_notes: dict[str, set[Path]],
) -> None:
    """C1 の不整合行を stderr に書き出す。

    Args:
        missing: customer-journeys.md に存在しなかった CJ ID 列。
        cj_in_notes: CJ ID -> 出現ファイル集合 の辞書。

    Policy:
        - 1 行 1 違反を保ち、参照元ファイル名を併記して原因を辿りやすくする。
    """
    for cj_id in missing:
        files = sorted(p.name for p in cj_in_notes[cj_id])
        print(
            f"CJ link broken: {cj_id} not found in customer-journeys.md "
            f"(referenced by: {', '.join(files)})",
            file=sys.stderr,
        )


def _count_category_violations(args: argparse.Namespace) -> int:
    """C2: 各 CJ の該当カテゴリが customer-jobs.md に存在するかを検証する。

    Args:
        args: _parse_verify_args の戻り値。

    Returns:
        int: customer-jobs.md に解決できなかったカテゴリトークン数。

    Policy:
        - 検証対象は customer-journeys.md にも存在する CJ ID のみ。
        - 違反があれば 1 件ずつ stderr に出し、ゼロ件なら OK 行を stdout に出す。
    """
    cj_in_notes = collect_cj_ids_from_notes(args.steering)
    headings = collect_cj_headings(args.journey)
    referenced_cjs = set(cj_in_notes.keys()) & headings
    cj_categories = collect_cj_categories(args.journey)
    jobs_text = args.jobs.read_text(encoding="utf-8")
    checked, fail = _evaluate_category_tokens(
        sorted(referenced_cjs), cj_categories, jobs_text,
    )
    if fail == 0:
        print(
            f"CJob category OK: {checked} category tokens checked",
            file=sys.stdout,
        )
    return fail


def _evaluate_category_tokens(
    cj_ids: list[str],
    cj_categories: dict[str, list[str]],
    jobs_text: str,
) -> tuple[int, int]:
    """カテゴリトークン群を走査して (検証件数, 違反件数) を返す。

    Args:
        cj_ids: 検証対象 CJ ID 列（ソート済み）。
        cj_categories: collect_cj_categories の戻り値。
        jobs_text: customer-jobs.md 全文。

    Returns:
        tuple[int, int]: (検証したトークン数, 解決できなかった件数)。

    Policy:
        - 違反トークンは 1 件 1 行で stderr に出力する。
    """
    checked = 0
    fail = 0
    for cj_id in cj_ids:
        for cat in cj_categories.get(cj_id, []):
            checked += 1
            if not has_category_in_jobs(cat, jobs_text):
                print(
                    f"CJob category broken: {cj_id} 該当カテゴリ "
                    f"{cat!r} not found in customer-jobs.md",
                    file=sys.stderr,
                )
                fail += 1
    return checked, fail


def _exit_code_for_fail_count(fail: int) -> int:
    """違反件数から CLI exit code を導く。

    Args:
        fail: C1 + C2 の違反件数合計。

    Returns:
        int: 0 件なら 0、1 件以上なら 1。

    Policy:
        - 失敗時は件数を stderr にサマリ出力してから 1 を返す。
    """
    if fail == 0:
        return 0
    print(f"FAIL: {fail} integrity issues", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(run_verify_cj_cjob())
