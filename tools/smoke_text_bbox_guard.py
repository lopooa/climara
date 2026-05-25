from climara.graphics._text_bbox import (
    TextBBoxNotImplementedError,
    TextItemBBoxRequest,
    build_multitext_bbox_request,
    compute_multitext_bbox,
    compute_text_item_bbox,
    has_text_bbox_engine,
)
from climara.graphics._text_semantics import build_text_item_semantics


def main():
    semantics = build_text_item_semantics(
        "Demo",
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=0,
        font=21,
        font_color="black",
        font_height=0.025,
    )

    request = TextItemBBoxRequest(
        semantics=semantics,
        x=0.5,
        y=0.5,
    )

    assert has_text_bbox_engine() is False

    try:
        compute_text_item_bbox(request)
    except TextBBoxNotImplementedError as exc:
        message = str(exc)
        assert "NCL TextItem bbox computation is not implemented" in message
        assert "do not replace this with heuristic visual extents" in message
    else:
        raise AssertionError("TextItem bbox must remain guarded until NCL semantics are implemented")

    multi_request = build_multitext_bbox_request([request])

    try:
        compute_multitext_bbox(multi_request)
    except TextBBoxNotImplementedError as exc:
        message = str(exc)
        assert "NCL MultiText bbox computation is not implemented" in message
        assert "do not replace this with heuristic visual extents" in message
    else:
        raise AssertionError("MultiText bbox must remain guarded until NCL semantics are implemented")

    print("✅ TextItem / MultiText bbox guard smoke passed")


if __name__ == "__main__":
    main()
