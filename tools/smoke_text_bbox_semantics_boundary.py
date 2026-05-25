from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import (
    TextBBoxNotImplementedError,
    build_text_item_bbox_request,
    compute_text_item_bbox,
    has_text_bbox_engine,
)
from climara.graphics._text_bbox_semantics import compute_text_bbox_from_plotchar_metrics
from climara.graphics._text_semantics import build_text_item_semantics


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    semantics = build_text_item_semantics(
        "Boundary",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=0,
        font=21,
        font_color="black",
        font_height=0.02,
    )

    request = build_text_item_bbox_request(
        semantics,
        x=0.5,
        y=0.5,
    )

    metrics = PlotcharExtentMetrics(
        dl=0.1,
        dr=0.3,
        db=0.05,
        dt=0.15,
    )

    supplied_metrics_result = compute_text_bbox_from_plotchar_metrics(
        request,
        metrics,
    )

    almost_equal(supplied_metrics_result.bbox.l, 0.3)
    almost_equal(supplied_metrics_result.bbox.r, 0.7)
    almost_equal(supplied_metrics_result.bbox.b, 0.4)
    almost_equal(supplied_metrics_result.bbox.t, 0.6)

    assert has_text_bbox_engine() is False

    try:
        compute_text_item_bbox(request)
    except TextBBoxNotImplementedError as exc:
        message = str(exc)
        assert "NCL TextItem bbox computation is not implemented" in message
        assert "do not replace this with heuristic visual extents" in message
    else:
        raise AssertionError(
            "TextItem bbox engine must remain guarded even though supplied-metrics semantics exist"
        )

    print("✅ TextBBox supplied-metrics semantics boundary smoke passed")


if __name__ == "__main__":
    main()
