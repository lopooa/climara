from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._render_svg import save_svg


def main():
    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
            "lbLabelAngleF": -45,
            "lbLabelFontColor": "red",
            "lbLabelFontHeightF": 0.04,
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
        },
    )

    primitives = labelbar_to_svg_primitives(
        labelbar,
        900,
        500,
        text_fill="red",
    )

    assert primitives.texts
    assert all(text.angle == 315.0 for text in primitives.texts)
    assert all(text.fill == "red" for text in primitives.texts)
    assert all(text.font_height == 0.04 for text in primitives.texts)

    out = Path("outputs/smoke/svg_labelbar_label_angle_color_render.svg")
    save_svg(labelbar, out, width=900, height=500)

    svg = out.read_text(encoding="utf-8")

    assert ">A<" in svg
    assert "rotate(315.000" in svg
    assert 'fill="red"' in svg
    assert 'font-size="20.000"' in svg

    print("✅ SVG LabelBar label angle/color render smoke passed")


if __name__ == "__main__":
    main()
