from math import isfinite

from climara.graphics._labelbar_adjust_bridge import (
    build_labelbar_adjust_request_from_supplied_plotchar_metrics,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import TEXT_BBOX_COORD_NDC


def make_labelbar(name="adjust_smoke_labelbar"):
    return HluLabelBar(
        name=name,
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
            "lbJustification": "CenterCenter",
        },
    )


def make_supplied_metrics_bundle(labelbar=None):
    if labelbar is None:
        labelbar = make_labelbar()

    requests = build_labelbar_text_bbox_requests(labelbar)
    assert requests.title is not None
    assert requests.labels.items

    title_metrics = PlotcharExtentMetrics(dl=0.12, dr=0.18, db=0.03, dt=0.07)
    label_metrics = tuple(
        PlotcharExtentMetrics(dl=0.02, dr=0.02, db=0.01, dt=0.02)
        for _ in requests.labels.items
    )

    return build_labelbar_adjust_request_from_supplied_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )


def assert_finite_bbox(box):
    assert box.coordinate_space == TEXT_BBOX_COORD_NDC
    assert box.width >= 0.0
    assert box.height >= 0.0
    for value in (box.l, box.r, box.b, box.t):
        assert isfinite(value), value


def contains(outer, inner):
    assert outer.l <= inner.l + 1e-12
    assert outer.r >= inner.r - 1e-12
    assert outer.b <= inner.b + 1e-12
    assert outer.t >= inner.t - 1e-12


def assert_adjust_result(result):
    assert result.final_view_bbox.width >= 0.0
    assert result.final_view_bbox.height >= 0.0
    assert_finite_bbox(result.final_view_bbox)
    assert_finite_bbox(result.final_adjusted_bar_bbox)
    contains(result.final_view_bbox, result.final_adjusted_bar_bbox)

    if result.final_adjusted_label_bbox is not None:
        assert_finite_bbox(result.final_adjusted_label_bbox)
        contains(result.final_view_bbox, result.final_adjusted_label_bbox)

    if result.final_adjusted_title_bbox is not None:
        assert_finite_bbox(result.final_adjusted_title_bbox)
        contains(result.final_view_bbox, result.final_adjusted_title_bbox)

    for value in (result.x_offset, result.y_offset, result.major_offset, result.minor_offset):
        assert isfinite(value), value
