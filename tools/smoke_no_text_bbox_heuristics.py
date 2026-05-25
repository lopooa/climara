from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_labelbar_geometry.py",
    ROOT / "src/climara/graphics/_labelbar_svg_adapter.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
    ROOT / "src/climara/graphics/_text_item.py",
    ROOT / "src/climara/graphics/_labelbar_object.py",
]

FORBIDDEN = [
    "estimate_text",
    "estimate_bbox",
    "approx_text",
    "approx_bbox",
    "approximate_text",
    "approximate_bbox",
    "char_width",
    "character_width",
    "fixed_width",
    "fixed-width",
    "text_width_guess",
    "text_height_guess",
    "svg_text_size",
    "text_size_heuristic",
    "heuristic_bbox",
    "visual spacing",
    "manual offset",
    "fake bbox",
    "fake TextItem bbox",
    "fake MultiText bbox",
]


def main():
    hits = []

    for path in CHECK_FILES:
        if not path.exists():
            continue

        text = path.read_text(encoding="utf-8")
        lowered_lines = text.lower().splitlines()

        for lineno, line in enumerate(lowered_lines, start=1):
            for token in FORBIDDEN:
                if token.lower() in line:
                    hits.append((path.relative_to(ROOT), lineno, text.splitlines()[lineno - 1].strip()))

    if hits:
        print("Found possible heuristic TextItem / MultiText bbox implementation fragments:")
        for path, lineno, line in hits:
            print(f"{path}:{lineno}: {line}")
        raise AssertionError(
            "TextItem / MultiText bbox must not be implemented from visual, SVG, "
            "fixed-width, or manual-offset heuristics. Use the audited NCL "
            "TextItem.c / MultiText.c / LabelBar.c source path first."
        )

    print("✅ no heuristic TextItem / MultiText bbox code found in render/layout paths")


if __name__ == "__main__":
    main()
