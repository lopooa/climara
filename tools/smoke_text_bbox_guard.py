from climara.graphics._plotchar_state import PlotcharUnsupportedError
from climara.graphics._text_bbox import (
    build_multitext_bbox_request,
    build_text_item_bbox_request,
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
        font_quality="High",
    )

    request = build_text_item_bbox_request(semantics, x=0.5, y=0.5)
    assert has_text_bbox_engine() is True

    bbox = compute_text_item_bbox(request)
    assert bbox.width > 0.0
    assert bbox.height > 0.0

    multi_request = build_multitext_bbox_request([request])
    multi_bbox = compute_multitext_bbox(multi_request)
    assert multi_bbox == bbox

    down = build_text_item_semantics(
        "Demo",
        direction="Down",
        func_code="~",
        just="CenterCenter",
        angle=0,
        font=21,
        font_color="black",
        font_height=0.025,
        font_quality="High",
    )
    down_request = build_text_item_bbox_request(down, x=0.5, y=0.5)

    try:
        compute_text_item_bbox(down_request)
    except PlotcharUnsupportedError as exc:
        assert "Down-text" in str(exc)
    else:
        raise AssertionError("Down-text must remain guarded until NCL PLCHHQ logic is mapped")

    print("✅ TextItem / MultiText Python mainline bbox guard smoke passed")


if __name__ == "__main__":
    main()
