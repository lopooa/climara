from pathlib import Path

from climara.graphics._labelbar_object import build_hlu_labelbar
from climara.graphics._render_svg import save_svg


def _read(path):
    return path.read_text(encoding="utf-8")


def _count(text, token):
    return text.count(token)


def main():
    out = Path("outputs/figures/labelbar_line_full_render_smoke.svg")
    out.parent.mkdir(parents=True, exist_ok=True)

    labelbar = build_hlu_labelbar(
        rect=(0.15, 0.82, 0.70, 0.18),
        colors=("#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62", "#b2182b"),
        labels=("A", "B", "C", "D"),
        resources={
            "EndStyle": "IncludeOuterBoxes",
            "lbBoxLinesOn": True,
            "lbBoxSeparatorLinesOn": True,
            "lbBoxLineColor": "purple",
            "lbBoxLineThicknessF": 2.5,
            "lbPerimOn": True,
            "lbPerimColor": "orange",
            "lbPerimThicknessF": 3.0,
            "lbPerimFill": "HollowFill",
        },
    )

    save_svg(labelbar, out, width=900, height=500)
    text = _read(out)

    if "<svg" not in text:
        raise RuntimeError("full-render line smoke did not produce SVG")

    if "purple" not in text:
        raise RuntimeError("SVG missing lbBoxLineColor")

    if "orange" not in text:
        raise RuntimeError("SVG missing lbPerimColor")

    if 'stroke-width="2.500"' not in text:
        raise RuntimeError("SVG missing lbBoxLineThicknessF stroke width")

    if 'stroke-width="3.000"' not in text:
        raise RuntimeError("SVG missing lbPerimThicknessF stroke width")

    if _count(text, "<polygon") < 6:
        raise RuntimeError("SVG should contain perim polygon plus box polygons")

    if _count(text, "<line") < 8:
        raise RuntimeError("SVG should contain box outline and separator lines")

    for label in ("A", "B", "C", "D"):
        if label not in text:
            raise RuntimeError(f"SVG missing label text: {label}")

    no_separator = Path("outputs/figures/labelbar_line_no_separator_full_render_smoke.svg")
    labelbar_no_separator = build_hlu_labelbar(
        rect=(0.15, 0.82, 0.70, 0.18),
        colors=("#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62", "#b2182b"),
        labels=("A", "B", "C", "D"),
        resources={
            "EndStyle": "IncludeOuterBoxes",
            "lbBoxLinesOn": True,
            "lbBoxSeparatorLinesOn": False,
            "lbBoxLineColor": "purple",
            "lbBoxLineThicknessF": 2.5,
        },
    )

    save_svg(labelbar_no_separator, no_separator, width=900, height=500)
    text_no_separator = _read(no_separator)

    if _count(text_no_separator, "<line") != 4:
        raise RuntimeError(
            "lbBoxSeparatorLinesOn=False should leave only the four bar outline lines"
        )

    no_box_lines = Path("outputs/figures/labelbar_line_off_full_render_smoke.svg")
    labelbar_no_box_lines = build_hlu_labelbar(
        rect=(0.15, 0.82, 0.70, 0.18),
        colors=("#2166ac", "#67a9cf", "#f7f7f7", "#ef8a62", "#b2182b"),
        labels=("A", "B", "C", "D"),
        resources={
            "EndStyle": "IncludeOuterBoxes",
            "lbBoxLinesOn": False,
            "lbBoxSeparatorLinesOn": True,
        },
    )

    save_svg(labelbar_no_box_lines, no_box_lines, width=900, height=500)
    text_no_box_lines = _read(no_box_lines)

    if _count(text_no_box_lines, "<line") != 0:
        raise RuntimeError("lbBoxLinesOn=False should suppress box outline and separators")

    print(f"✅ LabelBar line full-render smoke passed: {out}")
    print("✅ save_svg(...) emits box outline, separators, perim color, and stroke widths")
    print("✅ lbBoxSeparatorLinesOn and lbBoxLinesOn affect final SVG output")


if __name__ == "__main__":
    main()
