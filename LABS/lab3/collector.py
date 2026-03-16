from pathlib import Path
with open("all_py.txt", "w", encoding="utf-8") as out:
    for f in sorted(Path("./src").rglob("*.py")):
        out.write(f"\n\n# ===== FILE: {f} =====\n\n")
        out.write(f.read_text(encoding="utf-8"))
