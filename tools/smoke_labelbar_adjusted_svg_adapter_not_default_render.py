from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
]

FORBIDDEN = [
    "labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics(",
    "from ._labelbar_svg_adapter import labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics",
    "from climara.graphics._labelbar_svg_adapter import labelbar_to_adjusted_svg_primitives_from_supplied_plotchar_metrics",
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
            "Adjusted LabelBar SVG adapter is explicit-only and must not be used by default renderer yet."
        )

    print("✅ adjusted LabelBar SVG adapter is not used by default renderer")


if __name__ == "__main__":
    main()
