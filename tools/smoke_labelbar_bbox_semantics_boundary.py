from climara.graphics._labelbar_adjust import (
    adjust_labelbar_geometry_for_text,
    build_labelbar_adjust_geometry_request,
    has_labelbar_adjust_geometry_engine,
)
from climara.graphics._labelbar_bbox_semantics import (
    compute_labelbar_text_bbox_from_plotchar_metrics,
)
from climara.graphics._labelbar_object import HluLabelBar
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import (
    TextBBoxNotImplementedError,
    compute_multitext_bbox,
    compute_text_item_bbox,
    has_text_bbox_engine,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = HluLabelBar(
        name="labelbar_bbox_boundary",
        colors=["#2166ac", "#67a9cf", "#fddbc7", "#b2182b"],
        labels=["A", "B", "C", "D"],
        resources={
            "lbTitleString": "Boundary title",
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
    assert len(requests.labels.items) > 0

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

    supplied_metrics_result = compute_labelbar_text_bbox_from_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert supplied_metrics_result.title is not None
    assert supplied_metrics_result.labels is not None

    almost_equal(supplied_metrics_result.title.bbox.width, 0.30)
    almost_equal(supplied_metrics_result.title.bbox.height, 0.10)

    assert len(supplied_metrics_result.labels.child_text_bboxes) == len(requests.labels.items)

    assert has_text_bbox_engine() is False
    assert has_labelbar_adjust_geometry_engine() is False

    try:
        compute_text_item_bbox(requests.title)
    except TextBBoxNotImplementedError as exc:
        assert "NCL TextItem bbox computation is not implemented" in str(exc)
    else:
        raise AssertionError(
            "live TextItem bbox engine must remain guarded even though LabelBar supplied-metrics semantics exist"
        )

    try:
        compute_multitext_bbox(requests.labels)
    except TextBBoxNotImplementedError as exc:
        assert "NCL MultiText bbox computation is not implemented" in str(exc)
    else:
        raise AssertionError(
            "live MultiText bbox engine must remain guarded even though LabelBar supplied-metrics semantics exist"
        )

    adjust_request = build_labelbar_adjust_geometry_request(
        labelbar.compute_geometry(),
        title_bbox=supplied_metrics_result.title.bbox,
        label_bbox=supplied_metrics_result.labels.bbox,
    )

    adjust_result = adjust_labelbar_geometry_for_text(adjust_request)
    assert adjust_result.final_view_bbox.width >= 0.0
    assert adjust_result.final_view_bbox.height >= 0.0
    print("✅ LabelBar supplied-metrics bbox semantics boundary smoke passed")


if __name__ == "__main__":
    main()
