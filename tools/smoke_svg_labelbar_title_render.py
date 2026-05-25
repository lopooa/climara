from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import save_svg


def main():
    out = Path("outputs/smoke/svg_labelbar_title_render.svg")

    labelbar = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Top",
            "lbTitleJust": "CenterCenter",
            "lbTitleFontColor": "black",
            "lbTitleFontHeightF": 0.04,
            "lbLabelsOn": True,
            "labels": ["A", "B", "C", "D"],
            "colors": ["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        },
    )

    save_svg(labelbar, out, width=900, height=500)

    svg = out.read_text(encoding="utf-8")

    assert "Demo title" in svg
    assert 'font-size="20.000"' in svg
    assert 'text-anchor="middle"' in svg

    title_pos = svg.index("Demo title")
    first_text_pos = svg.index("<text")
    assert first_text_pos <= title_pos

    print("✅ SVG LabelBar title render smoke passed")


if __name__ == "__main__":
    main()
