from pathlib import Path

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._multitext_semantics import build_multitext_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    adapter = Path("src/climara/graphics/_labelbar_svg_adapter.py").read_text(encoding="utf-8")
    assert "build_multitext_semantics" in adapter

    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
            "lbLabelDirection": "NhlDown",
            "lbLabelJust": "NhlBottomLeft",
            "lbLabelAngleF": -30,
            "lbLabelFont": 26,
            "lbLabelFontColor": "blue",
            "lbLabelFontHeightF": 0.03,
            "lbLabelFontAspectF": 1.2,
            "lbLabelFontThicknessF": 1.5,
            "lbLabelFontQuality": "NhlLow",
            "lbLabelConstantSpacingF": 0.1,
            "lbLabelFuncCode": "%",
        },
    )

    primitives = labelbar_to_svg_primitives(labelbar, 900, 500)
    assert primitives.texts

    expected = build_multitext_semantics(
        [text.text for text in primitives.texts],
        direction="NhlDown",
        func_code="%",
        just="NhlBottomLeft",
        angle=-30,
        font=26,
        font_color="blue",
        font_height=0.03,
        font_aspect=1.2,
        font_thickness=1.5,
        font_quality="NhlLow",
        constant_spacing=0.1,
    )

    assert len(expected.items) == len(primitives.texts)

    for actual, item in zip(primitives.texts, expected.items):
        assert actual.text == item.text
        assert actual.direction == item.direction
        assert actual.real_string == item.real_string
        assert actual.func_code == item.func_code
        assert actual.just == item.just
        assert actual.angle == item.angle
        assert actual.font == item.font
        assert actual.fill == item.font_color
        almost_equal(actual.font_height, item.font_height)
        almost_equal(actual.font_aspect, item.font_aspect)
        almost_equal(actual.font_thickness, item.font_thickness)
        assert actual.font_quality == item.font_quality
        assert actual.quality_index == item.quality_index
        almost_equal(actual.constant_spacing, item.constant_spacing)

    print("✅ LabelBar labels use shared MultiText semantics smoke passed")


if __name__ == "__main__":
    main()
