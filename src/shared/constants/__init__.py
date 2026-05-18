"""ゲーム全体の定数 / 自動生成データ表をまとめるパッケージの入口。

Problems:
    - タイル / スプライト / ゲーム定数を散らすと、SSoT (YAML→generator)
      との一方通行を保てなくなる。

Solutions:
    - constants パッケージに生成済みデータ (tile_data / sprite_data) と
      手書き定数 (game_config) を集約し、改変経路を限定する。
"""
