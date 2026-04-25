from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ExploreModel:
    """フィールド探索時のモード・移動演出 state を保持する。

    P1-G3 で Game から walk_frame / walk_timer / move_cooldown / a_cooldown
    を scene-local state として取り込んだ（Q2A）。
    """

    mode: str = "map"
    walk_frame: int = 0
    walk_timer: int = 0
    move_cooldown: int = 0
    a_cooldown: bool = False

    def start_a_cooldown(self) -> None:
        """次フレームの A 押下を 1 回吸収するクールダウンを立てる。

        他 scene からマップへ遷移する直前に呼び、ロード直後／ending 直後／
        町を出た直後に残っている A 押下が町メニュー等を暴発させるのを防ぐ。
        framework-rule.md M4-1 で他 Scene の Model 内部状態への直接代入は
        禁止のため、外部 caller は本メソッド経由で cooldown を立てる。
        """
        self.a_cooldown = True
