from climara.graphics._text_bbox import (
    TEXT_BBOX_COORD_NDC,
    build_text_bbox,
    union_text_bboxes,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    first = build_text_bbox(
        l=0.2,
        r=0.4,
        b=0.3,
        t=0.5,
    )

    second = build_text_bbox(
        l=0.1,
        r=0.6,
        b=0.25,
        t=0.55,
        coordinate_space="ndc",
    )

    assert first.coordinate_space == TEXT_BBOX_COORD_NDC
    assert second.coordinate_space == TEXT_BBOX_COORD_NDC
    almost_equal(first.width, 0.2)
    almost_equal(first.height, 0.2)

    union = union_text_bboxes([first, second])

    assert union.coordinate_space == TEXT_BBOX_COORD_NDC
    almost_equal(union.l, 0.1)
    almost_equal(union.r, 0.6)
    almost_equal(union.b, 0.25)
    almost_equal(union.t, 0.55)
    almost_equal(union.width, 0.5)
    almost_equal(union.height, 0.3)

    try:
        build_text_bbox(l=0.4, r=0.2, b=0.3, t=0.5)
    except ValueError as exc:
        assert "r >= l" in str(exc)
    else:
        raise AssertionError("invalid horizontal bbox extents should fail")

    try:
        build_text_bbox(l=0.2, r=0.4, b=0.5, t=0.3)
    except ValueError as exc:
        assert "t >= b" in str(exc)
    else:
        raise AssertionError("invalid vertical bbox extents should fail")

    try:
        build_text_bbox(l=0.2, r=0.4, b=0.3, t=0.5, coordinate_space="SVG")
    except ValueError as exc:
        assert "only NDC coordinate space" in str(exc)
    else:
        raise AssertionError("non-NDC TextBBox coordinate space should fail")

    try:
        union_text_bboxes([])
    except ValueError as exc:
        assert "empty TextBBox sequence" in str(exc)
    else:
        raise AssertionError("empty TextBBox union should fail")

    print("✅ TextBBox union contract smoke passed")


if __name__ == "__main__":
    main()
