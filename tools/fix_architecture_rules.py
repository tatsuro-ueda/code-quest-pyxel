"""このスクリプトは architecture rule warning に対する一回限りの安全な autofix 入口。checker が返した warning のうち、generated file の再生成、manifest 追記、runtime entry chain の正規化、distribution artifact 周辺の整形のように副作用範囲を限定できるものだけを適用する。自動で判断しきれない問題は直さずに残し、修正結果と適用した fix 一覧を JSON で返す。"""

from architecture_rules.fix_architecture_rules import *  # noqa: F401,F403
from architecture_rules.fix_architecture_rules import main


if __name__ == "__main__":
    raise SystemExit(main())
