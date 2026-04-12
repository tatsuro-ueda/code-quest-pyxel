.PHONY: gen sync test build

gen:
	python3 tools/gen_data.py
	python3 tools/sync_main_data.py

sync:
	python3 tools/sync_main_data.py

test:
	python3 -m pytest test/ -v

build: gen test
	python3 tools/build_web_release.py
