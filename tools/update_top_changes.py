"""post-commit hook 本体: commit log を Claude Haiku で解釈し top_changes.json を更新する。

このファイルに含まれる関数・クラス：

- _git: subprocess で git コマンドを実行して標準出力を返す薄いラッパ
- _today_short: `5/6` 形式の短い日付文字列を返す
- _is_auto_amend: AUTO_MARKER の有無で再帰判定する純粋関数
- _build_prompt: Claude Haiku 用プロンプトを組み立てる純粋関数
- call_claude: Anthropic SDK 経由で 1 行翻訳 JSON を取得する I/O
- prepend_change: top_changes.json の changes 先頭に line を追加する I/O
- render_index: tools/render_top_changes.py を呼んで index.html を更新する
- amend_with_marker: 直前 commit に成果物を amend で取り込む
- run_update_top_changes: post-commit から呼ばれる CLI 入口

呼び出し元: .git/hooks/post-commit (tools/install_hooks.sh で配置)

Problems:
    - commit の主旨を「子どもに関係するか」で振り分け、子ども向け 1 行を
      top_changes.json に追記するルーチンを手作業でやると忘れる / 揺れる。
    - 自分が打った amend commit に hook が再度反応すると、無限再帰になる。
    - ANTHROPIC_API_KEY が無い／API 呼び出しが失敗するなど通常運用で起きる
      失敗で commit 自体を壊すと、開発体験が悪化する。

Solutions:
    - AUTO_MARKER をコミット本文末尾に残し、検出で即 return 0 して再帰を断つ。
    - 全ての fail パスで exit 0 を返し、commit は決して壊さない契約にする。
    - 主処理を「git 取得 → 再帰判定 → API key 検査 → prompt 構築 →
      Claude 呼出 → prepend → render → amend」のステップ列に揃え、
      各ステップは private helper / 既存 public 関数に閉じ込める。

挙動:
  1. 直前 commit の subject + body を取得
  2. AUTO_MARKER (`[top-changes auto]`) があれば即 exit 0（再帰防止）
  3. ANTHROPIC_API_KEY が無ければ stderr 警告のみで exit 0
  4. Claude Haiku に判定させる:
       - 関係なし → exit 0（top_changes.json は無変更）
       - 関係あり → 1 行翻訳を返す
  5. top_changes.json の changes 先頭に prepend（MAX_KEEP=20 で truncate）
  6. tools/render_top_changes.py を呼んで index.html を更新
  7. git commit --amend --no-edit で直前 commit に取り込む
       commit body 末尾に AUTO_MARKER を残して再帰を断つ
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOP_CHANGES_PATH = ROOT / "top_changes.json"
INDEX_HTML_PATH = ROOT / "index.html"
RENDER_SCRIPT = ROOT / "tools" / "render_top_changes.py"

AUTO_MARKER = "[top-changes auto]"
MAX_KEEP = 20
MODEL = "claude-haiku-4-5-20251001"


# === Public API ===


def call_claude(prompt: str, *, api_key: str, model: str = MODEL) -> dict:
    """Claude Haiku を呼んで JSON を返す。失敗時は {include: false}。

    Args:
        prompt: 判定プロンプト本文。
        api_key: ANTHROPIC_API_KEY の値。
        model: 使用するモデル名（既定: MODEL 定数）。

    Returns:
        dict: {"include": bool, "line": str?} または {"include": False}。

    Policy:
        - anthropic SDK 未導入 / API 呼出失敗のいずれでも壊さず、
          {include: False} を返して呼び元のステップ列を保つ。
    """
    return _resolve_claude_decision(prompt, api_key, model)


def prepend_change(  # noqa: CR100
    line: str, *, max_keep: int = MAX_KEEP,
) -> bool:
    """top_changes.json の changes 先頭に line を挿入する。

    Args:
        line: 挿入する 1 行文字列。
        max_keep: 保持件数の上限（既定: MAX_KEEP）。

    Returns:
        bool: 実際に書き込みが行われたかどうか。

    Policy:
        - 連続同一行や json 不在 / changes が list でないケースは silent skip し、
          False を返してステップ列を切り上げる。
        - 旧 API 名 `prepend_change` をテスト互換のため維持し、本体は
          private helper に委譲する。
    """
    return _try_prepend_change(line, max_keep)


def render_index() -> None:
    """tools/render_top_changes.py を呼んで index.html を更新する。

    Policy:
        - subprocess.check_call で同期実行し、失敗は呼び元の try/except に委ねる。
    """
    subprocess.check_call([sys.executable, str(RENDER_SCRIPT)], cwd=ROOT)


def amend_with_marker(subject: str, body: str) -> None:
    """直前 commit に top_changes.json + index.html を amend で取り込む。

    Args:
        subject: 直前 commit の subject。
        body: 直前 commit の body。

    Policy:
        - commit body 末尾に AUTO_MARKER を残し、次回 hook で再帰を断つ。
        - メッセージ組み立ては private helper に委譲する。
    """
    new_message = _compose_amend_message(subject, body)
    _stage_amend_files()
    _commit_amend(new_message)


def run_update_top_changes(argv: list[str] | None = None) -> int:
    """post-commit hook 入口: commit を判定し top_changes.json を更新する。

    Args:
        argv: コマンドライン引数（None なら sys.argv[1:] 相当）。

    Returns:
        int: 常に 0（fail パスでも commit を壊さないため）。

    Policy:
        - 「git 取得 → 再帰判定 → API key 検査 → prompt → Claude → prepend →
          render → amend」のステップ列に揃え、本体は委譲のみで構成する。
    """
    return _run_hook(argv)


# 後方互換: 旧 main エントリ名を残す（tests/hook が main を参照）。
def main(argv: list[str] | None = None) -> int:  # noqa: CR100
    """run_update_top_changes の旧名エイリアス。

    Args:
        argv: コマンドライン引数（None なら sys.argv[1:] 相当）。

    Returns:
        int: run_update_top_changes と同じ exit code（常に 0）。

    Policy:
        - 既存テスト (test_update_top_changes.py) と install_hooks.sh の
          `python tools/update_top_changes.py` 起動を壊さないために残す。
    """
    return run_update_top_changes(argv)


# === Internal helpers (private) ===


def _git(*args: str) -> str:  # noqa: CR100
    """git コマンドを実行して標準出力を strip して返す。

    Args:
        *args: git に渡すサブコマンド以下の引数列。

    Returns:
        str: 標準出力（末尾改行を除いた文字列）。

    Policy:
        - cwd=ROOT に固定し、stderr は捨てる。例外は呼び元に伝搬させる。
    """
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, stderr=subprocess.DEVNULL,
    ).strip()


def _today_short() -> str:  # noqa: CR100
    """今日の日付を `5/6` 形式（先頭 0 なし）で返す。

    Returns:
        str: `{month}/{day}` 形式の今日の日付。

    Policy:
        - datetime.date.today() を 1 度だけ参照し、ローカル変数経由で組み立てる。
    """
    import datetime as _dt
    today = _dt.date.today()
    return f"{today.month}/{today.day}"


def _is_auto_amend(subject: str, body: str) -> bool:
    """AUTO_MARKER が含まれていれば自動 amend 由来として True を返す。

    Args:
        subject: commit subject。
        body: commit body。

    Returns:
        bool: subject か body に AUTO_MARKER があれば True。

    Policy:
        - 再帰防止に使うので副作用を持たない単純な部分文字列判定に閉じる。
    """
    return _has_auto_marker(subject) or _has_auto_marker(body)


def _has_auto_marker(text: str) -> bool:
    """text に AUTO_MARKER が含まれるかを判定する。

    Args:
        text: 検査対象文字列。

    Returns:
        bool: AUTO_MARKER を含んでいれば True。

    Policy:
        - in 演算子のみで判定し、空文字列も自然に False になる前提に揃える。
    """
    return AUTO_MARKER in text


def _build_prompt(subject: str, body: str) -> str:
    """Claude Haiku 用プロンプトを組み立てる。

    Args:
        subject: commit subject。
        body: commit body。

    Returns:
        str: Claude Haiku へ送るユーザープロンプト本文。

    Policy:
        - 日付は _today_short で取得し、JSON 出力契約はテンプレートに固定で書く。
    """
    today = _today_short()
    return (
        "次の git commit が「Block Quest（子ども向け Pyxel RPG）の利用者"
        "（小学生）に関係する変更」かを判定し、\n"
        f"関係する場合のみ、小学生でも分かる短い 1 行（漢字最小、絵文字なし、"
        f"日付 \"{today}: \" で始める）を JSON で返してください。\n"
        "関係しない場合は {\"include\": false} を返してください。\n"
        "- 関係する例：新機能、バグ修正で遊びやすくなった、新しい敵 / 装備 / "
        "マップ、UI 改善\n"
        "- 関係しない例：refactor、test、docs（README/AGENTS 等）、build、"
        "CI、内部リファクタ\n\n"
        f"commit subject: {subject}\n"
        f"commit body: {body}\n\n"
        "JSON 形式: {\"include\": true, \"line\": \"...\"} "
        "または {\"include\": false}"
    )


def _load_anthropic_sdk():
    """anthropic SDK の Anthropic クラスを返す。未導入なら None。

    Returns:
        Anthropic | None: anthropic.Anthropic クラス、未導入なら None。

    Policy:
        - ImportError は警告だけ出して None を返し、呼び元のステップ列を保つ。
    """
    try:
        from anthropic import Anthropic
    except ImportError:
        print(
            "[top-changes] anthropic SDK が無いのでスキップ",
            file=sys.stderr,
        )
        return None
    return Anthropic


def _resolve_claude_decision(
    prompt: str, api_key: str, model: str,
) -> dict:
    """SDK 解決 → Claude 呼出 のステップ列を実行して dict を返す。

    Args:
        prompt: 判定プロンプト本文。
        api_key: ANTHROPIC_API_KEY の値。
        model: 使用モデル名。

    Returns:
        dict: Claude 応答 JSON、または {"include": False}。

    Policy:
        - SDK 未導入なら即 {"include": False} を返す責務だけをここに置く。
    """
    sdk_anthropic = _load_anthropic_sdk()
    if sdk_anthropic is None:
        return {"include": False}
    return _invoke_claude(sdk_anthropic, prompt, api_key, model)


def _invoke_claude(
    anthropic_cls,
    prompt: str,
    api_key: str,
    model: str,
) -> dict:
    """Anthropic クライアントを生成し、Claude Haiku で JSON 判定を得る。

    Args:
        anthropic_cls: anthropic.Anthropic クラス。
        prompt: 判定プロンプト本文。
        api_key: ANTHROPIC_API_KEY の値。
        model: 使用モデル名。

    Returns:
        dict: パース済み JSON、失敗時は {"include": False}。

    Policy:
        - 例外は警告して {"include": False} を返し、commit を壊さない。
    """
    client = anthropic_cls(api_key=api_key)
    try:
        return _query_claude(client, prompt, model)
    except Exception as exc:  # noqa: BLE001
        print(
            f"[top-changes] Claude 呼び出し失敗: {exc}",
            file=sys.stderr,
        )
        return {"include": False}


def _query_claude(client, prompt: str, model: str) -> dict:
    """client.messages.create を呼んで JSON dict にパースして返す。

    Args:
        client: anthropic.Anthropic のインスタンス。
        prompt: 判定プロンプト本文。
        model: 使用モデル名。

    Returns:
        dict: モデル応答を json.loads した結果。

    Policy:
        - 失敗時の握り潰しは呼び元 (_invoke_claude) に委ね、ここは純粋に
          API 呼出 → コードフェンス剥がし → json.loads のステップに徹する。
    """
    resp = client.messages.create(
        model=model,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = _unwrap_code_fence(resp.content[0].text.strip())
    return json.loads(text.strip())


def _try_prepend_change(line: str, max_keep: int) -> bool:
    """prepend_change の本体: 前提判定 → 書き込み のステップ列。

    Args:
        line: 挿入する 1 行。
        max_keep: 保持件数の上限。

    Returns:
        bool: 書き込みが行われたら True、skip なら False。

    Policy:
        - public prepend_change を薄い委譲のままに保つためのステップ列。
    """
    if not _can_prepend(line):
        return False
    return _write_prepended_change(line, max_keep)


def _run_hook(argv: list[str] | None) -> int:
    """run_update_top_changes の本体: argv 解決 → git log 取得 → 処理。

    Args:
        argv: 呼出元から渡された argv。

    Returns:
        int: 常に 0。

    Policy:
        - 「argv 解決 → dry-run 判定 → git log 取得 → 処理本体」のステップ列。
    """
    effective_argv = _resolve_argv(argv)
    is_dry_run = "--dry-run" in effective_argv
    git_log = _fetch_latest_commit_log()
    if git_log is None:
        return 0
    return _process_commit_log(git_log, is_dry_run=is_dry_run)


def _unwrap_code_fence(text: str) -> str:
    """``` 〜 ``` で囲まれた本文を剥がして中身だけを返す。

    Args:
        text: モデル応答テキスト。

    Returns:
        str: コードフェンスを剥がした本文（無ければそのまま）。

    Policy:
        - 先頭が ``` で始まる場合のみ split で 2 つ目のセグメントを取り、
          `json` プレフィックスがあれば 4 文字落とす。
    """
    if not text.startswith("```"):
        return text
    inner = text.split("```", 2)[1]
    if inner.lstrip().startswith("json"):
        inner = inner.lstrip()[4:]
    return inner


