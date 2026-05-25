from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
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

    actual = primitives.texts[0]

    expected = build_text_item_semantics(
        "A",
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

    assert actual.text == expected.text
    assert actual.direction == expected.direction
    assert actual.real_string == expected.real_string
    assert actual.func_code == expected.func_code
    assert actual.just == expected.just
    assert actual.angle == expected.angle
    assert actual.font == expected.font
    assert actual.fill == expected.font_color
    almost_equal(actual.font_height, expected.font_height)
    almost_equal(actual.font_aspect, expected.font_aspect)
    almost_equal(actual.font_thickness, expected.font_thickness)
    assert actual.font_quality == expected.font_quality
    assert actual.quality_index == expected.quality_index
    almost_equal(actual.constant_spacing, expected.constant_spacing)

    print("✅ LabelBar labels use shared TextItem semantics smoke passed")


if __name__ == "__main__":
    main()
