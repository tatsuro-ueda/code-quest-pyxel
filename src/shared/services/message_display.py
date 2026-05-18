"""短いメッセージウィンドウ制御（P1-G12 で Game から 12 メソッドを取り込み）。

このファイルに含まれる関数・クラス：

- MessageDisplay: overlay 的な短いメッセージウィンドウの state holder クラス
  - show: メッセージ行を差し替えて index をリセットするメソッド
  - enter: map に戻る前提で message state に入るメソッド
  - dialog_text: dialog runner から scene の最初の 1 text を取得するメソッド
  - dialog_lines: dialog runner から scene の全行を取得するメソッド
  - any_advance_btnp: 任意の進行入力（決定/キャンセル/方向）を判定する述語メソッド
  - advance_page: 次のページ index と終端判定を返すメソッド
  - current_page_lines: 現在ページの折返し済み行を返すメソッド
  - update: message state のページ送りとコールバック呼出しを行うメソッド
  - wrap_text: 文字列を max_chars で簡易に折返すメソッド
  - say: デバッグ用に任意の値を画面左上にオーバーレイ表示するメソッド
  - text: 文字列を misaki_gothic 8x8 で描画するメソッド (shared/ui への委譲)
  - draw_say_overlay: say() で蓄えたメッセージを画面左上に重ね描きするメソッド
  - draw_window: メッセージウィンドウを描画するメソッド (shared/ui への委譲)
  - _is_index_out_of_range: lines/index が空または範囲外かを返す述語メソッド
  - _compute_current_page_lines: 範囲外判定 + 折返し + max_rows カットを行うメソッド
  - _run_advance_step: 進行入力があればページ送りとコールバック呼出しを行うメソッド
  - _wrap_all_raw_lines: text を raw 行に分割し各 raw 行を折返して連結するメソッド
  - _wrap_one_raw_line: 1 つの raw 行を max_chars で分割するメソッド
  - _trim_say_buffer: say_buffer を 12 件以内に整えるメソッド
  - _advance_and_finish: ページ送りを進め終端ならコールバックを呼ぶメソッド

Problems:
    - structured dialog は dialog_runner.py が担当する一方、1〜数行のメッセージ
      表示も同じく overlay 的に複数 scene から呼ばれるため、共通の state holder
      が必要だが、Game クラスにメソッドを直書きすると責務が肥大化する。
    - ページ送り・折返し・任意進行入力判定などの制御フローを public メソッド
      に直書きすると CR203/CR204 違反になり、可読性も落ちる。

Solutions:
    - P1-G12 で Game から 12 メソッドを MessageDisplay にまとめ、overlay state
      の責務を 1 箇所に集約する（structured dialog は dialog_runner.py 担当）。
    - 制御フローを `_is_index_out_of_range` / `_wrap_one_raw_line` /
      `_trim_say_buffer` / `_advance_and_finish` などの private helper に
      切り出し、public メソッドは「述語呼び出し + private 委譲 + return」
      のステップ列に揃える。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.shared.services.input_bindings import (
    CANCEL_BUTTONS,
    CONFIRM_BUTTONS,
    DOWN_BUTTONS,
    LEFT_BUTTONS,
    RIGHT_BUTTONS,
    UP_BUTTONS,
)
from src.shared.ui.message_window import (
    MessageWindowLayout,
    draw_message_window,
    draw_say_overlay,
)
from src.shared.ui.text_renderer import draw_text


@dataclass
class MessageDisplay:
    """メッセージウィンドウの表示状態（P1-G12 で Game から取り込み）。"""

    game: Any = None
    lines: list[str] = field(default_factory=list)
    index: int = 0
    callback: Any = None
    say_buffer: list[str] = field(default_factory=list)

    # === Public API ===

    def show(self, lines, callback=None):
        """メッセージ行を差し替えて index をリセットする。

        Args:
            lines: 表示したいメッセージ行のリスト。
            callback: 全ページ送り完了時に呼ぶコールバック（省略可）。
        Policy:
            - 行列と callback を差し替えるだけで state 遷移は行わない。
        """
        self.lines = lines
        self.index = 0
        self.callback = callback

    def enter(self, lines, callback=None):
        """map に戻る前提で message state に入る。

        Args:
            lines: 表示したいメッセージ行のリスト。
            callback: 全ページ送り完了時に呼ぶコールバック（省略可）。
        Policy:
            - show() で内容を差し替えてから game の state を "message" に切替える。
        """
        self.show(lines, callback=callback)
        game = self.game
        game.prev_state = "map"
        game.state = "message"

    def dialog_text(self, scene_name, **extra_context):  # noqa: CR100
        """dialog runner から scene の最初の 1 text を取得する。

        Args:
            scene_name: dialog scene の識別名。
            **extra_context: dialog template に渡す追加 context。
        Returns:
            scene の最初の text 文字列。
        Policy:
            - dialog runner への薄い委譲のみで、state は変更しない。
        """
        game = self.game
        return game.dialog.start(
            scene_name,
            state=game.player_model.dialog_flags,
            extra_context=extra_context,
        ).text

    def dialog_lines(self, scene_name, **extra_context):  # noqa: CR100
        """dialog runner から scene の全行を取得する。

        Args:
            scene_name: dialog scene の識別名。
            **extra_context: dialog template に渡す追加 context。
        Returns:
            scene の全行を表す list[str]。
        Policy:
            - dialog runner への薄い委譲のみで、state は変更しない。
        """
        game = self.game
        return game.dialog.load_all_lines(
            scene_name,
            state=game.player_model.dialog_flags,
            extra_context=extra_context,
        )

    def any_advance_btnp(self) -> bool:  # noqa: CR100
        """メッセージを進める入力。決定/キャンセル/方向のどれでもOK。

        Returns:
            いずれかの進行入力 btnp が True なら True。
        Policy:
            - 決定/キャンセル/上下左右の btnp を OR で束ねる。
        """
        btnp = self.game.input_state.btnp
        return (
            btnp(CONFIRM_BUTTONS)
            or btnp(CANCEL_BUTTONS)
            or btnp(UP_BUTTONS)
            or btnp(DOWN_BUTTONS)
            or btnp(LEFT_BUTTONS)
            or btnp(RIGHT_BUTTONS)
        )

    def advance_page(self, index, lines):
        """次のページ index と終端判定を返す。

        Args:
            index: 現在のページ index。
            lines: メッセージ行のリスト。
        Returns:
            (next_index, done) のタプル。done は次 index が末尾以降なら True。
        Policy:
            - 純粋計算で副作用なし。
        """
        next_index = index + 1
        return next_index, next_index >= len(lines)

    def current_page_lines(  # noqa: CR100
        self, lines, index, *, max_chars=28, max_rows=3,
    ):
        """現在ページの折返し済み行を返す。

        Args:
            lines: メッセージ行のリスト。
            index: 現在のページ index。
            max_chars: 1 行あたりの最大文字数。
            max_rows: 1 ページあたりの最大行数。
        Returns:
            折返し済みの行リスト（範囲外なら空リスト）。
        Policy:
            - 範囲外判定と折返しはすべて _compute_current_page_lines に
              委譲し、本体は private 委譲 + return のステップ列に留める。
        """
        return self._compute_current_page_lines(
            lines, index, max_chars=max_chars, max_rows=max_rows,
        )

    def update(self):
        """message state のページ送りとコールバック呼出し。

        Policy:
            - 入力判定からコールバック呼出しまでをすべて _run_advance_step に委譲し、
              本体は private 委譲のみに留める。
        """
        self._run_advance_step()

    def wrap_text(self, text: str, max_chars: int = 28) -> list[str]:
        """簡易な折返し（CJK文字幅考慮なし、おおよその目安）。

        Args:
            text: 折返したい文字列（"\\n" は raw 行区切りとして扱う）。
            max_chars: 1 行あたりの最大文字数。
        Returns:
            折返し済み行のリスト。空入力でも `[""]` を返す。
        Policy:
            - raw 行の走査と折返しは _wrap_all_raw_lines に委譲し、
              本体は private 委譲 + return のステップ列に留める。
        """
        return self._wrap_all_raw_lines(text, max_chars)

    def say(self, *args) -> None:
        """デバッグ用: 任意の値を画面左上にオーバーレイ表示する。

        Args:
            *args: 任意の値（str(...) して空白連結する）。
        Policy:
            - 連結した msg を say_buffer に push し、長さ制御は
              _trim_say_buffer に委譲する。
        """
        msg = " ".join(str(a) for a in args)
        self.say_buffer.append(msg)
        self._trim_say_buffer()

    def text(self, x: int, y: int, s: str, col: int) -> None:
        """文字列を misaki_gothic 8x8 で描画する (shared/ui への委譲)。

        Args:
            x: 描画 x 座標。
            y: 描画 y 座標。
            s: 描画文字列。
            col: Pyxel 色番号。
        Policy:
            - shared/ui/text_renderer の draw_text に丸投げする薄い委譲。
        """
        draw_text(x, y, s, col)

    def draw_say_overlay(self):
        """say() で蓄えたメッセージを画面左上に重ね描きする (shared/ui への委譲)。

        Policy:
            - shared/ui/message_window の draw_say_overlay に say_buffer を渡す。
        """
        draw_say_overlay(self.say_buffer, draw_text_fn=self.text)

    def draw_window(self):
        """メッセージウィンドウを描画する (shared/ui への委譲)。

        Policy:
            - MessageWindowLayout を取り出し、current_page_lines の結果を
              shared/ui の draw_message_window に渡すだけ。
        """
        layout = MessageWindowLayout()
        lines = self.current_page_lines(
            self.lines,
            self.index,
            max_chars=layout.wrap_width,
            max_rows=3,
        )
        draw_message_window(lines, layout=layout, draw_text_fn=self.text)

    # === Internal helpers (private) ===

    def _is_index_out_of_range(self, lines, index) -> bool:
        """lines/index が空または範囲外かを判定する。

        Args:
            lines: メッセージ行のリスト。
            index: 現在のページ index。
        Returns:
            lines が空 / index が負 / index が末尾以降のいずれかなら True。
        Policy:
            - 範囲外判定の 1 箇所に集約し、current_page_lines を
              述語呼び出し + 委譲 + return のステップ列に保つ。
        """
        if not lines:
            return True
        if index < 0:
            return True
        return index >= len(lines)

    def _compute_current_page_lines(
        self, lines, index, *, max_chars: int, max_rows: int,
    ) -> list[str]:
        """範囲外判定 + 折返し + max_rows カットを一括で行う。

        Args:
            lines: メッセージ行のリスト。
            index: 現在のページ index。
            max_chars: 1 行あたりの最大文字数。
            max_rows: 1 ページあたりの最大行数。
        Returns:
            折返し済みの行リスト（範囲外なら空リスト）。
        Policy:
            - public 側を述語呼び出し + 委譲 + return に保つため、
              制御フローをここに閉じ込める。
        """
        if self._is_index_out_of_range(lines, index):
            return []
        return self.wrap_text(lines[index], max_chars=max_chars)[:max_rows]

    def _run_advance_step(self) -> None:
        """進行入力があればページ送りとコールバック呼出しを行う。

        Policy:
            - any_advance_btnp が False の間は早期 return し、True のときだけ
              _advance_and_finish に委譲する。
        """
        if not self.any_advance_btnp():
            return
        self._advance_and_finish()

    def _wrap_all_raw_lines(self, text: str, max_chars: int) -> list[str]:
        """text を raw 行に分割し、各 raw 行を折返して連結する。

        Args:
            text: 折返したい文字列（"\\n" は raw 行区切りとして扱う）。
            max_chars: 1 行あたりの最大文字数。
        Returns:
            折返し済み行のリスト。空入力でも `[""]` を返す。
        Policy:
            - 1 raw 行ぶんの折返しは _wrap_one_raw_line に委譲し、
              ここでは raw 行を回して結果を集約するだけ。
        """
        out: list[str] = []
        for raw_line in text.split("\n"):
            out.extend(self._wrap_one_raw_line(raw_line, max_chars))
        return out or [""]

    def _wrap_one_raw_line(self, raw_line: str, max_chars: int) -> list[str]:
        """1 つの raw 行を max_chars 単位で分割する。

        Args:
            raw_line: 改行を含まない 1 raw 行。
            max_chars: 1 行あたりの最大文字数。
        Returns:
            分割後の行リスト（末尾に max_chars 未満の余りも含む）。
        Policy:
            - CJK 文字幅は考慮せず、文字数で純粋に区切るだけ。
        """
        out: list[str] = []
        cur = ""
        for ch in raw_line:
            cur += ch
            if len(cur) >= max_chars:
                out.append(cur)
                cur = ""
        if cur:
            out.append(cur)
        return out

    def _trim_say_buffer(self) -> None:
        """say_buffer を 12 件以内に整える。

        Policy:
            - 12 件を超えたら末尾 12 件まで縮める。
        """
        if len(self.say_buffer) > 12:
            self.say_buffer = self.say_buffer[-12:]

    def _advance_and_finish(self) -> None:
        """ページ送りを進め、終端ならコールバックを呼ぶ。

        Policy:
            - advance_page で index を更新し、done のとき prev_state に戻して
              callback があれば呼び出す。
        """
        game = self.game
        self.index, done = self.advance_page(self.index, self.lines)
        if not done:
            return
        game.state = game.prev_state
        if self.callback:
            self.callback()