def _can_prepend(line: str) -> bool:
    """prepend_change の前提条件が揃っているかを判定する。

    Args:
        line: 挿入予定の 1 行。

    Returns:
        bool: top_changes.json が存在し、changes が list で、先頭重複が無ければ True。

    Policy:
        - 副作用無しで判定責務を集約し、書き込み側は専念できるようにする。
    """
    if not TOP_CHANGES_PATH.exists():
        return False
    data = json.loads(TOP_CHANGES_PATH.read_text(encoding="utf-8"))
    changes = data.get("changes", [])
    if not isinstance(changes, list):
        return False
    if _is_duplicate_top(changes, line):
        return False
    return True


def _is_duplicate_top(changes: list, line: str) -> bool:
    """changes の先頭が既に line と同一かどうかを判定する。

    Args:
        changes: top_changes.json の changes リスト。
        line: これから挿入したい 1 行。

    Returns:
        bool: 先頭重複なら True、空 list / 別の値なら False。

    Policy:
        - 連続同一行を防止する 1 件判定だけに責務を絞る。
    """
    if not changes:
        return False
    return changes[0] == line


def _write_prepended_change(line: str, max_keep: int) -> bool:
    """top_changes.json の changes 先頭に line を挿入して書き戻す。

    Args:
        line: 挿入する 1 行。
        max_keep: 保持件数の上限。

    Returns:
        bool: 書き込みに成功すれば True。

    Policy:
        - _can_prepend が True を返した直後だけ呼ばれる前提で再判定はしない。
    """
    data = json.loads(TOP_CHANGES_PATH.read_text(encoding="utf-8"))
    changes = data.get("changes", [])
    changes.insert(0, line)
    data["changes"] = changes[:max_keep]
    TOP_CHANGES_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=4) + "\n",
        encoding="utf-8",
    )
    return True


