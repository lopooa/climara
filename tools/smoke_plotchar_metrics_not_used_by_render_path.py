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
    "compute_plotchar_extent_metrics(",
    "build_plotchar_metrics_request(",
    "build_plotchar_metrics_request_from_text_bbox_request(",
    "from ._plotchar_metrics import",
    "from climara.graphics._plotchar_metrics import",
    "from ._text_bbox_plotchar_bridge import",
    "from climara.graphics._text_bbox_plotchar_bridge import",
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
            "Plotchar metrics are guarded and must not be used by render/layout paths "
            "until audited NCL c_plchhq / c_pcgetr semantics are implemented."
        )

    print("✅ Plotchar metrics are not used by render/layout paths")


if __name__ == "__main__":
    main()
