from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._render_svg import save_svg


def main():
    out = Path("outputs/smoke/svg_labelbar_title_angle_render.svg")

    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Rotated title",
            "lbTitlePosition": "Top",
            "lbTitleJust": "CenterCenter",
            "lbTitleAngleF": -45,
            "lbTitleFontColor": "black",
            "lbTitleFontHeightF": 0.04,
        },
    )

    geometry = labelbar.compute_geometry()
    assert geometry.title_text_item is not None
    assert geometry.title_text_item.angle == 315.0

    save_svg(labelbar, out, width=900, height=500)

    svg = out.read_text(encoding="utf-8")

    assert "Rotated title" in svg
    assert "rotate(315.000" in svg
    assert 'font-size="20.000"' in svg
    assert 'text-anchor="middle"' in svg

    print("✅ SVG LabelBar title angle render smoke passed")


if __name__ == "__main__":
    main()
