from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_labelbar_geometry.py",
    ROOT / "src/climara/graphics/_labelbar_svg_adapter.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
]

FORBIDDEN = [
    "compute_labelbar_adjust_writeback_semantics(",
    "LabelBarAdjustWritebackSemantics",
    "from ._labelbar_adjust_writeback_semantics import",
    "from climara.graphics._labelbar_adjust_writeback_semantics import",
]


def main():
    hits = []

    for path in CHECK_FILES:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        for lineno, line in enumerate(text.splitlines(), start=1):
            for token in FORBIDDEN:
                if token in line:
                    hits.append((path.relative_to(ROOT), lineno, line.strip()))

    if hits:
        for path, lineno, line in hits:
            print(f"{path}:{lineno}: {line}")
        raise AssertionError(
            "LabelBar AdjustGeometry write-back semantics must not be used by render/layout paths yet."
        )

    print("✅ LabelBar AdjustGeometry write-back semantics are not used by render/layout paths")


if __name__ == "__main__":
    main()
