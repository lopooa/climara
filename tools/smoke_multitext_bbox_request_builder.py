from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._text_bbox import (
    build_multitext_bbox_request_from_semantics,
    build_text_item_bbox_request,
    compute_multitext_bbox,
    compute_text_item_bbox,
    TextBBoxNotImplementedError,
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

    positions = (
        (0.2, 0.3),
        (0.4, 0.3),
        (0.6, 0.3),
    )

    request = build_multitext_bbox_request_from_semantics(
        semantics,
        positions,
    )

    assert len(request.items) == 3

    for index, item in enumerate(request.items):
        assert item.semantics.text == semantics.items[index].text
        assert item.semantics.real_string == semantics.items[index].real_string
        almost_equal(item.x, positions[index][0])
        almost_equal(item.y, positions[index][1])

    single = build_text_item_bbox_request(
        semantics.items[0],
        x=0.2,
        y=0.3,
    )

    assert single.semantics.text == "A"
    almost_equal(single.x, 0.2)
    almost_equal(single.y, 0.3)

    try:
        build_multitext_bbox_request_from_semantics(
            semantics,
            [(0.1, 0.2)],
        )
    except ValueError as exc:
        assert "one position for each TextItem semantic item" in str(exc)
    else:
        raise AssertionError("mismatched MultiText bbox positions should fail")

    try:
        compute_text_item_bbox(single)
    except TextBBoxNotImplementedError:
        pass
    else:
        raise AssertionError("TextItem bbox must remain guarded")

    try:
        compute_multitext_bbox(request)
    except TextBBoxNotImplementedError:
        pass
    else:
        raise AssertionError("MultiText bbox must remain guarded")

    print("✅ MultiText bbox request builder smoke passed")


if __name__ == "__main__":
    main()
