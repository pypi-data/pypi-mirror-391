import re
from pathlib import Path
import subprocess

NAMES = [
    ["db-talk", "DB-Talk"],
    ["talk-db", "Talk-DB"],
    ["talking-db", "Talking-DB"],
    ["talking-database", "Talking-DB"],
    ["langquery", "LangQuery"],
    #["nldb", "NLDB"], used
    # askdb
    ["nl-database", "NL-Database"],
    ["nlq-db", "NLQ-DB"],
    ["db-nlq", "DB-NLQ"],
    ["speakql", "SpeakQL"],
]
FILES = [
    "pyproject.toml",
    "README.md",
]


def replace_name(old_names: list[str], new_names: list[str], files: list[str] = None):
    files = files or FILES
    for i in range(len(old_names)):
        old_name = old_names[i]
        new_name = new_names[i]
        for path in files:
            p = Path(path)
            p.write_text(
                re.sub(
                    fr'(?<![\\/\w]){old_name}\b',
                    new_name,
                    p.read_text(encoding="utf-8"),
                    flags=re.M
                ), encoding="utf-8"
            )


prev = NAMES[0]
for nxt in NAMES[1:] + [NAMES[0]]:
    print(f"Building for project name: {nxt[0]}...")
    replace_name(prev, nxt)
    subprocess.run(["python", "-m", "build"], check=True)
    prev = nxt
print("All builds completed.")
