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
            "lbLabelFontHeightF": 0.04,
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
        },
    )

    primitives = labelbar_to_svg_primitives(labelbar, 900, 500)

    assert primitives.texts
    assert all(text.font_height == 0.04 for text in primitives.texts)

    out = Path("outputs/smoke/svg_labelbar_label_font_height.svg")
    save_svg(labelbar, out, width=900, height=500)

    svg = out.read_text(encoding="utf-8")

    assert ">A<" in svg
    assert 'font-size="20.000"' in svg

    default_labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
        },
    )

    primitives = labelbar_to_svg_primitives(default_labelbar, 900, 500)

    assert primitives.texts
    assert all(text.font_height == 0.02 for text in primitives.texts)

    print("✅ LabelBar label font height SVG smoke passed")


if __name__ == "__main__":
    main()
