from math import isfinite

from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def assert_ndc_value(value):
    assert isinstance(value, float), type(value)
    assert isfinite(value), value
    assert abs(value) < 10.0, value


def main():
    title_lb = HluLabelBar(
        name="bbox_request_builder_labelbar",
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
            "lbLabelDirection": "Across",
            "lbLabelFuncCode": "%",
        },
    )

    geometry = title_lb.compute_geometry()
    requests = build_labelbar_text_bbox_requests(title_lb)

    assert requests.title is not None
    assert requests.title.coordinate_space == TEXT_BBOX_COORD_NDC
    assert requests.title.semantics.text == "BBox title"
    assert requests.title.semantics.real_string == "@A@BBox title"
    assert requests.title.semantics.just == "TopRight"
    assert requests.title.semantics.angle == 315.0
    assert requests.title.semantics.font == 25
    assert requests.title.semantics.font_color == "red"
    almost_equal(requests.title.semantics.font_height, 0.04)

    almost_equal(requests.title.x, geometry.title_text_item.x)
    almost_equal(requests.title.y, geometry.title_text_item.y)
    assert_ndc_value(requests.title.x)
    assert_ndc_value(requests.title.y)

    assert requests.labels.coordinate_space == TEXT_BBOX_COORD_NDC
    assert len(requests.labels.items) == len(geometry.label_text_positions)
    assert requests.labels.items[0].semantics.text == "A"
    assert requests.labels.items[0].semantics.real_string == "%A%A"

    for request, position in zip(requests.labels.items, geometry.label_text_positions):
        assert request.coordinate_space == TEXT_BBOX_COORD_NDC
        almost_equal(request.x, position.x)
        almost_equal(request.y, position.y)
        assert_ndc_value(request.x)
        assert_ndc_value(request.y)

    no_title = HluLabelBar(
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleOn": False,
        },
    )

    no_title_requests = build_labelbar_text_bbox_requests(no_title)

    assert no_title_requests.title is None
    assert len(no_title_requests.labels.items) > 0

    print("✅ LabelBar TextBBox request builder smoke passed")


if __name__ == "__main__":
    main()
