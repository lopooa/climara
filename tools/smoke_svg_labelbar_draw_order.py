from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import save_svg


def main():
    out = Path("outputs/smoke/svg_labelbar_draw_order.svg")

    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Top",
            "lbTitleJust": "CenterCenter",
            "lbLabelsOn": True,
            "lbBoxLinesOn": True,
            "lbBoxSeparatorLinesOn": False,
        },
    )

    save_svg(labelbar, out, width=900, height=500)

    svg = out.read_text(encoding="utf-8")

    polygon_pos = svg.index("<polygon")
    title_pos = svg.index("Demo title")
    label_pos = svg.index(">A<")
    line_pos = svg.index("<line")

    assert polygon_pos < title_pos
    assert title_pos < label_pos
    assert label_pos < line_pos

    print("✅ SVG LabelBar draw order smoke passed")


if __name__ == "__main__":
    main()
