from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_text_semantics(actual, expected):
    assert actual.text == expected.text
    assert actual.direction == expected.direction
    assert actual.real_string == expected.real_string
    assert actual.func_code == expected.func_code
    assert actual.just == expected.just
    assert actual.angle == expected.angle
    assert actual.font == expected.font
    assert actual.font_color == expected.font_color
    almost_equal(actual.font_height, expected.font_height)
    almost_equal(actual.font_aspect, expected.font_aspect)
    almost_equal(actual.font_thickness, expected.font_thickness)
    assert actual.font_quality == expected.font_quality
    assert actual.quality_index == expected.quality_index
    almost_equal(actual.constant_spacing, expected.constant_spacing)


def main():
    title_lb = HluLabelBar(
        name="bridge_title_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Bridge title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleJust": "TopRight",
            "lbTitleAngleF": -45,
            "lbTitleFont": 25,
            "lbTitleFontColor": "red",
            "lbTitleFontHeightF": 0.04,
            "lbTitleFontAspectF": 1.1,
            "lbTitleFontThicknessF": 2.0,
            "lbTitleFontQuality": "Medium",
            "lbTitleConstantSpacingF": 0.2,
            "lbTitleFuncCode": "@",
        },
    )

    title_geom = title_lb.compute_geometry()
    assert title_geom.title_text_item is not None

    expected_title = build_text_item_semantics(
        "Bridge title",
        direction="Across",
        func_code="@",
        just="TopRight",
        angle=-45,
        font=25,
        font_color="red",
        font_height=0.04,
        font_aspect=1.1,
        font_thickness=2.0,
        font_quality="Medium",
        constant_spacing=0.2,
    )

    assert_text_semantics(title_geom.title_text_item, expected_title)

    label_lb = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
            "lbLabelDirection": "Down",
            "lbLabelJust": "BottomLeft",
            "lbLabelAngleF": -30,
            "lbLabelFont": 26,
            "lbLabelFontColor": "blue",
            "lbLabelFontHeightF": 0.03,
            "lbLabelFontAspectF": 1.2,
            "lbLabelFontThicknessF": 1.5,
            "lbLabelFontQuality": "Low",
            "lbLabelConstantSpacingF": 0.1,
            "lbLabelFuncCode": "%",
        },
    )

    primitives = labelbar_to_svg_primitives(label_lb, 900, 500)
    assert primitives.texts

    first_label = primitives.texts[0]
    expected_label = build_text_item_semantics(
        first_label.text,
        direction="Down",
        func_code="%",
        just="BottomLeft",
        angle=-30,
        font=26,
        font_color="blue",
        font_height=0.03,
        font_aspect=1.2,
        font_thickness=1.5,
        font_quality="Low",
        constant_spacing=0.1,
    )

    assert first_label.text == "A"
    assert first_label.direction == expected_label.direction
    assert first_label.real_string == expected_label.real_string
    assert first_label.func_code == expected_label.func_code
    assert first_label.just == expected_label.just
    assert first_label.angle == expected_label.angle
    assert first_label.font == expected_label.font
    assert first_label.fill == expected_label.font_color
    almost_equal(first_label.font_height, expected_label.font_height)
    almost_equal(first_label.font_aspect, expected_label.font_aspect)
    almost_equal(first_label.font_thickness, expected_label.font_thickness)
    assert first_label.font_quality == expected_label.font_quality
    assert first_label.quality_index == expected_label.quality_index
    almost_equal(first_label.constant_spacing, expected_label.constant_spacing)

    print("✅ TextItem semantics bridge to LabelBar smoke passed")


if __name__ == "__main__":
    main()
