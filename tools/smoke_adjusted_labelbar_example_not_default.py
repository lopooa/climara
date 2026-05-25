from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

CHECK_FILES = [
    ROOT / "src/climara/graphics/_render_svg.py",
    ROOT / "src/climara/graphics/_panel.py",
    ROOT / "src/climara/graphics/_workstation.py",
]

FORBIDDEN = [
    "adjusted_labelbar_supplied_metrics",
    "build_uniform_labelbar_plotchar_metrics_bundle(",
    "save_adjusted_labelbar_svg_from_plotchar_metrics_bundle(",
    "render_adjusted_labelbar_svg_from_plotchar_metrics_bundle(",
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
            "Adjusted LabelBar example/API must remain explicit-only and out of default render paths."
        )

    print("✅ adjusted LabelBar example/API is not used by default render paths")


if __name__ == "__main__":
    main()
