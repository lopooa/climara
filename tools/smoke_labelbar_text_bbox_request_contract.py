from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._text_bbox import (
    TEXT_BBOX_COORD_NDC,
    build_multitext_bbox_request_from_semantics,
    build_text_item_bbox_request,
)
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_semantics_equal(actual, expected):
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
        name="bbox_request_labelbar",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "BBox title",
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
        "BBox title",
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

    title_request = build_text_item_bbox_request(
        title_geom.title_text_item,
        x=title_geom.title_text_item.x,
        y=title_geom.title_text_item.y,
    )

    assert title_request.coordinate_space == TEXT_BBOX_COORD_NDC
    assert_semantics_equal(title_request.semantics, expected_title)
    almost_equal(title_request.x, title_geom.title_text_item.x)
    almost_equal(title_request.y, title_geom.title_text_item.y)

    label_lb = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
            "lbLabelDirection": "Across",
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

    label_multitext = build_multitext_semantics(
        [text.text for text in primitives.texts],
        direction="Across",
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

    label_positions = tuple((text.x, text.y) for text in primitives.texts)

    multi_request = build_multitext_bbox_request_from_semantics(
        label_multitext,
        label_positions,
    )

    assert multi_request.coordinate_space == TEXT_BBOX_COORD_NDC
    assert len(multi_request.items) == len(primitives.texts)
    assert multi_request.items[0].coordinate_space == TEXT_BBOX_COORD_NDC
    assert multi_request.items[0].semantics.text == "A"
    assert multi_request.items[0].semantics.real_string == "%A%A"
    assert multi_request.items[0].semantics.font_color == "blue"
    almost_equal(multi_request.items[0].x, primitives.texts[0].x)
    almost_equal(multi_request.items[0].y, primitives.texts[0].y)

    for request, primitive in zip(multi_request.items, primitives.texts):
        assert request.coordinate_space == TEXT_BBOX_COORD_NDC
        assert request.semantics.text == primitive.text
        assert request.semantics.real_string == primitive.real_string
        assert request.semantics.direction == primitive.direction
        assert request.semantics.func_code == primitive.func_code
        assert request.semantics.font_color == primitive.fill
        almost_equal(request.x, primitive.x)
        almost_equal(request.y, primitive.y)

    print("✅ LabelBar TextItem bbox request contract smoke passed")


if __name__ == "__main__":
    main()
