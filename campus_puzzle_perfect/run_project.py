from pathlib import Path
from contextlib import redirect_stdout
from main import main

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "output" / "schedule_report.txt"

with OUTPUT_FILE.open("w", encoding="utf-8") as file:
    with redirect_stdout(file):
        main()

print(f"Schedule report created: {OUTPUT_FILE}")