def _compose_amend_message(subject: str, body: str) -> str:
    """amend 用のコミットメッセージを組み立てる。

    Args:
        subject: 直前 commit の subject。
        body: 直前 commit の body。

    Returns:
        str: AUTO_MARKER を末尾に持つ新しいコミットメッセージ。

    Policy:
        - body が空なら subject のみ、そうでなければ subject + body の形に整える。
    """
    new_body = body.rstrip()
    if AUTO_MARKER not in new_body:
        new_body = (new_body + "\n\n" + AUTO_MARKER).strip()
    if not new_body:
        return subject
    return f"{subject}\n\n{new_body}"


def _stage_amend_files() -> None:
    """amend に取り込む top_changes.json / index.html を staging する。

    Policy:
        - subprocess.check_call で同期実行し、失敗は呼び元に伝搬させる。
    """
    subprocess.check_call(
        ["git", "add", "top_changes.json", "index.html"], cwd=ROOT,
    )


def _commit_amend(new_message: str) -> None:
    """git commit --amend で直前 commit に新メッセージで取り込む。

    Args:
        new_message: 上書きする commit メッセージ。

    Policy:
        - subprocess.check_call で同期実行し、失敗は呼び元に伝搬させる。
    """
    subprocess.check_call(
        ["git", "commit", "--amend", "-m", new_message],
        cwd=ROOT,
    )


