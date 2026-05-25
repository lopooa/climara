from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_svg_adapter import labelbar_to_svg_primitives
from climara.graphics._text_bbox import (
    TextItemBBoxRequest,
    build_multitext_bbox_request,
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

    title_request = TextItemBBoxRequest(
        semantics=title_geom.title_text_item,
        x=title_geom.title_text_item.x,
        y=title_geom.title_text_item.y,
    )

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

    label_requests = tuple(
        TextItemBBoxRequest(
            semantics=build_text_item_semantics(
                text.text,
                direction=text.direction,
                func_code=text.func_code,
                just=text.just,
                angle=text.angle,
                font=text.font,
                font_color=text.fill,
                font_height=text.font_height,
                font_aspect=text.font_aspect,
                font_thickness=text.font_thickness,
                font_quality=text.font_quality,
                constant_spacing=text.constant_spacing,
            ),
            x=text.x,
            y=text.y,
        )
        for text in primitives.texts
    )

    assert label_requests
    assert label_requests[0].semantics.text == "A"
    assert label_requests[0].semantics.real_string == "%A%A"
    assert label_requests[0].semantics.font_color == "blue"

    multi_request = build_multitext_bbox_request(label_requests)

    assert len(multi_request.items) == len(primitives.texts)
    assert multi_request.items[0].semantics.text == "A"
    assert multi_request.items[0].semantics.real_string == "%A%A"

    print("✅ LabelBar TextItem bbox request contract smoke passed")


if __name__ == "__main__":
    main()
