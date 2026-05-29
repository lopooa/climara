from climara.graphics._labelbar_adjust import (
    adjust_labelbar_geometry_for_text,
    build_labelbar_adjust_geometry_request,
    has_labelbar_adjust_geometry_engine,
)
from climara.graphics._labelbar_bbox_semantics import (
    compute_labelbar_text_bbox_from_plotchar_metrics,
)
from climara.graphics._labelbar_text_bbox import build_labelbar_text_bbox_requests
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import (
    compute_multitext_bbox,
    compute_text_item_bbox,
    has_text_bbox_engine,
)

from _smoke_labelbar_adjust_helpers import assert_adjust_result, make_labelbar


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    labelbar = make_labelbar("labelbar_bbox_boundary")
    requests = build_labelbar_text_bbox_requests(labelbar)

    title_metrics = PlotcharExtentMetrics(dl=0.12, dr=0.18, db=0.03, dt=0.07)
    label_metrics = tuple(
        PlotcharExtentMetrics(dl=0.02, dr=0.02, db=0.01, dt=0.02)
        for _ in requests.labels.items
    )

    supplied = compute_labelbar_text_bbox_from_plotchar_metrics(
        labelbar,
        title_metrics=title_metrics,
        label_metrics=label_metrics,
    )

    assert supplied.title is not None
    assert supplied.labels is not None
    almost_equal(supplied.title.bbox.width, 0.30)
    almost_equal(supplied.title.bbox.height, 0.10)

    assert has_text_bbox_engine() is True
    assert has_labelbar_adjust_geometry_engine() is False

    live_title = compute_text_item_bbox(requests.title)
    live_labels = compute_multitext_bbox(requests.labels)
    assert live_title.width > 0.0
    assert live_labels.width > 0.0

    request = build_labelbar_adjust_geometry_request(
        labelbar.compute_geometry(),
        title_bbox=supplied.title.bbox,
        label_bbox=supplied.labels.bbox,
    )

    result = adjust_labelbar_geometry_for_text(request)
    assert_adjust_result(result)

    print("✅ LabelBar supplied-metrics bbox and Python mainline boundary smoke passed")


if __name__ == "__main__":
    main()
