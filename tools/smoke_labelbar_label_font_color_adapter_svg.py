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
            "lbLabelFontColor": "red",
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "~",
        },
    )

    primitives = labelbar_to_svg_primitives(labelbar, 900, 500)

    assert primitives.texts
    assert all(text.fill == "red" for text in primitives.texts)

    explicit = labelbar_to_svg_primitives(
        labelbar,
        900,
        500,
        text_fill="blue",
    )

    assert explicit.texts
    assert all(text.fill == "blue" for text in explicit.texts)

    out = Path("outputs/smoke/svg_labelbar_label_font_color_adapter.svg")
    save_svg(labelbar, out, width=900, height=500)

    svg = out.read_text(encoding="utf-8")

    assert ">A<" in svg
    assert 'fill="red"' in svg

    print("✅ LabelBar label font color adapter/SVG smoke passed")


if __name__ == "__main__":
    main()
