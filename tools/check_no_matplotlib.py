from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

patterns = [
    "import matplotlib",
    "from matplotlib",
    "pyplot",
    "plt.",
    "fig.",
    "ax.",
    "add_axes",
    "colorbar",
    "matplotlib.",
]

ignore = {
    "tools/check_no_matplotlib.py",
}

bad = []

for path in (ROOT / "src" / "climara").rglob("*.py"):
    rel = path.relative_to(ROOT).as_posix()

    if rel in ignore:
        continue

    text = path.read_text(encoding="utf-8", errors="ignore")

    for lineno, line in enumerate(text.splitlines(), start=1):
        if any(p in line for p in patterns):
            bad.append((rel, lineno, line.rstrip()))

if bad:
    print("Matplotlib-related code found:\n")

    for rel, lineno, line in bad:
        print(f"{rel}:{lineno}: {line}")

    raise SystemExit(1)

print("OK: no Matplotlib-related code found in src/climara")
