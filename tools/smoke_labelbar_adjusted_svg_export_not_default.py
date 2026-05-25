from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
]

FORBIDDEN = [
    "render_adjusted_labelbar_svg_from_supplied_plotchar_metrics(",
    "save_adjusted_labelbar_svg_from_supplied_plotchar_metrics(",
    "add_adjusted_labelbar_primitives_to_svg_document(",
    "from ._labelbar_adjusted_svg_export import",
    "from climara.graphics._labelbar_adjusted_svg_export import",
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
            "Adjusted LabelBar SVG export must stay explicit-only and must not be used by default render paths."
        )

    print("✅ adjusted LabelBar SVG export is not used by default render paths")


if __name__ == "__main__":
    main()
