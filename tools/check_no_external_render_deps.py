from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_PATHS = [
    ROOT / "src" / "climara",
    ROOT / "pyproject.toml",
]

BANNED = [
    "import matplotlib",
    "from matplotlib",
    "matplotlib.",
    "pyplot",
    "plt.",
    "import cartopy",
    "from cartopy",
    "cartopy.",
]


def main():
    hits = []

    for path in CHECK_PATHS:
        if path.is_file():
            files = [path]
        else:
            files = sorted(path.rglob("*.py"))

        for file in files:
            text = file.read_text(encoding="utf-8", errors="ignore")
            for lineno, line in enumerate(text.splitlines(), start=1):
                for word in BANNED:
                    if word in line:
                        hits.append((file.relative_to(ROOT), lineno, line.strip()))

    if hits:
        for file, lineno, line in hits:
            print(f"{file}:{lineno}: {line}")
        raise SystemExit(1)

    print("OK: no external Matplotlib/Cartopy render dependencies found in src/climara or pyproject.toml")


if __name__ == "__main__":
    main()
