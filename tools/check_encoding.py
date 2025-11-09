import os
import sys
from pathlib import Path

TARGET_EXTS = {".py", ".md", ".json", ".yml", ".yaml", ".txt", ".html", ".css", ".js"}
ROOT = Path(__file__).resolve().parents[1]

bad_files = []

for path in ROOT.rglob("*"):
    if not path.is_file():
        continue
    if path.suffix.lower() not in TARGET_EXTS:
        continue
    try:
        with open(path, "rb") as f:
            data = f.read()
        # Try decode as UTF-8 strictly
        data.decode("utf-8")
    except Exception as e:
        bad_files.append((str(path.relative_to(ROOT)), str(e)))

if bad_files:
    print("[ENCODING CHECK] Non-UTF-8 files detected:")
    for fp, err in bad_files:
        print(f" - {fp}: {err}")
    sys.exit(1)
else:
    print("[ENCODING CHECK] All checked files are UTF-8.")
