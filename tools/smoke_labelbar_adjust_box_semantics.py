from math import isfinite

from climara.graphics._labelbar_adjust import (
    adjust_labelbar_geometry_for_text,
)
from climara.graphics._labelbar_adjust_bridge import (
    build_labelbar_adjust_request_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_adjust_semantics import (
    compute_labelbar_adjust_box_semantics,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC


def contains(outer, inner):
    assert outer.l <= inner.l + 1e-12
    assert outer.r >= inner.r - 1e-12
    assert outer.b <= inner.b + 1e-12
    assert outer.t >= inner.t - 1e-12


def assert_finite_bbox(box):
    assert box.coordinate_space == TEXT_BBOX_COORD_NDC
    assert box.width >= 0.0
    assert box.height >= 0.0
    for value in (box.l, box.r, box.b, box.t):
        assert isfinite(value), value


def main():
    labelbar = HluLabelBar(
        name="adjust_box_semantics",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Adjust title",
            "lbTitlePosition": "Top",
            "lbTitleDirection": "Across",
            "lbTitleJust": "CenterCenter",
            "lbTitleAngleF": 0,
            "lbTitleFuncCode": "@",
            "lbTitleFontHeightF": 0.04,
            "lbLabelDirection": "Across",
            "lbLabelJust": "CenterCenter",
            "lbLabelAngleF": 0,
            "lbLabelFuncCode": "%",
            "lbLabelFontHeightF": 0.03,
        },
    )

    requests = build_labelbar_text_bbox_requests(labelbar)
    assert requests.title is not None
    assert requests.labels.items

    title_metrics = PlotcharExtentMetrics(
        dl=0.12,
        dr=0.18,
        db=0.03,
        dt=0.07,
    )

    label_metrics = tuple(
        PlotcharExtentMetrics(
            dl=0.02,
            dr=0.02,
            db=0.01,
            dt=0.02,
        )
        for _ in requests.labels.items
    )

    bundle = build_labelbar_adjust_request_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    semantics = compute_labelbar_adjust_box_semantics(bundle.adjust_request)

    assert_finite_bbox(semantics.labelbar_bbox)
    assert_finite_bbox(semantics.bar_and_labels_bbox)
    assert_finite_bbox(semantics.adjusted_bar_bbox)

    contains(semantics.labelbar_bbox, semantics.adjusted_bar_bbox)
    contains(semantics.labelbar_bbox, semantics.bar_and_labels_bbox)

    assert semantics.adjusted_label_bbox is not None
    assert_finite_bbox(semantics.adjusted_label_bbox)
    contains(semantics.labelbar_bbox, semantics.adjusted_label_bbox)

    assert semantics.adjusted_title_bbox is not None
    assert_finite_bbox(semantics.adjusted_title_bbox)
    contains(semantics.labelbar_bbox, semantics.adjusted_title_bbox)

    assert semantics.title_x is not None
    assert semantics.title_y is not None
    assert isfinite(semantics.label_pos_offset)
    assert isfinite(semantics.center_offset)

    adjust_result = adjust_labelbar_geometry_for_text(bundle.adjust_request)
    assert adjust_result.final_view_bbox.width >= 0.0
    assert adjust_result.final_view_bbox.height >= 0.0
    print("✅ LabelBar AdjustGeometry supplied-bbox box semantics smoke passed")


if __name__ == "__main__":
    main()