def _resolve_argv(argv: list[str] | None) -> list[str]:
    """run_update_top_changes に渡す argv を確定する。

    Args:
        argv: 呼出元から渡された argv（None なら sys.argv[1:]）。

    Returns:
        list[str]: 実際に解釈する argv。

    Policy:
        - None を sys.argv[1:] にフォールバックさせる責務をここに閉じ込める。
    """
    if argv is None:
        return sys.argv[1:]
    return argv


def _fetch_latest_commit_log() -> tuple[str, str] | None:
    """直前 commit の (subject, body) を取得する。失敗時は None。

    Returns:
        tuple[str, str] | None: subject と body のタプル、失敗時は None。

    Policy:
        - git log 取得失敗は警告だけ出して None を返し、commit を壊さない。
    """
    try:
        subject = _git("log", "-1", "--format=%s")
        body = _git("log", "-1", "--format=%b")
    except Exception as exc:  # noqa: BLE001
        print(f"[top-changes] git log 取得失敗: {exc}", file=sys.stderr)
        return None
    return subject, body


def _process_commit_log(
    git_log: tuple[str, str],
    *,
    is_dry_run: bool,
) -> int:
    """commit log を受け取り、再帰判定〜amend までのステップ列を実行する。

    Args:
        git_log: (subject, body) のタプル。
        is_dry_run: True なら Claude 呼出をスキップし prompt 表示のみ。

    Returns:
        int: 常に 0。

    Policy:
        - AUTO_MARKER / API key 不在 / dry-run / Claude 関係なし のいずれも
          途中 return 0 で抜けるステップ列に揃える。
    """
    subject, body = git_log
    if _is_auto_amend(subject, body):
        return 0
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        _warn_missing_api_key()
        return 0
    prompt = _build_prompt(subject, body)
    if is_dry_run:
        _print_dry_run_prompt(prompt)
        return 0
    return _apply_claude_decision(prompt, api_key, subject, body)


