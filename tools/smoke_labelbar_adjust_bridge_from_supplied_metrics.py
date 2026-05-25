from climara.graphics._labelbar_adjust import (
    adjust_labelbar_geometry_for_text,
    has_labelbar_adjust_geometry_engine,
)
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC

from _smoke_labelbar_adjust_helpers import (
    assert_adjust_result,
    make_labelbar,
    make_supplied_metrics_bundle,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = make_labelbar("adjust_bridge_labelbar")
    bundle = make_supplied_metrics_bundle(labelbar)

    assert bundle.text_bboxes.title is not None
    assert bundle.text_bboxes.labels is not None
    assert bundle.adjust_request.geometry == labelbar.compute_geometry()
    assert bundle.adjust_request.title_bbox is bundle.text_bboxes.title.bbox
    assert bundle.adjust_request.label_bbox is bundle.text_bboxes.labels.bbox
    assert bundle.adjust_request.title_bbox.coordinate_space == TEXT_BBOX_COORD_NDC
    assert bundle.adjust_request.label_bbox.coordinate_space == TEXT_BBOX_COORD_NDC

    almost_equal(bundle.adjust_request.title_bbox.width, 0.30)
    almost_equal(bundle.adjust_request.title_bbox.height, 0.10)

    assert has_labelbar_adjust_geometry_engine() is False

    result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert_adjust_result(result)

    print("✅ LabelBar supplied-metrics AdjustGeometry request bridge smoke passed")


if __name__ == "__main__":
    main()
