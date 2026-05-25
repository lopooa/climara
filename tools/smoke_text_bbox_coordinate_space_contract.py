from climara.graphics._multitext_semantics import build_multitext_semantics
from climara.graphics._text_bbox import (
    TEXT_BBOX_COORD_NDC,
    build_multitext_bbox_request,
    build_multitext_bbox_request_from_semantics,
    build_text_item_bbox_request,
)
from climara.graphics._text_semantics import build_text_item_semantics


def main():
    item = build_text_item_semantics(
        "Demo",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=0,
        font=21,
        font_color="black",
        font_height=0.02,
    )

    request = build_text_item_bbox_request(
        item,
        x=0.2,
        y=0.3,
    )

    assert request.coordinate_space == TEXT_BBOX_COORD_NDC
    assert request.x == 0.2
    assert request.y == 0.3
    assert request.semantics.real_string == "~A~Demo"

    request_lower = build_text_item_bbox_request(
        item,
        x=0.2,
        y=0.3,
        coordinate_space="ndc",
    )

    assert request_lower.coordinate_space == TEXT_BBOX_COORD_NDC

    multi = build_multitext_bbox_request([request, request_lower])

    assert multi.coordinate_space == TEXT_BBOX_COORD_NDC
    assert len(multi.items) == 2

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

    from_semantics = build_multitext_bbox_request_from_semantics(
        semantics,
        [(0.1, 0.2), (0.3, 0.4)],
        coordinate_space="NDC",
    )

    assert from_semantics.coordinate_space == TEXT_BBOX_COORD_NDC
    assert len(from_semantics.items) == 2
    assert from_semantics.items[0].semantics.text == "A"
    assert from_semantics.items[1].semantics.text == "B"

    try:
        build_text_item_bbox_request(
            item,
            x=0.2,
            y=0.3,
            coordinate_space="SVG",
        )
    except ValueError as exc:
        assert "only NDC coordinate space" in str(exc)
    else:
        raise AssertionError("non-NDC TextItem bbox coordinate space must fail")

    try:
        build_multitext_bbox_request_from_semantics(
            semantics,
            [(0.1, 0.2)],
        )
    except ValueError as exc:
        assert "one position for each TextItem semantic item" in str(exc)
    else:
        raise AssertionError("mismatched MultiText positions must fail")

    print("✅ TextItem / MultiText bbox coordinate-space contract smoke passed")


if __name__ == "__main__":
    main()
