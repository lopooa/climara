from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
]

FORBIDDEN = [
    "render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(",
    "save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(",
    "render_adjusted_labelbar_svg_from_supplied_plotchar_metrics(",
    "save_adjusted_labelbar_svg_from_supplied_plotchar_metrics(",
    "compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle(",
    "build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle(",
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
            "Adjusted LabelBar public API must remain explicit-only and out of default render paths."
        )

    print("✅ adjusted LabelBar public API is not used by default render paths")


if __name__ == "__main__":
    main()
