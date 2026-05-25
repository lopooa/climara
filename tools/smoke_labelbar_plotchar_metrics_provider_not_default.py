from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
]

FORBIDDEN = [
    "build_labelbar_plotchar_metrics_bundle_from_provider(",
    "build_labelbar_adjust_pipeline_from_plotchar_metrics_provider(",
    "compute_labelbar_adjusted_geometry_from_plotchar_metrics_provider(",
    "render_adjusted_labelbar_svg_from_plotchar_metrics_provider(",
    "save_adjusted_labelbar_svg_from_plotchar_metrics_provider(",
    "StaticPlotcharMetricsProvider",
    "build_static_plotchar_metrics_provider(",
    "from ._plotchar_metrics_provider import",
    "from climara.graphics._plotchar_metrics_provider import",
    "from ._labelbar_plotchar_metrics_provider import",
    "from climara.graphics._labelbar_plotchar_metrics_provider import",
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
            "Plotchar metrics provider API must remain explicit-only and out of default render paths."
        )

    print("✅ Plotchar metrics provider API is not used by default render paths")


if __name__ == "__main__":
    main()
