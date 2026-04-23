.PHONY: gen test build

# P3-F: sync_main_data.py は廃止。gen_data.py が src/generated/*.py を生成し、
# Phase 1.5 shim の import * と Phase 2 codemaker_bundler がそれを読む。

gen:
	python3 tools/gen_data.py

test:
	python3 -m pytest test/ -v

build: gen test
	python3 tools/build_web_release.py
