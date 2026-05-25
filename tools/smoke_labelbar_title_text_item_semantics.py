from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_semantics import TITLE_DIRECTION_ACROSS, TITLE_DIRECTION_DOWN


def almost_equal(value, expected, tol=1e-9):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    off_geom = HluLabelBar().compute_geometry()
    assert off_geom.title_text_item is None

    default_title = HluLabelBar(
        name="my_labelbar",
        resources={
            "lbTitleOn": True,
        },
    ).compute_geometry()

    item = default_title.title_text_item
    assert item is not None
    assert item.text == "my_labelbar"
    assert item.direction == TITLE_DIRECTION_ACROSS
    assert item.just == "CenterCenter"
    assert item.angle == 0.0
    assert item.font == 21
    assert item.font_color == "Foreground"
    almost_equal(item.font_height, 0.025)
    almost_equal(item.font_aspect, 1.3125)
    almost_equal(item.font_thickness, 1.0)
    assert item.font_quality == "High"
    almost_equal(item.constant_spacing, 0.0)
    assert item.func_code == "~"

    custom_title = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitlePosition": "Left",
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
    ).compute_geometry()

    item = custom_title.title_text_item
    assert item is not None
    assert item.text == "Demo title"
    assert item.direction == TITLE_DIRECTION_DOWN
    assert item.just == "TopRight"
    assert item.angle == 315.0
    assert item.font == 25
    assert item.font_color == "red"
    almost_equal(item.font_height, 0.04)
    almost_equal(item.font_aspect, 1.1)
    almost_equal(item.font_thickness, 2.0)
    assert item.font_quality == "Medium"
    almost_equal(item.constant_spacing, 0.2)
    assert item.func_code == "@"

    negative_spacing = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitleConstantSpacingF": -1.0,
        },
    ).compute_geometry()

    assert negative_spacing.title_text_item is not None
    almost_equal(negative_spacing.title_text_item.constant_spacing, 0.0)

    non_positive_height = HluLabelBar(
        resources={
            "lbTitleString": "Demo title",
            "lbTitleFontHeightF": 0.0,
        },
    ).compute_geometry()

    assert non_positive_height.title_text_item is not None
    almost_equal(non_positive_height.title_text_item.font_height, 0.025)

    print("✅ LabelBar title TextItem semantics smoke passed")


if __name__ == "__main__":
    main()
