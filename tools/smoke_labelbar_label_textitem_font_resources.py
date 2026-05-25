from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives


def almost_equal(value, expected, tol=1e-9):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
            "lbLabelJust": "TopRight",
            "lbLabelFont": 25,
            "lbLabelFontHeightF": 0.04,
            "lbLabelFontAspectF": 1.1,
            "lbLabelFontThicknessF": 2.0,
            "lbLabelFontQuality": "Medium",
            "lbLabelConstantSpacingF": 0.2,
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "@",
        },
    )

    primitives = labelbar_to_svg_primitives(labelbar, 900, 500)

    assert primitives.texts
    for text in primitives.texts:
        assert text.just == "TopRight"
        assert text.font == 25
        almost_equal(text.font_height, 0.04)
        almost_equal(text.font_aspect, 1.1)
        almost_equal(text.font_thickness, 2.0)
        assert text.font_quality == "Medium"
        assert text.quality_index == 1
        almost_equal(text.constant_spacing, 0.2)
        assert text.direction == "Across"
        assert text.func_code == "@"
        assert text.real_string == f"@A@{text.text}"

    default_labelbar = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
        },
    )

    primitives = labelbar_to_svg_primitives(default_labelbar, 900, 500)

    assert primitives.texts
    for text in primitives.texts:
        assert text.just == "CenterCenter"
        assert text.font == 21
        almost_equal(text.font_height, 0.02)
        almost_equal(text.font_aspect, 1.3125)
        almost_equal(text.font_thickness, 1.0)
        assert text.font_quality == "High"
        assert text.quality_index == 0
        almost_equal(text.constant_spacing, 0.0)

    low_quality = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
            "lbLabelFontQuality": "NhlLow",
            "lbLabelConstantSpacingF": -1.0,
        },
    )

    primitives = labelbar_to_svg_primitives(low_quality, 900, 500)

    assert primitives.texts
    assert primitives.texts[0].quality_index == 2
    almost_equal(primitives.texts[0].constant_spacing, 0.0)

    print("✅ LabelBar label TextItem font resources smoke passed")


if __name__ == "__main__":
    main()
