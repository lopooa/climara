from climara.graphics._multitext_bbox_semantics import (
    compute_multitext_bbox_from_plotchar_metrics,
)
from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._plotchar_metrics import PlotcharExtentMetrics
from climara.graphics._text_bbox import (
    TEXT_BBOX_COORD_NDC,
    TextBBoxNotImplementedError,
    build_multitext_bbox_request_from_semantics,
    compute_multitext_bbox,
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

    result = compute_multitext_bbox_from_plotchar_metrics(
        request,
        metrics,
    )

    assert result.bbox.coordinate_space == TEXT_BBOX_COORD_NDC
    assert len(result.child_text_bboxes) == 2

    almost_equal(result.child_text_bboxes[0].bbox.l, 0.25)
    almost_equal(result.child_text_bboxes[0].bbox.r, 0.35)
    almost_equal(result.child_text_bboxes[0].bbox.b, 0.475)
    almost_equal(result.child_text_bboxes[0].bbox.t, 0.525)

    almost_equal(result.child_text_bboxes[1].bbox.l, 0.65)
    almost_equal(result.child_text_bboxes[1].bbox.r, 0.75)
    almost_equal(result.child_text_bboxes[1].bbox.b, 0.475)
    almost_equal(result.child_text_bboxes[1].bbox.t, 0.525)

    almost_equal(result.bbox.l, 0.25)
    almost_equal(result.bbox.r, 0.75)
    almost_equal(result.bbox.b, 0.475)
    almost_equal(result.bbox.t, 0.525)
    almost_equal(result.bbox.width, 0.5)
    almost_equal(result.bbox.height, 0.05)

    try:
        compute_multitext_bbox_from_plotchar_metrics(
            request,
            metrics[:1],
        )
    except ValueError as exc:
        assert "one metrics object for each TextItem request" in str(exc)
    else:
        raise AssertionError("mismatched MultiText supplied metrics should fail")

    empty = build_multitext_bbox_request_from_semantics(
        build_multitext_semantics([]),
        [],
    )

    try:
        compute_multitext_bbox_from_plotchar_metrics(
            empty,
            [],
        )
    except ValueError as exc:
        assert "cannot be empty" in str(exc)
    else:
        raise AssertionError("empty MultiText supplied metrics should fail")

    try:
        compute_multitext_bbox(request)
    except TextBBoxNotImplementedError as exc:
        message = str(exc)
        assert "NCL MultiText bbox computation is not implemented" in message
        assert "do not replace this with heuristic visual extents" in message
    else:
        raise AssertionError(
            "live MultiText bbox engine must remain guarded even though supplied-metrics semantics exist"
        )

    print("✅ MultiText bbox semantics from supplied Plotchar metrics smoke passed")


if __name__ == "__main__":
    main()
