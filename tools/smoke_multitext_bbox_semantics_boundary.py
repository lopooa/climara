from climara.graphics._multitext_bbox_semantics import (
    compute_multitext_bbox_from_plotchar_metrics,
)
from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import (
    build_multitext_bbox_request_from_semantics,
    compute_multitext_bbox,
    has_text_bbox_engine,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    semantics = build_multitext_semantics(
        ["A", "B"],
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=0,
        font=21,
        font_color="black",
        font_height=0.02,
    )

    request = build_multitext_bbox_request_from_semantics(
        semantics,
        [(0.3, 0.5), (0.7, 0.5)],
    )

    metrics = (
        PlotcharExtentMetrics(dl=0.05, dr=0.05, db=0.02, dt=0.03),
        PlotcharExtentMetrics(dl=0.05, dr=0.05, db=0.02, dt=0.03),
    )

    supplied_metrics_result = compute_multitext_bbox_from_plotchar_metrics(request, metrics)
    almost_equal(supplied_metrics_result.bbox.l, 0.25)
    almost_equal(supplied_metrics_result.bbox.r, 0.75)
    almost_equal(supplied_metrics_result.bbox.b, 0.475)
    almost_equal(supplied_metrics_result.bbox.t, 0.525)

    assert has_text_bbox_engine() is True
    live_bbox = compute_multitext_bbox(request)
    assert live_bbox.l < live_bbox.r
    assert live_bbox.b < live_bbox.t

    print("✅ MultiText supplied-metrics and Python mainline boundary smoke passed")


if __name__ == "__main__":
    main()
