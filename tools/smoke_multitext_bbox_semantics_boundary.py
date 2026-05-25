from climara.graphics._multitext_bbox_semantics import (
    compute_multitext_bbox_from_plotchar_metrics,
)
from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import (
    TextBBoxNotImplementedError,
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
        [
            (0.3, 0.5),
            (0.7, 0.5),
        ],
    )

    metrics = (
        PlotcharExtentMetrics(dl=0.05, dr=0.05, db=0.02, dt=0.03),
        PlotcharExtentMetrics(dl=0.05, dr=0.05, db=0.02, dt=0.03),
    )

    supplied_metrics_result = compute_multitext_bbox_from_plotchar_metrics(
        request,
        metrics,
    )

    almost_equal(supplied_metrics_result.bbox.l, 0.25)
    almost_equal(supplied_metrics_result.bbox.r, 0.75)
    almost_equal(supplied_metrics_result.bbox.b, 0.475)
    almost_equal(supplied_metrics_result.bbox.t, 0.525)

    assert has_text_bbox_engine() is False

    try:
        compute_multitext_bbox(request)
    except TextBBoxNotImplementedError as exc:
        message = str(exc)
        assert "NCL MultiText bbox computation is not implemented" in message
        assert "do not replace this with heuristic visual extents" in message
    else:
        raise AssertionError(
            "MultiText bbox engine must remain guarded even though supplied-metrics semantics exist"
        )

    print("✅ MultiText supplied-metrics semantics boundary smoke passed")


if __name__ == "__main__":
    main()
