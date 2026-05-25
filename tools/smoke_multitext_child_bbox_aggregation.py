from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._text_bbox import (
    TEXT_BBOX_COORD_NDC,
    aggregate_multitext_child_bboxes,
    build_multitext_bbox_request_from_semantics,
    build_text_bbox,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    semantics = build_multitext_semantics(
        ["A", "B", "C"],
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
            (0.2, 0.3),
            (0.4, 0.3),
            (0.6, 0.3),
        ],
    )

    child_bboxes = [
        build_text_bbox(l=0.18, r=0.22, b=0.28, t=0.33),
        build_text_bbox(l=0.37, r=0.43, b=0.27, t=0.34),
        build_text_bbox(l=0.55, r=0.65, b=0.26, t=0.35),
    ]

    aggregate = aggregate_multitext_child_bboxes(
        request,
        child_bboxes,
    )

    assert aggregate.coordinate_space == TEXT_BBOX_COORD_NDC
    almost_equal(aggregate.l, 0.18)
    almost_equal(aggregate.r, 0.65)
    almost_equal(aggregate.b, 0.26)
    almost_equal(aggregate.t, 0.35)
    almost_equal(aggregate.width, 0.47)
    almost_equal(aggregate.height, 0.09)

    try:
        aggregate_multitext_child_bboxes(
            request,
            child_bboxes[:1],
        )
    except ValueError as exc:
        assert "one child bbox for each TextItem request" in str(exc)
    else:
        raise AssertionError("mismatched child bbox count should fail")

    empty_request = build_multitext_bbox_request_from_semantics(
        build_multitext_semantics([]),
        [],
    )

    try:
        aggregate_multitext_child_bboxes(
            empty_request,
            [],
        )
    except ValueError as exc:
        assert "empty child bbox sequence" in str(exc)
    else:
        raise AssertionError("empty child bbox aggregation should fail")

    print("✅ MultiText child bbox aggregation contract smoke passed")


if __name__ == "__main__":
    main()
