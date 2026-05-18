"""ステータスバーの配置寸法と描画。

このファイルに含まれる関数・クラス：

- StatusBarLayout: 画面上部のステータスバーの寸法を保持する不変レコード
  - rect: 描画用に (x, y, width, height) のタプルを返す
- StatusBar: レベル/ゾーン名/HP/MP と HP/MP バーを画面上部に描画する
  - draw: ステータスバーを 1 行分描画する
  - _draw_background: ステータスバー背景の矩形を描く
  - _draw_status_text: レベル・ゾーン名・HP/MP のテキスト 2 行を描画する
  - _resolve_zone_name: player の位置から表示用ゾーン名を返す
  - _draw_hp_bar: HP バー（背景 + 残量）を描画する
  - _draw_mp_bar: MP バー（背景 + 残量）を描画する
  - _draw_debug_label: デバッグモード時に DEBUG ラベルを重ね描きする

Problems:
    - 描画コードに状態判定（zone 名引き / HP 比率しきい値 / デバッグ表示判定）
      が混ざると、見た目を変えるだけのつもりが Model 整合まで考えることになる。
    - HP/MP バーや zone 名解決の magic number を呼び出し側に散らすと、
      レイアウト変更のたびに複数箇所を編集することになる。

Solutions:
    - StatusBarLayout を frozen dataclass にして、レイアウト記述子として
      scene 間で共有する。
    - StatusBar.draw を「private 委譲のステップ列」に揃え、ゾーン名解決と
      HP/MP バー描画とデバッグ表示を private helper に閉じ込める。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pyxel


@dataclass(frozen=True)
class StatusBarLayout:
    """画面上部のステータスバー（HP / MP / LV / 所持金など）の寸法。"""

    # === Public API ===

    x: int = 0
    y: int = 0
    width: int = 256
    height: int = 16

    def rect(self) -> tuple[int, int, int, int]:  # noqa: CR100
        """描画用に (x, y, width, height) のタプルを返す。

        Returns:
            (x, y, width, height) 形式の矩形寸法。
        Policy:
            - フィールドの単純な並び替えに留め、座標変換や副作用は行わない。
            - メソッド名 rect は他の UI レイアウトと統一されているため固定。
        """
        return (self.x, self.y, self.width, self.height)


@dataclass
class StatusBar:
    """レベル/ゾーン名/HP/MP と HP/MP バーを画面上部に描画する。"""

    # === Public API ===

    game: Any = None

    def draw(self):  # noqa: CR100
        """ステータスバーを 1 行分描画する。

        Policy:
            - 背景塗り → テキスト → HP/MP バー → デバッグ表示の順に
              private helper へ委譲するステップ列に揃える。
            - 判定・整形は private に閉じ込め、本体には副作用呼び出しのみを置く。
        """
        self._draw_background()
        self._draw_status_text()
        self._draw_hp_bar()
        self._draw_mp_bar()
        self._draw_debug_label()

    # === Internal helpers (private) ===

    def _draw_background(self) -> None:
        """ステータスバー背景の矩形を描く。

        Policy:
            - 背景色とサイズは現行表示の互換維持のため固定値。
        """
        pyxel.rect(0, 0, 256, 24, 1)

    def _draw_status_text(self) -> None:
        """レベル・ゾーン名・HP/MP のテキスト 2 行を描画する。

        Policy:
            - ゾーン名解決はフォント有無で日本語/英語辞書を切り替える。
        """
        game = self.game
        player = game.player_model
        zone_name = self._resolve_zone_name(player)
        game.messages.text(4, 2, f"レベル{player.lv} {zone_name}", 7)
        game.messages.text(
            4, 13,
            f"HP{player.hp}/{player.max_hp} MP{player.mp}/{player.max_mp}",
            7,
        )

    def _resolve_zone_name(self, player: Any) -> str:
        """player の位置から表示用ゾーン名を返す。

        Args:
            player: game.player_model 相当のオブジェクト。
        Returns:
            ゾーン名文字列（未定義のときは "???"）。
        Policy:
            - has_jp_font が真なら ZONE_NAMES、偽なら ZONE_NAMES_EN を引く。
        """
        import src.runtime.main_runtime as runtime
        zone = runtime.get_zone(player.y, player.in_dungeon)
        if self.game.has_jp_font:
            return runtime.ZONE_NAMES.get(zone, "???")
        return runtime.ZONE_NAMES_EN.get(zone, "???")

    def _draw_hp_bar(self) -> None:
        """HP バー（背景 + 残量）を描画する。

        Policy:
            - 残量 30% 以下は色 8（赤）、それ以外は色 11（緑）に切り替える。
        """
        player = self.game.player_model
        bar_x = 170
        bar_w = 60
        pyxel.rect(bar_x, 4, bar_w, 6, 0)
        hp_ratio = player.hp / max(1, player.max_hp)
        color = 11 if hp_ratio > 0.3 else 8
        pyxel.rect(bar_x, 4, int(bar_w * hp_ratio), 6, color)

    def _draw_mp_bar(self) -> None:
        """MP バー（背景 + 残量）を描画する。

        Policy:
            - 残量色は 12（青）固定。
        """
        player = self.game.player_model
        bar_x = 170
        bar_w = 60
        pyxel.rect(bar_x, 14, bar_w, 6, 0)
        mp_ratio = player.mp / max(1, player.max_mp)
        pyxel.rect(bar_x, 14, int(bar_w * mp_ratio), 6, 12)

    def _draw_debug_label(self) -> None:
        """デバッグモード時に DEBUG ラベルを重ね描きする。

        Policy:
            - game.debug_mode が真のときだけ描画する。
        """
        if not self.game.debug_mode:
            return
        self.game.messages.text(130, 2, "DEBUG", 8)