def _warn_missing_api_key() -> None:
    """ANTHROPIC_API_KEY 未設定の警告メッセージを stderr に出す。

    Policy:
        - 1 度の print に閉じ込めて呼び元のステップ列を維持する。
    """
    print(
        "[top-changes] ANTHROPIC_API_KEY 未設定のためスキップ "
        "（手で top_changes.json を編集すれば反映できます）",
        file=sys.stderr,
    )


def _print_dry_run_prompt(prompt: str) -> None:
    """--dry-run 時のプロンプト表示を担当する。

    Args:
        prompt: 表示するプロンプト本文。

    Policy:
        - 表示責務だけを切り出し、呼び元はステップ列のままで読める形に保つ。
    """
    print("[top-changes] --dry-run prompt:")
    print(prompt)


def _apply_claude_decision(
    prompt: str,
    api_key: str,
    subject: str,
    body: str,
) -> int:
    """Claude 判定を呼び出し、関係ありなら prepend → render → amend を実行する。

    Args:
        prompt: 判定プロンプト。
        api_key: ANTHROPIC_API_KEY の値。
        subject: 直前 commit の subject。
        body: 直前 commit の body。

    Returns:
        int: 常に 0。

    Policy:
        - 「関係なし / line 不在 / prepend 失敗」のいずれも途中 return 0。
        - render / amend 失敗は警告のみで return 0 にして commit を壊さない。
    """
    result = call_claude(prompt, api_key=api_key)
    if not result.get("include"):
        return 0
    line = result.get("line", "").strip()
    if not line:
        return 0
    if not prepend_change(line):
        return 0
    _run_render_index_safely()
    _run_amend_with_marker_safely(subject, body, line)
    return 0


def _run_render_index_safely() -> None:
    """render_index を呼んで失敗時は警告のみに留める。

    Policy:
        - 例外は print だけして握り潰し、commit を壊さない。
    """
    try:
        render_index()
    except Exception as exc:  # noqa: BLE001
        print(f"[top-changes] render 失敗: {exc}", file=sys.stderr)


def _run_amend_with_marker_safely(subject: str, body: str, line: str) -> None:
    """amend_with_marker を呼んで失敗時は警告のみに留める。

    Args:
        subject: 直前 commit の subject。
        body: 直前 commit の body。
        line: top_changes.json に追加した 1 行（成功時の通知用）。

    Policy:
        - 例外は print だけして握り潰し、commit を壊さない。
    """
    try:
        amend_with_marker(subject, body)
        print(f"[top-changes] 追加: {line}")
    except Exception as exc:  # noqa: BLE001
        print(f"[top-changes] amend 失敗: {exc}", file=sys.stderr)


if __name__ == "__main__":
    sys.exit(run_update_top_changes())
