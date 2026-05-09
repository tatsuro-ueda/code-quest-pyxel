.PHONY: gen test build verify-module-docstrings verify-cj-cjob verify-scene-cj-map verify

# P3-F: sync_main_data.py は廃止。gen_data.py が src/generated/*.py を生成し、
# Phase 1.5 shim の import * と Phase 2 codemaker_bundler がそれを読む。

gen:
	python3 tools/gen_data.py

test:
	python3 -m pytest test/ -v

# モジュール docstring の drift 検出（A2 / B1）。
# 横展開未完のため --skip-missing-docstring で段階移行モード。
# docstring が無い／箇条書きが無いファイルはスキップし、整備済ファイルのみ件数一致を検証する。
verify-module-docstrings:
	python3 tools/verify_module_docstrings.py src/ --skip-missing-docstring

# タスクノートと customer-journeys.md / customer-jobs.md の整合（C1 / C2）。
verify-cj-cjob:
	python3 tools/verify_cj_cjob.py

# tools/scene_to_cj.json 自体の健全性（C3）。
# 対応表中の CJ ID が customer-journeys.md に実在するかをチェック。
verify-scene-cj-map:
	python3 tools/scene_to_cj.py --verify-only

# まとめて全検証（B2 / C4）。
verify: verify-module-docstrings verify-cj-cjob verify-scene-cj-map

build: verify gen test
	python3 tools/build_web_release.py
