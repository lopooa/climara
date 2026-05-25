from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
]

FORBIDDEN = [
    "build_labelbar_adjust_pipeline_from_plotchar_metrics_bundle(",
    "compute_labelbar_adjusted_geometry_from_plotchar_metrics_bundle(",
    "render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(",
    "save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(",
    "from ._labelbar_plotchar_metrics_bundle import",
    "from climara.graphics._labelbar_plotchar_metrics_bundle import",
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
            "LabelBar Plotchar metrics bundle API must stay explicit-only and out of default render paths."
        )

    print("✅ LabelBar Plotchar metrics bundle API is not used by default render paths")


if __name__ == "__main__":
    main()
