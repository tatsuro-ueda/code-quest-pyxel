"""画面エフェクト Service（P1-G14 で Game から 2 メソッドを取り込み）。

このファイルに含まれる関数・クラス：

- VfxSystem: VFX の type/timer state を保持する dataclass
  - start: 指定タイプの VFX を起動する public メソッド
  - draw_overlay: アクティブな VFX の点滅オーバーレイを描画する public メソッド
  - _resolve_flash_config: VFX_FLASH から指定タイプの設定を引く private メソッド
  - _apply_flash_config: 取得済み config を type/timer に反映する private メソッド
  - _draw_overlay_if_active: アクティブ判定の下で overlay 描画を実行する private メソッド
  - _is_inactive: timer 切れで描画不要かを返す述語メソッド
  - _is_blink_frame: 現在フレームが点滅 ON 側かを返す述語メソッド
  - _draw_color_overlay: 指定色のオーバーレイを実描画する private メソッド

Problems:
    - VFX の type 文字列と timer を Game 直書きにすると、判定と
      描画が混ざってシーン側からテストしづらくなる。
    - public メソッドに if/early-return を直書きすると、ステップ列で
      ない CR204 の指摘が出て読み下しの順序が崩れる。

Solutions:
    - 本 Service は (type, timer) の state-only に保ち、設定参照は
      `_resolve_flash_config` に集約して描画は vfx_overlay に委譲する。
    - public メソッドは「述語呼び出し + private 委譲 + return」の
      ステップ列だけにし、分岐や config 解決は private 側に押し込む。
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.shared.ui.vfx_overlay import draw_vfx_overlay


@dataclass
class VfxSystem:
    """画面エフェクトの状態と描画。"""

    # === Public API ===

    game: Any = None
    timer: int = 0
    type: str = ""  # noqa: CR100

    def start(self, vfx_type: str) -> None:
        """指定タイプの VFX を発動する。

        Args:
            vfx_type: VFX_FLASH のキー文字列。
        Policy:
            - 2026-05-07 改訂（CJ44 確定版）：vfx_enabled の判定は撤去。VFX は常に ON。
            - 設定が見つからないキーは無視（state を触らない）。
        """
        flash_config = self._resolve_flash_config(vfx_type)
        self._apply_flash_config(vfx_type, flash_config)
        return

    def draw_overlay(self) -> None:
        """アクティブな VFX の点滅オーバーレイを描画する（VFX は常に ON）。

        Policy:
            - timer が切れている、または config 不在のときは何もしない。
            - timer が偶数フレームのときだけ色を載せて点滅させる。
        """
        self._draw_overlay_if_active()
        return

    # === Internal helpers (private) ===

    def _resolve_flash_config(self, vfx_type: str) -> dict | None:
        """VFX_FLASH から指定タイプの設定 dict を返す。

        Args:
            vfx_type: VFX_FLASH のキー文字列。
        Returns:
            dict | None: 一致する config、なければ None。
        Policy:
            - main_runtime の遅延 import で循環参照を回避する。
        """
        import src.runtime.main_runtime as main_runtime
        return main_runtime.VFX_FLASH.get(vfx_type)

    def _apply_flash_config(
        self,
        vfx_type: str,
        flash_config: dict | None,
    ) -> None:
        """取得済み config を (type, timer) に反映する。

        Args:
            vfx_type: 起動対象の VFX キー。
            flash_config: _resolve_flash_config の戻り値。
        Policy:
            - config が None のときは state を触らない。
        """
        if flash_config is None:
            return
        self.type = vfx_type
        self.timer = flash_config["duration"]

    def _draw_overlay_if_active(self) -> None:
        """アクティブで点滅 ON フレームのときだけ overlay を描く。

        Policy:
            - timer 切れ、config 不在、点滅 OFF フレームでは何もしない。
        """
        if self._is_inactive():
            return
        flash_config = self._resolve_flash_config(self.type)
        if flash_config is None:
            return
        if not self._is_blink_frame():
            return
        self._draw_color_overlay(flash_config["color"])

    def _is_inactive(self) -> bool:
        """timer 切れで描画不要かを返す。

        Returns:
            bool: timer <= 0 なら True。
        Policy:
            - 起動前と終了後の双方を 1 つの述語で表す。
        """
        return self.timer <= 0

    def _is_blink_frame(self) -> bool:
        """現在フレームが点滅 ON 側かを返す。

        Returns:
            bool: timer が偶数なら True。
        Policy:
            - 偶数フレームのみ色を載せて点滅効果を作る。
        """
        return self.timer % 2 == 0

    def _draw_color_overlay(self, color: int) -> None:
        """指定色のオーバーレイを実描画する。

        Args:
            color: VFX_FLASH config の color 値。
        Policy:
            - 描画は shared.ui.vfx_overlay.draw_vfx_overlay に委譲する。
        """
        draw_vfx_overlay(color)
