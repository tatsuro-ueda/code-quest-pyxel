from pathlib import Path


_RUNTIME_PATH = Path(__file__).resolve().parent / "src" / "runtime" / "main_development_runtime.py"
exec(compile(_RUNTIME_PATH.read_text(encoding="utf-8"), str(_RUNTIME_PATH), "exec"), globals())

if __name__ == "__main__":
    run()
